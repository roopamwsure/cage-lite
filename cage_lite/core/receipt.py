from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from cage_lite.core.decision import CageDecision


@dataclass
class CageReceipt:
    receipt_id: str
    action_id: str
    agent_id: str
    action_type: str
    outcome: str
    reason: str
    prebind: bool
    created_at: str
    policy_ref: str | None = None
    evidence_ref: str | None = None
    evidence_refs: list[str] = field(default_factory=list)
    standing_ref: str | None = None
    allowed_scope: dict[str, object] = field(default_factory=dict)
    digest: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def create_receipt(decision: CageDecision, prebind: bool = True) -> CageReceipt:
    receipt = CageReceipt(
        receipt_id=f"receipt-{uuid4().hex[:12]}",
        action_id=decision.action_id,
        agent_id=decision.agent_id,
        action_type=decision.action_type,
        outcome=decision.outcome,
        reason=decision.reason,
        prebind=prebind,
        created_at=datetime.now(timezone.utc).isoformat(),
        policy_ref=decision.policy_ref,
        evidence_ref=decision.evidence_ref,
        evidence_refs=decision.all_evidence_refs(),
        standing_ref=decision.standing_ref,
        allowed_scope=decision.allowed_scope,
    )

    receipt.digest = _digest(receipt)
    return receipt


def write_receipt(receipt: CageReceipt, folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f"{receipt.receipt_id}.json"
    path.write_text(
        json.dumps(receipt.to_dict(), indent=2),
        encoding="utf-8",
    )

    return path


def _digest(receipt: CageReceipt) -> str:
    data = receipt.to_dict()
    data["digest"] = None

    payload = json.dumps(data, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()