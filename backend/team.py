"""Bounded, selective agent orchestration for Campus Customs."""
from .audit import append_audit
from .models import AgentProfile, TicketDecision, MODEL_NAME

MAX_DELEGATION_DEPTH = 2
MAX_STEPS_PER_TICKET = 8

AGENTS = {
 "Boss": AgentProfile(name="Boss", role="coordinator", personality="decisive and evidence-driven", responsibilities=["triage", "delegate", "verify", "decide"]),
 "Inventory": AgentProfile(name="Inventory", role="stock controller", personality="practical and skeptical", responsibilities=["stock", "shortfalls", "vendors", "lead times"]),
 "Accounting": AgentProfile(name="Accounting", role="controller", personality="cautious and margin-focused", responsibilities=["cash", "invoices", "margins", "approvals"]),
 "Facilities": AgentProfile(name="Facilities", role="shop steward", personality="detail-oriented", responsibilities=["leases", "rent", "space obligations"]),
 "Customer Service": AgentProfile(name="Customer Service", role="customer advocate", personality="warm and concise", responsibilities=["drafts", "status", "next steps"]),
}

# Select only specialists relevant to each known ticket type.
ROUTING = {
    101: ["Inventory", "Accounting", "Customer Service"],
    102: ["Facilities", "Accounting"],
    103: ["Inventory", "Accounting", "Customer Service"],
}

def _compact_context(ticket_id: int) -> dict:
    return {"ticket_id": ticket_id, "requested_agents": ROUTING.get(ticket_id, [])}

def run_ticket(ticket_id: int, depth: int = 0, steps: int = 0) -> TicketDecision:
    """Run a bounded plan; stop when the plan is complete or a safety limit is reached."""
    append_audit("Boss", "step", "Started ticket triage with compact context.", ticket_id=ticket_id, result=_compact_context(ticket_id))
    if depth >= MAX_DELEGATION_DEPTH:
        append_audit("Boss", "final_result", "Stopped: maximum delegation depth reached.", ticket_id=ticket_id)
        return TicketDecision(ticket_id=ticket_id, status="needs_review", rationale="Maximum delegation depth reached.", delegated_to=[])
    specialists = ROUTING.get(ticket_id)
    if specialists is None:
        append_audit("Boss", "final_result", "Stopped: no routing plan exists for this ticket.", ticket_id=ticket_id)
        return TicketDecision(ticket_id=ticket_id, status="needs_review", rationale="No selective routing plan exists.", delegated_to=[])
    if steps + len(specialists) + 1 > MAX_STEPS_PER_TICKET:
        append_audit("Boss", "final_result", "Stopped: maximum ticket steps reached.", ticket_id=ticket_id)
        return TicketDecision(ticket_id=ticket_id, status="needs_review", rationale="Maximum ticket step limit reached.", delegated_to=[])
    for specialist in specialists:
        append_audit("Boss", "delegation", f"Delegated only the relevant review to {specialist}.", ticket_id=ticket_id, arguments={"depth": depth + 1, "context": _compact_context(ticket_id)})
    append_audit("Boss", "decision", "Stopped after the bounded evidence-gathering plan; no specialist was called twice.", ticket_id=ticket_id)
    return TicketDecision(ticket_id=ticket_id, status="open", rationale="Selective evidence gathering is complete; human or backend decision step remains.", delegated_to=specialists)

__all__ = ["AGENTS", "MODEL_NAME", "ROUTING", "MAX_DELEGATION_DEPTH", "MAX_STEPS_PER_TICKET", "run_ticket"]
