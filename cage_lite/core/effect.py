from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Callable
from uuid import uuid4

from cage_lite.core.decision import CageDecision
from cage_lite.core.ledger import FileLedger


@dataclass
class EffectRecord:
    effect_id: str
    action_id: str
    agent_id: str
    action_type: str
    decision_outcome: str
    receipt_id: str | None
    tool_name: str
    attempted: bool
    executed: bool
    disposition: str
    system_of_record_status: str
    reason: str
    created_at: str
    result: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EffectResult:
    action_id: str
    agent_id: str
    action_type: str
    decision_outcome: str
    bound: bool
    reason: str
    receipt_id: str | None = None
    effect_id: str | None = None
    disposition: str | None = None
    system_of_record_status: str | None = None
    result: Any | None = None


def execute_if_admitted(
    decision: CageDecision,
    effect: Callable[[], Any],
    *,
    tool_name: str = "protected_effect",
    ledger: FileLedger | None = None,
) -> EffectResult:
    if decision.outcome != "admitted":
        reason = (
            f"CAGE returned '{decision.outcome}'. "
            "Protected effect was not executed."
        )

        record = _record_effect(
            decision=decision,
            tool_name=tool_name,
            attempted=True,
            executed=False,
            disposition="no_bind",
            system_of_record_status="not_written",
            reason=reason,
            result=None,
        )
        _save_effect(record, ledger)

        return _result_from_record(record, bound=False)

    result = effect()
    reason = "CAGE admitted the action. Protected effect executed."

    record = _record_effect(
        decision=decision,
        tool_name=tool_name,
        attempted=True,
        executed=True,
        disposition="bound",
        system_of_record_status="written",
        reason=reason,
        result=result,
    )
    _save_effect(record, ledger)

    return _result_from_record(record, bound=True)


def execute_narrowed(
    decision: CageDecision,
    effect: Callable[[dict[str, object]], Any],
    *,
    tool_name: str = "protected_effect",
    ledger: FileLedger | None = None,
) -> EffectResult:
    if decision.outcome != "narrowed":
        reason = (
            f"CAGE returned '{decision.outcome}'. "
            "Narrowed effect was not executed."
        )

        record = _record_effect(
            decision=decision,
            tool_name=tool_name,
            attempted=True,
            executed=False,
            disposition="no_bind",
            system_of_record_status="not_written",
            reason=reason,
            result=None,
        )
        _save_effect(record, ledger)

        return _result_from_record(record, bound=False)

    if not decision.allowed_scope:
        reason = "CAGE narrowed the action, but no allowed scope was provided."

        record = _record_effect(
            decision=decision,
            tool_name=tool_name,
            attempted=True,
            executed=False,
            disposition="no_bind",
            system_of_record_status="not_written",
            reason=reason,
            result=None,
        )
        _save_effect(record, ledger)

        return _result_from_record(record, bound=False)

    result = effect(decision.allowed_scope)
    reason = "CAGE narrowed the action. Effect executed within allowed scope."

    record = _record_effect(
        decision=decision,
        tool_name=tool_name,
        attempted=True,
        executed=True,
        disposition="narrowed_bound",
        system_of_record_status="written",
        reason=reason,
        result=result,
    )
    _save_effect(record, ledger)

    return _result_from_record(record, bound=True)


def _record_effect(
    *,
    decision: CageDecision,
    tool_name: str,
    attempted: bool,
    executed: bool,
    disposition: str,
    system_of_record_status: str,
    reason: str,
    result: Any | None,
) -> EffectRecord:
    return EffectRecord(
        effect_id=f"effect-{uuid4().hex[:12]}",
        action_id=decision.action_id,
        agent_id=decision.agent_id,
        action_type=decision.action_type,
        decision_outcome=decision.outcome,
        receipt_id=decision.receipt_id,
        tool_name=tool_name,
        attempted=attempted,
        executed=executed,
        disposition=disposition,
        system_of_record_status=system_of_record_status,
        reason=reason,
        created_at=datetime.now(timezone.utc).isoformat(),
        result=result,
    )


def _result_from_record(record: EffectRecord, *, bound: bool) -> EffectResult:
    return EffectResult(
        action_id=record.action_id,
        agent_id=record.agent_id,
        action_type=record.action_type,
        decision_outcome=record.decision_outcome,
        bound=bound,
        reason=record.reason,
        receipt_id=record.receipt_id,
        effect_id=record.effect_id,
        disposition=record.disposition,
        system_of_record_status=record.system_of_record_status,
        result=record.result,
    )


def _save_effect(record: EffectRecord, ledger: FileLedger | None) -> None:
    if ledger is not None:
        ledger.append_effect(record)