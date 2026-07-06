from dataclasses import dataclass
from typing import Literal, Optional


BoundaryOutcome = Literal[
    "admitted",
    "held",
    "narrowed",
    "escalated",
    "refused",
    "quarantined",
    "no-bind",
]


@dataclass
class CageDecision:
    action_id: str
    agent_id: str
    action_type: str
    outcome: BoundaryOutcome
    reason: str
    policy_ref: Optional[str] = None
    evidence_ref: Optional[str] = None
    standing_ref: Optional[str] = None
    receipt_id: Optional[str] = None