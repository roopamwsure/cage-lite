from cage_lite.demo.payment_replay import run_replay_demo


def test_payment_replay_demo_links_held_and_admitted_receipts(tmp_path):
    summary = run_replay_demo(tmp_path)

    held = summary["held"]
    replay = summary["replay"]

    assert summary["scenario"] == "75000_vendor_payment_replay"
    assert summary["amount"] == 75000
    assert summary["currency"] == "USD"
    assert summary["standing_limit"] == 50000
    assert summary["approval_required_above"] == 50000

    assert held["boundary_outcome"] == "held"
    assert held["effect_disposition"] == "no_bind"
    assert held["effect_executed"] is False
    assert held["system_of_record_status"] == "not_written"
    assert held["approval_required"] is True
    assert held["approval_present"] is False

    assert replay["boundary_outcome"] == "admitted"
    assert replay["effect_disposition"] == "bound"
    assert replay["effect_executed"] is True
    assert replay["system_of_record_status"] == "written"
    assert replay["approval_required"] is True
    assert replay["approval_present"] is True

    assert replay["replay_of_receipt_id"] == held["receipt_id"]
    assert summary["held_receipt_id"] == held["receipt_id"]
    assert summary["replay_receipt_id"] == replay["receipt_id"]

    summary_file = tmp_path / "demo_summary.json"
    assert summary_file.exists()