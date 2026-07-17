from dataclasses import asdict, dataclass, field, fields, is_dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from uuid import uuid4

from cage_lite.core.decision import CageDecision


RECEIPT_SCHEMA_VERSION = "0.4"

DIGEST_STATUS_VERIFIED = "VERIFIED"
DIGEST_STATUS_MISMATCH = "MISMATCH"
DIGEST_STATUS_NOT_AVAILABLE = "NOT AVAILABLE"
DIGEST_STATUS_LEGACY = "LEGACY"

RECEIPT_DIGEST_METADATA_FIELDS = {
    "_file_name",
}


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


@dataclass(frozen=True)
class ReceiptDigestVerification:
    status: str
    recorded_digest: str | None
    computed_digest: str | None
    schema_version: str | None
    reason: str


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


def verify_receipt_digest(
    warrant: dict[str, object],
) -> ReceiptDigestVerification:
    if not isinstance(warrant, dict):
        return ReceiptDigestVerification(
            status=DIGEST_STATUS_LEGACY,
            recorded_digest=None,
            computed_digest=None,
            schema_version=None,
            reason="Digest verification requires a Warrant JSON object.",
        )

    schema_version = warrant.get("schema_version")
    schema_label = (
        str(schema_version)
        if schema_version is not None
        else None
    )

    if schema_version != RECEIPT_SCHEMA_VERSION:
        if schema_version is None:
            reason = "The Warrant schema version is missing."
        else:
            reason = (
                "Digest verification is not supported for "
                f"schema version {schema_version!r}."
            )

        return ReceiptDigestVerification(
            status=DIGEST_STATUS_LEGACY,
            recorded_digest=None,
            computed_digest=None,
            schema_version=schema_label,
            reason=reason,
        )

    data = {
        key: value
        for key, value in warrant.items()
        if key not in RECEIPT_DIGEST_METADATA_FIELDS
    }

    schema_fields = {
        receipt_field.name
        for receipt_field in fields(CageReceipt)
    }
    required_fields = schema_fields - {"digest"}

    actual_fields = set(data)
    missing_fields = sorted(required_fields - actual_fields)
    extra_fields = sorted(actual_fields - schema_fields)

    shape_issues = []

    if missing_fields:
        shape_issues.append(
            "missing fields: " + ", ".join(missing_fields)
        )

    if extra_fields:
        shape_issues.append(
            "unsupported fields: " + ", ".join(extra_fields)
        )

    if shape_issues:
        return ReceiptDigestVerification(
            status=DIGEST_STATUS_LEGACY,
            recorded_digest=None,
            computed_digest=None,
            schema_version=schema_label,
            reason=(
                "The schema 0.4 Warrant cannot be verified because "
                + "; ".join(shape_issues)
                + "."
            ),
        )

    recorded_digest = data.get("digest")

    if not isinstance(recorded_digest, str):
        return ReceiptDigestVerification(
            status=DIGEST_STATUS_NOT_AVAILABLE,
            recorded_digest=None,
            computed_digest=None,
            schema_version=schema_label,
            reason="The Warrant does not contain a recorded digest.",
        )

    normalized_digest = recorded_digest.strip().lower()

    if not re.fullmatch(r"[0-9a-f]{64}", normalized_digest):
        return ReceiptDigestVerification(
            status=DIGEST_STATUS_NOT_AVAILABLE,
            recorded_digest=recorded_digest,
            computed_digest=None,
            schema_version=schema_label,
            reason=(
                "The recorded digest is not a valid "
                "64-character SHA-256 hexadecimal value."
            ),
        )

    computed_digest = _digest_data(data)

    if normalized_digest == computed_digest:
        return ReceiptDigestVerification(
            status=DIGEST_STATUS_VERIFIED,
            recorded_digest=recorded_digest,
            computed_digest=computed_digest,
            schema_version=schema_label,
            reason=(
                "The recorded digest matches the independently "
                "recomputed schema 0.4 digest."
            ),
        )

    return ReceiptDigestVerification(
        status=DIGEST_STATUS_MISMATCH,
        recorded_digest=recorded_digest,
        computed_digest=computed_digest,
        schema_version=schema_label,
        reason=(
            "The recorded digest does not match the independently "
            "recomputed schema 0.4 digest."
        ),
    )


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
    return _digest_data(receipt.to_dict())


def _digest_data(data: dict[str, object]) -> str:
    canonical_data = dict(data)
    canonical_data["digest"] = None

    payload = json.dumps(
        canonical_data,
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