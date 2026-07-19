from pathlib import Path

from cage_lite.core.action import ActionRequest
from cage_lite.core.boundary import evaluate_prebind
from cage_lite.core.effect import execute_if_admitted
from cage_lite.core.ledger import FileLedger
from cage_lite.core.standing import AgentStanding
from cage_lite.policies.payment import evaluate_payment


def send_payment_to_bank():
    return {
        "status": "sent",
        "payment_id": "pay-001",
    }


if __name__ == "__main__":
    output_dir = Path("playground")
    ledger = FileLedger(output_dir)

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
        receipt_folder=output_dir / "receipts",
    )

    effect_result = execute_if_admitted(
        decision=decision,
        effect=send_payment_to_bank,
        tool_name="vendor_payment_api",
        ledger=ledger,
    )

    print("CAGE decision:")
    print(decision)

    print("\nEffect result:")
    print(effect_result)