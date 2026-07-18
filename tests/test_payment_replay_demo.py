from pathlib import Path

from cage_lite.demo import payment_replay
from cage_lite.demo.payment_replay import run_replay_demo


def test_payment_replay_demo_links_held_and_admitted_receipts(
    tmp_path,
):
    summary = run_replay_demo(tmp_path)

    held = summary["held"]
    replay = summary["replay"]

    assert (
        summary["scenario"]
        == "75000_vendor_payment_replay"
    )
    assert summary["amount"] == 75000
    assert summary["currency"] == "USD"
    assert summary["standing_limit"] == 50000
    assert (
        summary["approval_required_above"]
        == 50000
    )

    assert held["boundary_outcome"] == "held"
    assert (
        held["effect_disposition"]
        == "no_bind"
    )
    assert held["effect_executed"] is False
    assert (
        held["system_of_record_status"]
        == "not_written"
    )
    assert held["approval_required"] is True
    assert held["approval_present"] is False

    assert (
        replay["boundary_outcome"]
        == "admitted"
    )
    assert (
        replay["effect_disposition"]
        == "bound"
    )
    assert replay["effect_executed"] is True
    assert (
        replay["system_of_record_status"]
        == "written"
    )
    assert replay["approval_required"] is True
    assert replay["approval_present"] is True

    assert (
        replay["replay_of_receipt_id"]
        == held["receipt_id"]
    )
    assert (
        summary["held_receipt_id"]
        == held["receipt_id"]
    )
    assert (
        summary["replay_receipt_id"]
        == replay["receipt_id"]
    )

    summary_file = (
        tmp_path
        / "demo_summary.json"
    )

    assert summary_file.exists()


def test_demo_console_output_uses_warrant_language(
    capsys,
):
    summary = {
        "held_receipt_id": "warrant-held-001",
        "replay_receipt_id": "warrant-replay-001",
        "held": {
            "boundary_outcome": "held",
            "effect_disposition": "no_bind",
            "effect_executed": False,
            "system_of_record_status": "not_written",
        },
        "replay": {
            "boundary_outcome": "admitted",
            "effect_disposition": "bound",
            "effect_executed": True,
            "system_of_record_status": "written",
            "replay_of_receipt_id": "warrant-held-001",
        },
    }

    payment_replay._print_demo_summary(
        summary,
        Path("playground/demo"),
    )

    output = capsys.readouterr().out

    assert "CAGE-lite v1 product preview" in output
    assert (
        "Held Warrant ID: warrant-held-001"
        in output
    )
    assert (
        "Replay Warrant ID: warrant-replay-001"
        in output
    )
    assert (
        "Original Warrant ID: warrant-held-001"
        in output
    )

    assert "Boundary outcome: HELD" in output
    assert "Effect disposition: NO BIND" in output
    assert "Effect executed: No" in output
    assert "System of record: NOT WRITTEN" in output

    assert "Boundary outcome: ADMITTED" in output
    assert "Effect disposition: BOUND" in output
    assert "Effect executed: Yes" in output
    assert "System of record: WRITTEN" in output

    assert "held_receipt_id:" not in output
    assert "replay_receipt_id:" not in output
    assert (
        "CAGE-lite v0.4 replay demo"
        not in output
    )