from pathlib import Path

from cage_lite.core.action import ActionRequest
from cage_lite.core.receipt import create_receipt, write_receipt
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

    decision = evaluate_payment(action, standing)

    receipt = create_receipt(decision)
    decision.receipt_id = receipt.receipt_id

    receipt_path = write_receipt(receipt, Path("playground/receipts"))

    print(decision)
    print(f"Receipt written to {receipt_path}")