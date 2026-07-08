from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from cage_lite.core.decision import CageDecision


RECEIPT_SCHEMA_VERSION = "0.4"


@dataclass
class CageReceipt:
    schema_version: str = RECEIPT_SCHEMA_VERSION

    receipt_id: str = ""
    action_id: str = ""
    movement_id: str | None = None
    attempt_id: str | None = None
    replay_of_receipt_id: str | None = None

    agent_id: str = ""
    actor_id: str | None = None
    delegation_chain: list[str] = field(default_factory=list)

    action_type: str = ""
    action_summary: str | None = None
    action_payload_hash: str | None = None
    amount: float | None = None
    currency: str | None = None

    standing_ref: str | None = None
    standing_limit: float | None = None

    policy_ref: str | None = None
    policy_version: str | None = None

    approval_required: bool = False
    approval_present: bool = False
    approval_ref: str | None = None

    boundary_outcome: str = ""
    boundary_reason: str = ""

    effect_id: str | None = None
    effect_disposition: str | None = None
    effect_attempted: bool = False
    effect_executed: bool = False
    system_of_record_status: str | None = None

    evidence_refs: list[str] = field(default_factory=list)

    created_at: str = ""
    digest: str | None = None

    # Backward-compatible fields used by older tests and demos.
    outcome: str | None = None
    reason: str | None = None
    prebind: bool = True
    evidence_ref: str | None = None
    allowed_scope: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def create_receipt(
    decision: CageDecision,
    prebind: bool = True,
    *,
    action: object | None = None,
    standing: object | None = None,
    approval: object | None = None,
    effect_result: object | None = None,
    receipt_id: str | None = None,
    movement_id: str | None = None,
    attempt_id: str | None = None,
    replay_of_receipt_id: str | None = None,
    actor_id: str | None = None,
    delegation_chain: list[str] | None = None,
    action_summary: str | None = None,
    policy_version: str | None = None,
) -> CageReceipt:
    action_id = _get(action, "action_id", decision.action_id)
    agent_id = _get(action, "agent_id", decision.agent_id)
    action_type = _get(action, "action_type", decision.action_type)
    amount = _get(action, "amount")
    currency = _get(action, "currency")

    standing_limit = _get(standing, "max_payment_amount")
    approval_ref = _get(approval, "approval_id")

    approval_present = approval is not None
    if approval is not None and action is not None and hasattr(approval, "covers"):
        approval_present = approval.covers(action)

    approval_required = _approval_required(
        amount=amount,
        standing_limit=standing_limit,
        decision=decision,
    )

    refs = _unique_refs(
        decision.all_evidence_refs(),
        [_get(approval, "evidence_ref")],
    )

    effect = _effect_fields(effect_result)

    receipt = CageReceipt(
        schema_version=RECEIPT_SCHEMA_VERSION,
        receipt_id=receipt_id or decision.receipt_id or f"receipt-{uuid4().hex[:12]}",
        action_id=action_id,
        movement_id=movement_id or action_id,
        attempt_id=attempt_id or f"attempt-{uuid4().hex[:12]}",
        replay_of_receipt_id=replay_of_receipt_id,
        agent_id=agent_id,
        actor_id=actor_id or agent_id,
        delegation_chain=delegation_chain or [agent_id],
        action_type=action_type,
        action_summary=action_summary or _default_action_summary(
            action_type=action_type,
            amount=amount,
            currency=currency,
        ),
        action_payload_hash=_payload_hash(action),
        amount=amount,
        currency=currency,
        standing_ref=decision.standing_ref,
        standing_limit=standing_limit,
        policy_ref=decision.policy_ref,
        policy_version=policy_version or _policy_version(decision.policy_ref),
        approval_required=approval_required,
        approval_present=approval_present,
        approval_ref=approval_ref,
        boundary_outcome=decision.outcome,
        boundary_reason=decision.reason,
        effect_id=effect["effect_id"],
        effect_disposition=effect["effect_disposition"],
        effect_attempted=effect["effect_attempted"],
        effect_executed=effect["effect_executed"],
        system_of_record_status=effect["system_of_record_status"],
        evidence_refs=refs,
        created_at=datetime.now(timezone.utc).isoformat(),
        outcome=decision.outcome,
        reason=decision.reason,
        prebind=prebind,
        evidence_ref=decision.evidence_ref,
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


def _approval_required(
    amount: float | None,
    standing_limit: float | None,
    decision: CageDecision,
) -> bool:
    if amount is not None and standing_limit is not None:
        return amount > standing_limit

    reason = decision.reason.lower()
    return decision.outcome == "held" and "approval" in reason


def _effect_fields(effect_result: object | None) -> dict:
    if effect_result is None:
        return {
            "effect_id": None,
            "effect_disposition": None,
            "effect_attempted": False,
            "effect_executed": False,
            "system_of_record_status": None,
        }

    record = _get(effect_result, "effect_record") or _get(effect_result, "record")

    effect_id = _get(record, "effect_id") or _get(effect_result, "effect_id")
    disposition = (
        _get(record, "disposition")
        or _get(effect_result, "disposition")
    )

    executed = _get(record, "executed")
    if executed is None:
        executed = _get(effect_result, "executed")
    if executed is None:
        bound = _get(effect_result, "bound")
        executed = bool(bound)

    if disposition is None:
        disposition = "bound" if executed else "no_bind"

    system_status = (
        _get(record, "system_of_record_status")
        or _get(effect_result, "system_of_record_status")
    )
    if system_status is None:
        system_status = "written" if executed else "not_written"

    return {
        "effect_id": effect_id,
        "effect_disposition": disposition,
        "effect_attempted": True,
        "effect_executed": bool(executed),
        "system_of_record_status": system_status,
    }


def _default_action_summary(
    action_type: str,
    amount: float | None,
    currency: str | None,
) -> str:
    if action_type == "payment" and amount is not None:
        if currency:
            return f"Payment request for {amount:g} {currency}."
        return f"Payment request for {amount:g}."

    return f"{action_type} action requested."


def _policy_version(policy_ref: str | None) -> str | None:
    if not policy_ref:
        return None

    last_part = policy_ref.rsplit("-", 1)[-1]
    if last_part.startswith("v"):
        return last_part

    return None


def _payload_hash(value: object | None) -> str | None:
    if value is None:
        return None

    payload = json.dumps(
        _plain_data(value),
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _digest(receipt: CageReceipt) -> str:
    data = receipt.to_dict()
    data["digest"] = None

    payload = json.dumps(
        data,
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _plain_data(value: object) -> object:
    if is_dataclass(value):
        return asdict(value)

    if isinstance(value, dict):
        return value

    if hasattr(value, "__dict__"):
        return {
            key: val
            for key, val in vars(value).items()
            if not key.startswith("_")
        }

    return str(value)


def _get(value: object | None, name: str, default=None):
    if value is None:
        return default

    if isinstance(value, dict):
        return value.get(name, default)

    return getattr(value, name, default)


def _unique_refs(*groups: list[str | None]) -> list[str]:
    refs = []

    for group in groups:
        for ref in group:
            if ref and ref not in refs:
                refs.append(ref)

    return refs