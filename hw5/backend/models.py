from typing import Any, Literal
from pydantic import BaseModel, Field

MODEL_NAME = "gpt-6-luna"

class AgentStep(BaseModel):
    timestamp_utc: str
    agent: str
    event: Literal["step", "delegation", "tool_call", "decision", "approval_request", "final_result"]
    summary: str
    tool_name: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    result: Any | None = None
    ticket_id: int | None = None

class TicketDecision(BaseModel):
    ticket_id: int
    status: str
    rationale: str
    delegated_to: list[str] = Field(default_factory=list)
    approval_required: bool = False

class AgentProfile(BaseModel):
    name: str
    role: str
    personality: str
    responsibilities: list[str]
