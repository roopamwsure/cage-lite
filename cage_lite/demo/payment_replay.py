import json
from pathlib import Path

from cage_lite.cli import run_payment
from cage_lite.core.ledger import FileLedger


def run_replay_demo(output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)

    held_decision, held_effect = run_payment(
        amount=75000,
        approved=False,
        output_dir=output_dir,
    )

    replay_decision, replay_effect = run_payment(
        amount=75000,
        approved=True,
        output_dir=output_dir,
        replay_of_receipt_id=held_decision.receipt_id,
    )

    ledger = FileLedger(output_dir)

    held_receipt = ledger.get_receipt(held_decision.receipt_id)
    replay_receipt = ledger.get_receipt(replay_decision.receipt_id)

    summary = {
        "scenario": "75000_vendor_payment_replay",
        "amount": 75000,
        "currency": "USD",
        "agent_id": "finance-agent-01",
        "standing_limit": 50000,
        "approval_required_above": 50000,
        "held_receipt_id": held_decision.receipt_id,
        "replay_receipt_id": replay_decision.receipt_id,
        "held": _receipt_summary(held_receipt),
        "replay": _receipt_summary(replay_receipt),
    }

    summary_path = output_dir / "demo_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return summary


def _receipt_summary(receipt: dict) -> dict:
    return {
        "receipt_id": receipt["receipt_id"],
        "action_id": receipt["action_id"],
        "movement_id": receipt["movement_id"],
        "replay_of_receipt_id": receipt["replay_of_receipt_id"],
        "boundary_outcome": receipt["boundary_outcome"],
        "boundary_reason": receipt["boundary_reason"],
        "effect_id": receipt["effect_id"],
        "effect_disposition": receipt["effect_disposition"],
        "effect_executed": receipt["effect_executed"],
        "system_of_record_status": receipt["system_of_record_status"],
        "approval_required": receipt["approval_required"],
        "approval_present": receipt["approval_present"],
        "digest": receipt["digest"],
    }


def main():
    output_dir = Path("playground/v04-replay-demo")
    summary = run_replay_demo(output_dir)

    print("CAGE-lite v0.4 replay demo")
    print(f" output_dir: {output_dir}")
    print(f" held_receipt_id: {summary['held_receipt_id']}")
    print(f" replay_receipt_id: {summary['replay_receipt_id']}")

    print("\nHeld attempt")
    print(f" boundary_outcome: {summary['held']['boundary_outcome']}")
    print(f" effect_disposition: {summary['held']['effect_disposition']}")
    print(f" system_of_record_status: {summary['held']['system_of_record_status']}")

    print("\nReplay with approval")
    print(f" boundary_outcome: {summary['replay']['boundary_outcome']}")
    print(f" effect_disposition: {summary['replay']['effect_disposition']}")
    print(f" system_of_record_status: {summary['replay']['system_of_record_status']}")
    print(f" replay_of_receipt_id: {summary['replay']['replay_of_receipt_id']}")


if __name__ == "__main__":
    main()