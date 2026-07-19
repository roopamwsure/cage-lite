from pathlib import Path

from cage_lite.core.action import ActionRequest
from cage_lite.core.boundary import evaluate_prebind
from cage_lite.core.effect import execute_narrowed
from cage_lite.core.ledger import FileLedger
from cage_lite.core.standing import AgentStanding
from cage_lite.policies.payment import evaluate_payment


def send_payment_with_allowed_scope(scope):
    return {
        "status": "sent",
        "payment_id": "pay-narrowed-001",
        "amount": scope["amount"],
        "currency": scope["currency"],
    }


if __name__ == "__main__":
    output_dir = Path("playground")
    ledger = FileLedger(output_dir)

    action = ActionRequest(
        action_id="payment-003",
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
        receipt_folder=output_dir / "receipts",
        policy_context={
            "allow_narrowing": True,
        },
    )

    effect_result = execute_narrowed(
        decision=decision,
        effect=send_payment_with_allowed_scope,
        tool_name="vendor_payment_api",
        ledger=ledger,
    )

    print("CAGE decision:")
    print(decision)

    print("\nRequested amount:")
    print(action.amount)

    print("\nEffect result:")
    print(effect_result)