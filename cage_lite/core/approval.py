from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from cage_lite.core.action import ActionRequest


@dataclass
class ApprovalRecord:
    approval_id: str
    action_id: str
    action_type: str
    approved_by: str
    approved_at: str
    approved_amount: float | None = None
    active: bool = True
    evidence_ref: str | None = None

    @classmethod
    def issue(
        cls,
        action: ActionRequest,
        approved_by: str,
        approved_amount: float | None = None,
        evidence_ref: str | None = None,
    ) -> "ApprovalRecord":
        return cls(
            approval_id=f"approval-{uuid4().hex[:12]}",
            action_id=action.action_id,
            action_type=action.action_type,
            approved_by=approved_by,
            approved_at=datetime.now(timezone.utc).isoformat(),
            approved_amount=approved_amount,
            evidence_ref=evidence_ref,
        )

    def covers(self, action: ActionRequest) -> bool:
        if not self.active:
            return False

        if self.action_id != action.action_id:
            return False

        if self.action_type != action.action_type:
            return False

        if self.approved_amount is None:
            return True

        if action.amount is None:
            return False

        return action.amount <= self.approved_amount