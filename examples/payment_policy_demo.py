from cage_lite.core.decision import CageDecision


def evaluate_payment(agent_id: str, amount: float, has_approval: bool) -> CageDecision:
    policy_ref = "policy/payment-threshold-v1"

    if amount > 50000 and not has_approval:
        return CageDecision(
            action_id="payment-001",
            agent_id=agent_id,
            action_type="payment",
            outcome="held",
            reason="Payment exceeds the threshold and cannot bind without approval.",
            policy_ref=policy_ref,
            evidence_ref="evidence/payment-request-001",
            standing_ref="standing/finance-agent-01",
        )

    return CageDecision(
        action_id="payment-001",
        agent_id=agent_id,
        action_type="payment",
        outcome="admitted",
        reason="Payment is within control requirements.",
        policy_ref=policy_ref,
        evidence_ref="evidence/payment-request-001",
        standing_ref="standing/finance-agent-01",
    )


if __name__ == "__main__":
    decision = evaluate_payment(
        agent_id="finance-agent-01",
        amount=75000,
        has_approval=False,
    )

    print(decision)