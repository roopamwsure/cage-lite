from pathlib import Path

from cage_lite.core.action import ActionRequest
from cage_lite.core.boundary import evaluate_prebind
from cage_lite.core.effect import execute_if_admitted
from cage_lite.core.standing import AgentStanding
from cage_lite.policies.payment import evaluate_payment


def send_narrowed_payment():
    return {
        "status": "sent",
        "payment_id": "pay-narrowed-001",
        "amount": 50000,
        "currency": "USD",
    }


if __name__ == "__main__":
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
        receipt_folder=Path("playground/receipts"),
        policy_context={
            "allow_narrowing": True,
        },
    )

    if decision.outcome == "narrowed":
        print("CAGE narrowed the action.")
        print(f"Original amount: {action.amount}")
        print(f"Allowed amount: {decision.allowed_scope['amount']}")

    effect_result = execute_if_admitted(
        decision=decision,
        effect=send_narrowed_payment,
    )

    print("\nCAGE decision:")
    print(decision)

    print("\nEffect result:")
    print(effect_result)