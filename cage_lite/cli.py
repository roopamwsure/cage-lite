import argparse
from pathlib import Path

from cage_lite.core.action import ActionRequest
from cage_lite.core.approval import ApprovalRecord
from cage_lite.core.boundary import evaluate_prebind
from cage_lite.core.effect import execute_if_admitted
from cage_lite.core.evidence import EvidenceRecord, write_evidence
from cage_lite.core.ledger import FileLedger
from cage_lite.core.receipt import create_receipt, write_receipt
from cage_lite.core.standing import AgentStanding
from cage_lite.policies.payment import evaluate_payment


def send_payment_to_bank():
    return {
        "status": "sent",
        "payment_id": "demo-payment-001",
    }


def run_payment(
    amount: float,
    approved: bool,
    output_dir: Path,
    replay_of_receipt_id: str | None = None,
):
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
        policy_context={
            "approval": approval,
        },
    )

    effect_result = execute_if_admitted(
        decision=decision,
        effect=send_payment_to_bank,
        ledger=ledger,
    )

    receipt = create_receipt(
        decision=decision,
        action=action,
        standing=standing,
        approval=approval,
        effect_result=effect_result,
        movement_id="movement-vendor-payment-001",
        replay_of_receipt_id=replay_of_receipt_id,
        actor_id="finance-ops-user-01",
        delegation_chain=[
            "finance-ops-user-01",
            action.agent_id,
        ],
        action_summary=f"Finance agent requested a {amount:g} USD vendor payment.",
        policy_version="v1",
    )

    decision.receipt_id = receipt.receipt_id
    write_receipt(receipt, receipt_dir)

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
        "--replay-of-receipt-id",
        default=None,
        help="Warrant ID for the earlier held attempt.",
    )
    parser.add_argument(
        "--output-dir",
        default="playground",
        help="Folder for generated evidence, receipts, and effects.",
    )

    args = parser.parse_args()

    decision, effect_result = run_payment(
        amount=args.amount,
        approved=args.approved,
        output_dir=Path(args.output_dir),
        replay_of_receipt_id=args.replay_of_receipt_id,
    )

    record = (
        getattr(effect_result, "effect_record", None)
        or getattr(effect_result, "record", None)
    )

    effect_id = getattr(record, "effect_id", None) or getattr(
        effect_result,
        "effect_id",
        None,
    )
    disposition = getattr(record, "disposition", None) or getattr(
        effect_result,
        "disposition",
        None,
    )
    system_status = getattr(record, "system_of_record_status", None) or getattr(
        effect_result,
        "system_of_record_status",
        None,
    )

    print("CAGE decision")
    print(f" action_id: {decision.action_id}")
    print(f" outcome: {decision.outcome}")
    print(f" reason: {decision.reason}")
    print(f" receipt_id: {decision.receipt_id}")
    print(f" evidence_refs: {decision.all_evidence_refs()}")

    print("\nEffect result")
    print(f" effect_id: {effect_id}")
    print(f" disposition: {disposition}")
    print(f" system_of_record_status: {system_status}")
    print(f" bound: {effect_result.bound}")
    print(f" reason: {effect_result.reason}")
    print(f" result: {effect_result.result}")


if __name__ == "__main__":
    main()