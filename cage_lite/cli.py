import argparse
from pathlib import Path

from cage_lite.core.action import ActionRequest
from cage_lite.core.approval import ApprovalRecord
from cage_lite.core.boundary import evaluate_prebind
from cage_lite.core.effect import execute_if_admitted
from cage_lite.core.evidence import EvidenceRecord, write_evidence
from cage_lite.core.standing import AgentStanding
from cage_lite.policies.payment import evaluate_payment
from cage_lite.core.ledger import FileLedger


def send_payment_to_bank():
    return {
        "status": "sent",
        "payment_id": "demo-payment-001",
    }


def run_payment(amount: float, approved: bool, output_dir: Path):
    evidence_dir = output_dir / "evidence"
    receipt_dir = output_dir / "receipts"
    ledger = FileLedger(output_dir)

    payment_evidence = EvidenceRecord.create(
        evidence_type="payment_request",
        subject_id="payment-cli-001",
        summary=f"Finance agent requested a payment of {amount}.",
        source="cli",
        data={
            "amount": amount,
            "currency": "USD",
            "requested_by": "finance-agent-01",
        },
    )
    write_evidence(payment_evidence, evidence_dir)

    action = ActionRequest(
        action_id="payment-cli-001",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=amount,
        currency="USD",
        evidence_ref=payment_evidence.evidence_id,
    )

    standing = AgentStanding(
        agent_id="finance-agent-01",
        allowed_actions={"payment"},
        max_payment_amount=50000,
    )

    approval = None

    if approved:
        approval_evidence = EvidenceRecord.create(
            evidence_type="manager_approval",
            subject_id=action.action_id,
            summary=f"Manager approved the payment of {amount}.",
            source="cli",
            data={
                "approved_by": "manager-01",
                "approved_amount": amount,
            },
        )
        write_evidence(approval_evidence, evidence_dir)

        approval = ApprovalRecord.issue(
            action=action,
            approved_by="manager-01",
            approved_amount=amount,
            evidence_ref=approval_evidence.evidence_id,
        )

    decision = evaluate_prebind(
        action=action,
        standing=standing,
        policy=evaluate_payment,
        receipt_folder=receipt_dir,
        policy_context={
            "approval": approval,
        },
    )

    effect_result = execute_if_admitted(
    decision=decision,
    effect=send_payment_to_bank,
    tool_name="mock_vendor_payment_api",
    ledger=ledger,
    )
    
    return decision, effect_result


def main():
    parser = argparse.ArgumentParser(
        description="Run a CAGE-lite payment boundary demo."
    )

    parser.add_argument(
        "--amount",
        type=float,
        default=75000,
        help="Payment amount to evaluate.",
    )

    parser.add_argument(
        "--approved",
        action="store_true",
        help="Include a manager approval record.",
    )

    parser.add_argument(
        "--output-dir",
        default="playground",
        help="Folder for generated evidence and receipts.",
    )

    args = parser.parse_args()

    decision, effect_result = run_payment(
        amount=args.amount,
        approved=args.approved,
        output_dir=Path(args.output_dir),
    )

    print("CAGE decision")
    print(f"  action_id: {decision.action_id}")
    print(f"  outcome: {decision.outcome}")
    print(f"  reason: {decision.reason}")
    print(f"  receipt_id: {decision.receipt_id}")
    print(f"  evidence_refs: {decision.all_evidence_refs()}")

    print("\nEffect result")
    print(f"  bound: {effect_result.bound}")
    print(f"  reason: {effect_result.reason}")
    print(f"  result: {effect_result.result}")
    print(f" effect_id: {effect_result.effect_id}")
    print(f" disposition: {effect_result.disposition}")
    print(f" system_of_record_status: {effect_result.system_of_record_status}")


if __name__ == "__main__":
    main()