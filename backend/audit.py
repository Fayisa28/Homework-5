import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from .models import AgentStep

AUDIT_PATH = Path(__file__).resolve().parents[1] / "output" / "audit_trail.json"

def append_audit(agent: str, event: str, summary: str, ticket_id: int | None = None, tool_name: str | None = None, arguments: dict[str, Any] | None = None, result: Any = None) -> AgentStep:
    entry = AgentStep(timestamp_utc=datetime.now(timezone.utc).isoformat(), agent=agent, event=event, summary=summary, ticket_id=ticket_id, tool_name=tool_name, arguments=arguments or {}, result=result)
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = json.loads(AUDIT_PATH.read_text()) if AUDIT_PATH.exists() else []
    if not isinstance(rows, list): rows = []
    rows.append(entry.model_dump())
    AUDIT_PATH.write_text(json.dumps(rows, indent=2))
    return entry
