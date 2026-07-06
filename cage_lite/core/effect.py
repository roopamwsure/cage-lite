from dataclasses import dataclass
from typing import Any, Callable

from cage_lite.core.decision import CageDecision


@dataclass
class EffectResult:
    action_id: str
    agent_id: str
    action_type: str
    outcome: str
    bound: bool
    reason: str
    receipt_id: str | None = None
    result: Any | None = None


def execute_if_admitted(
    decision: CageDecision,
    effect: Callable[[], Any],
) -> EffectResult:
    if decision.outcome != "admitted":
        return EffectResult(
            action_id=decision.action_id,
            agent_id=decision.agent_id,
            action_type=decision.action_type,
            outcome=decision.outcome,
            bound=False,
            reason=f"Action did not bind because the boundary outcome was '{decision.outcome}'.",
            receipt_id=decision.receipt_id,
        )

    result = effect()

    return EffectResult(
        action_id=decision.action_id,
        agent_id=decision.agent_id,
        action_type=decision.action_type,
        outcome=decision.outcome,
        bound=True,
        reason="Action was admitted and the effect was executed.",
        receipt_id=decision.receipt_id,
        result=result,
    )