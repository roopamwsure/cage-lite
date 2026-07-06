from dataclasses import dataclass
from typing import Optional


@dataclass
class ActionRequest:
    action_id: str
    agent_id: str
    action_type: str
    amount: Optional[float] = None
    currency: Optional[str] = None
    evidence_ref: Optional[str] = None