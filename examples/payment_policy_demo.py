from pathlib import Path

from cage_lite.core.action import ActionRequest
from cage_lite.core.boundary import evaluate_prebind
from cage_lite.core.standing import AgentStanding
from cage_lite.policies.payment import evaluate_payment


if __name__ == "__main__":
    action = ActionRequest(
        action_id="payment-001",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=75000,
        currency="USD",
    )

    standing = AgentStanding(
        agent_id="finance-agent-01",
        allowed_actions={"payment"},
        max_payment_amount=50000,
    )

    decision = evaluate_prebind(
        action=action,
        standing=standing,
        policy=evaluate_payment,
        receipt_folder=Path("playground/receipts"),
    )

    print(decision)