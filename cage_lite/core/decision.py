from dataclasses import dataclass, field
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
    evidence_refs: list[str] = field(default_factory=list)
    standing_ref: Optional[str] = None
    receipt_id: Optional[str] = None

    def all_evidence_refs(self) -> list[str]:
        refs = []

        for ref in [self.evidence_ref, *self.evidence_refs]:
            if ref and ref not in refs:
                refs.append(ref)

        return refs