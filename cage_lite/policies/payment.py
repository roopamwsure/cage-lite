from cage_lite.core.action import ActionRequest
from cage_lite.core.decision import CageDecision
from cage_lite.core.standing import AgentStanding


PAYMENT_LIMIT = 50000


def evaluate_payment(action: ActionRequest, standing: AgentStanding) -> CageDecision:
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

    if standing.agent_id != action.agent_id:
        return CageDecision(
            action_id=action.action_id,
            agent_id=action.agent_id,
            action_type=action.action_type,
            outcome="refused",
            reason="Standing record does not match the acting agent.",
            policy_ref=policy_ref,
        )

    if not standing.can_perform("payment"):
        return CageDecision(
            action_id=action.action_id,
            agent_id=action.agent_id,
            action_type=action.action_type,
            outcome="refused",
            reason="Agent does not have standing to perform payment actions.",
            policy_ref=policy_ref,
            standing_ref=f"standing/{standing.agent_id}",
        )

    if action.amount is None:
        return CageDecision(
            action_id=action.action_id,
            agent_id=action.agent_id,
            action_type=action.action_type,
            outcome="held",
            reason="Payment amount is missing, so the action cannot bind.",
            policy_ref=policy_ref,
            standing_ref=f"standing/{standing.agent_id}",
        )

    limit = standing.max_payment_amount or PAYMENT_LIMIT

    if action.amount > limit and not action.approved_by:
        return CageDecision(
            action_id=action.action_id,
            agent_id=action.agent_id,
            action_type=action.action_type,
            outcome="held",
            reason="Payment exceeds the agent standing limit and requires approval before binding.",
            policy_ref=policy_ref,
            evidence_ref=f"evidence/{action.action_id}",
            standing_ref=f"standing/{standing.agent_id}",
        )

    return CageDecision(
        action_id=action.action_id,
        agent_id=action.agent_id,
        action_type=action.action_type,
        outcome="admitted",
        reason="Payment satisfies standing and policy requirements.",
        policy_ref=policy_ref,
        evidence_ref=f"evidence/{action.action_id}",
        standing_ref=f"standing/{standing.agent_id}",
    )