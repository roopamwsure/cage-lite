from dataclasses import dataclass
from typing import Any, Callable

from cage_lite.core.decision import CageDecision


@dataclass
class EffectResult:
    action_id: str
    agent_id: str
    action_type: str
    decision_outcome: str
    bound: bool
    reason: str
    receipt_id: str | None = None
    result: Any | None = None


def execute_if_admitted(
    decision: CageDecision,
    effect: Callable[[], Any],
) -> EffectResult:
    if decision.outcome != "admitted":
        return _blocked(
            decision,
            f"Action did not bind. CAGE returned '{decision.outcome}', not 'admitted'.",
        )

    effect_result = effect()

    return EffectResult(
        action_id=decision.action_id,
        agent_id=decision.agent_id,
        action_type=decision.action_type,
        decision_outcome=decision.outcome,
        bound=True,
        reason="Action was admitted by CAGE and the full effect was executed.",
        receipt_id=decision.receipt_id,
        result=effect_result,
    )


def execute_narrowed(
    decision: CageDecision,
    effect: Callable[[dict[str, object]], Any],
) -> EffectResult:
    if decision.outcome != "narrowed":
        return _blocked(
            decision,
            f"Narrowed effect did not run. CAGE returned '{decision.outcome}', not 'narrowed'.",
        )

    if not decision.allowed_scope:
        return _blocked(
            decision,
            "Narrowed effect did not run because no allowed scope was provided.",
        )

    effect_result = effect(decision.allowed_scope)

    return EffectResult(
        action_id=decision.action_id,
        agent_id=decision.agent_id,
        action_type=decision.action_type,
        decision_outcome=decision.outcome,
        bound=True,
        reason="Original action did not bind. Narrowed effect executed within the allowed scope.",
        receipt_id=decision.receipt_id,
        result=effect_result,
    )


def _blocked(decision: CageDecision, reason: str) -> EffectResult:
    return EffectResult(
        action_id=decision.action_id,
        agent_id=decision.agent_id,
        action_type=decision.action_type,
        decision_outcome=decision.outcome,
        bound=False,
        reason=reason,
        receipt_id=decision.receipt_id,
    )