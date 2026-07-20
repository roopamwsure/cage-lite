from pathlib import Path

from cage_lite.core.action import ActionRequest
from cage_lite.core.approval import ApprovalRecord
from cage_lite.core.boundary import evaluate_prebind
from cage_lite.core.effect import execute_if_admitted
from cage_lite.core.evidence import EvidenceRecord, write_evidence
from cage_lite.core.ledger import FileLedger
from cage_lite.core.standing import AgentStanding
from cage_lite.policies.payment import evaluate_payment


def send_payment_to_bank():
    return {
        "status": "sent",
        "payment_id": "pay-002",
    }


if __name__ == "__main__":
    output_dir = Path("playground")
    evidence_folder = output_dir / "evidence"
    ledger = FileLedger(output_dir)

    payment_evidence = EvidenceRecord.create(
        evidence_type="payment_request",
        subject_id="payment-002",
        summary="Finance agent requested a 75,000 USD payment.",
        source="demo",
        data={
            "amount": 75000,
            "currency": "USD",
            "requested_by": "finance-agent-01",
        },
    )
    write_evidence(payment_evidence, evidence_folder)

    action = ActionRequest(
        action_id="payment-002",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=75000,
        currency="USD",
        evidence_ref=payment_evidence.evidence_id,
    )

    standing = AgentStanding(
        agent_id="finance-agent-01",
        allowed_actions={"payment"},
        max_payment_amount=50000,
    )

    approval_evidence = EvidenceRecord.create(
        evidence_type="manager_approval",
        subject_id=action.action_id,
        summary="Manager approved the 75,000 USD payment.",
        source="demo",
        data={
            "approved_by": "manager-01",
            "approved_amount": 75000,
        },
    )
    write_evidence(approval_evidence, evidence_folder)

    approval = ApprovalRecord.issue(
        action=action,
        approved_by="manager-01",
        approved_amount=75000,
        evidence_ref=approval_evidence.evidence_id,
    )

    decision = evaluate_prebind(
        action=action,
        standing=standing,
        policy=evaluate_payment,
        receipt_folder=output_dir / "receipts",
        policy_context={
            "approval": approval,
        },
    )

    effect_result = execute_if_admitted(
        decision=decision,
        effect=send_payment_to_bank,
        tool_name="vendor_payment_api",
        ledger=ledger,
    )

    print("CAGE decision:")
    print(decision)

    print("\nApproval:")
    print(approval)

    print("\nEffect result:")
    print(effect_result)