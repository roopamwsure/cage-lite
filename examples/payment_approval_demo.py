from pathlib import Path

from cage_lite.core.action import ActionRequest
from cage_lite.core.approval import ApprovalRecord
from cage_lite.core.boundary import evaluate_prebind
from cage_lite.core.effect import execute_if_admitted
from cage_lite.core.standing import AgentStanding
from cage_lite.policies.payment import evaluate_payment


def send_payment_to_bank():
    return {
        "status": "sent",
        "payment_id": "pay-002",
    }


if __name__ == "__main__":
    action = ActionRequest(
        action_id="payment-002",
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

    approval = ApprovalRecord.issue(
        action=action,
        approved_by="manager-01",
        approved_amount=75000,
        evidence_ref="approval/email-manager-01-payment-002",
    )

    decision = evaluate_prebind(
        action=action,
        standing=standing,
        policy=evaluate_payment,
        receipt_folder=Path("playground/receipts"),
        policy_context={
            "approval": approval,
        },
    )

    effect_result = execute_if_admitted(
        decision=decision,
        effect=send_payment_to_bank,
    )

    print("CAGE decision:")
    print(decision)

    print("\nApproval:")
    print(approval)

    print("\nEffect result:")
    print(effect_result)