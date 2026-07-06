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
    """
    Run the real-world effect only when CAGE admits the action.

    If the decision is held, refused, escalated, quarantined, narrowed,
    or no-bind, the effect is not executed.
    """

    if decision.outcome != "admitted":
        return EffectResult(
            action_id=decision.action_id,
            agent_id=decision.agent_id,
            action_type=decision.action_type,
            decision_outcome=decision.outcome,
            bound=False,
            reason=(
                "Action did not bind. "
                f"CAGE returned '{decision.outcome}', not 'admitted'."
            ),
            receipt_id=decision.receipt_id,
        )

    effect_result = effect()

    return EffectResult(
        action_id=decision.action_id,
        agent_id=decision.agent_id,
        action_type=decision.action_type,
        decision_outcome=decision.outcome,
        bound=True,
        reason="Action was admitted by CAGE and the effect was executed.",
        receipt_id=decision.receipt_id,
        result=effect_result,
    )