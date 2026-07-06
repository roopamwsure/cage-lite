from cage_lite.core.action import ActionRequest
from cage_lite.core.decision import CageDecision


PAYMENT_THRESHOLD = 50000


def evaluate_payment(action: ActionRequest) -> CageDecision:
    policy_ref = "policy/payment-threshold-v1"

    if action.action_type != "payment":
        return CageDecision(
            action_id=action.action_id,
            agent_id=action.agent_id,
            action_type=action.action_type,
            outcome="refused",
            reason="This policy only applies to payment actions.",
            policy_ref=policy_ref,
        )

    if action.amount is None:
        return CageDecision(
            action_id=action.action_id,
            agent_id=action.agent_id,
            action_type=action.action_type,
            outcome="held",
            reason="Payment amount is missing, so the action cannot bind.",
            policy_ref=policy_ref,
        )

    if action.amount > PAYMENT_THRESHOLD and not action.approved_by:
        return CageDecision(
            action_id=action.action_id,
            agent_id=action.agent_id,
            action_type=action.action_type,
            outcome="held",
            reason="Payment exceeds the threshold and requires approval before binding.",
            policy_ref=policy_ref,
            evidence_ref=f"evidence/{action.action_id}",
            standing_ref=f"standing/{action.agent_id}",
        )

    return CageDecision(
        action_id=action.action_id,
        agent_id=action.agent_id,
        action_type=action.action_type,
        outcome="admitted",
        reason="Payment satisfies the policy requirements.",
        policy_ref=policy_ref,
        evidence_ref=f"evidence/{action.action_id}",
        standing_ref=f"standing/{action.agent_id}",
    )