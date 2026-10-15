from __future__ import annotations
import json, shutil, sqlite3, hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
except ImportError:  # Allows schema review before dependencies are installed.
    FastAPI = None
    class BaseModel:
        def __init__(self, **kwargs): self.__dict__.update(kwargs)
        def model_dump(self): return dict(self.__dict__)
    def Field(default=None, **kwargs): return default

from .team import run_ticket
from .audit import append_audit, AUDIT_PATH

ROOT = Path(__file__).resolve().parents[1]
WORKING_DB = ROOT / "data" / "campus_customs_new.db"
ORIGINAL_DB = ROOT / "data" / "campus_customs.db"

class ApprovalRequest(BaseModel):
    ticket_id: int
    kind: str = Field(pattern="^(payment|purchase)$")
    amount: float = Field(gt=0)
    description: str

class ApprovalDecision(BaseModel):
    approval_id: str
    approved_by: str

class TicketStatusUpdate(BaseModel):
    status: str = Field(pattern="^(open|resolved|needs_review)$")
    actor: str


def db_query(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with sqlite3.connect(WORKING_DB) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def db_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    rows = db_query(sql, params)
    return rows[0] if rows else None


def ticket_or_404(ticket_id: int) -> dict[str, Any]:
    row = db_one("SELECT * FROM tickets WHERE id=?", (ticket_id,))
    if not row: raise HTTPException(404, "Ticket not found")
    return row


def audit_rows() -> list[dict[str, Any]]:
    if not AUDIT_PATH.exists(): return []
    try: return json.loads(AUDIT_PATH.read_text())
    except json.JSONDecodeError: return []

if FastAPI is not None:
    app = FastAPI(title="Campus Customs Operations API", version="1.0")
    app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    @app.get("/health")
    def health(): return {"ok": True, "database": str(WORKING_DB)}

    @app.get("/tickets")
    def list_tickets(): return {"tickets": db_query("SELECT id,type,requester,subject,status FROM tickets WHERE id IN (101,102,103) ORDER BY id")}

    @app.get("/tickets/{ticket_id}")
    def get_ticket(ticket_id: int): return {"ticket": ticket_or_404(ticket_id)}

    @app.post("/tickets/{ticket_id}/status")
    def update_ticket_status(ticket_id: int, update: TicketStatusUpdate):
        ticket_or_404(ticket_id)
        with sqlite3.connect(WORKING_DB) as conn:
            conn.execute("UPDATE tickets SET status=? WHERE id=?", (update.status, ticket_id))
            conn.commit()
        append_audit(update.actor, "decision", "Ticket status updated through the explicit status route.", ticket_id=ticket_id, arguments=update.model_dump(), result={"status": update.status})
        return {"ticket": ticket_or_404(ticket_id)}

    @app.post("/tickets/{ticket_id}/run")
    def start_ticket(ticket_id: int):
        ticket_or_404(ticket_id)
        decision = run_ticket(ticket_id)
        return {"ticket": ticket_or_404(ticket_id), "decision": decision.model_dump()}

    @app.get("/events")
    def recent_events(limit: int = 50):
        if limit < 1 or limit > 200: raise HTTPException(400, "limit must be between 1 and 200")
        return {"events": audit_rows()[-limit:]}

    @app.post("/approvals")
    def create_approval(req: ApprovalRequest):
        ticket_or_404(req.ticket_id)
        approval_id = f"approval-{req.ticket_id}-{int(datetime.now(timezone.utc).timestamp()*1000)}"
        append_audit("Boss", "approval_request", req.description, ticket_id=req.ticket_id, arguments=req.model_dump(), result={"approval_id": approval_id, "status": "pending"})
        return {"approval_id": approval_id, "status": "pending", "request": req.model_dump(), "message": "Human approval required; no payment was made."}

    @app.post("/approvals/{approval_id}/approve")
    def approve(approval_id: str, decision: ApprovalDecision):
        events = [e for e in audit_rows() if e.get("event")=="approval_request" and e.get("result",{}).get("approval_id")==approval_id]
        if not events: raise HTTPException(404, "Approval request not found")
        req = events[-1]["arguments"]; cash = db_one("SELECT * FROM cash_accounts WHERE name='checking'")
        if not cash: raise HTTPException(500, "Checking account not found")
        if cash["balance"] < req["amount"]: raise HTTPException(409, "Payment refused: insufficient checking cash")
        now = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(WORKING_DB) as conn:
            conn.execute("BEGIN IMMEDIATE")
            current = conn.execute("SELECT balance FROM cash_accounts WHERE name='checking'").fetchone()
            if current is None or current[0] < req["amount"]:
                conn.rollback()
                raise HTTPException(409, "Payment refused: insufficient checking cash")
            new_balance = current[0] - req["amount"]
            conn.execute("UPDATE cash_accounts SET balance=?, date=? WHERE name='checking' AND balance>=?", (new_balance, now[:10], req["amount"]))
            if conn.total_changes != 1:
                conn.rollback()
                raise HTTPException(409, "Payment refused: checking balance changed")
            conn.execute("INSERT INTO payments(kind,ref_id,amount,account,paid_at,approved_by) VALUES(?,?,?,?,?,?)", (req["kind"], req["ticket_id"], req["amount"], "checking", now, decision.approved_by))
            conn.commit()
        append_audit("Accounting", "decision", "Human-approved payment recorded and cash updated.", ticket_id=req["ticket_id"], arguments={"approval_id": approval_id, "approved_by": decision.approved_by}, result={"amount": req["amount"]})
        return {"approval_id": approval_id, "status": "approved", "approved_by": decision.approved_by, "cash_account": db_one("SELECT * FROM cash_accounts WHERE name='checking'")}

    @app.get("/cash")
    def cash(): return {"cash_accounts": db_query("SELECT * FROM cash_accounts")}

    @app.post("/reset")
    def reset_database():
        if not ORIGINAL_DB.exists(): raise HTTPException(500, "Original database not found")
        original_hash = hashlib.sha256(ORIGINAL_DB.read_bytes()).hexdigest()
        temp = WORKING_DB.with_suffix(".reset.tmp")
        shutil.copy2(ORIGINAL_DB, temp)
        shutil.move(temp, WORKING_DB)
        if hashlib.sha256(ORIGINAL_DB.read_bytes()).hexdigest() != original_hash:
            raise HTTPException(500, "Reset aborted: original database changed")
        append_audit("Boss", "decision", "Working database reset from untouched original.")
        return {"status": "reset", "database": str(WORKING_DB), "original_preserved": True}
else:
    app = None
