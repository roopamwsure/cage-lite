import json

from cage_lite.ui.app_data import load_artifacts
from cage_lite.ui.app_data import load_artifacts_with_issues


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value),
        encoding="utf-8",
    )


def create_empty_artifact_folders(root):
    (root / "receipts").mkdir()
    (root / "effects").mkdir()


def test_load_artifacts_keeps_existing_three_value_contract(tmp_path):
    write_json(
        tmp_path / "demo_summary.json",
        {"scenario": "payment_replay"},
    )
    write_json(
        tmp_path / "receipts" / "warrant-001.json",
        {
            "receipt_id": "warrant-001",
            "created_at": "2026-07-15T21:59:58.831027+00:00",
        },
    )
    write_json(
        tmp_path / "effects" / "effect-001.json",
        {
            "effect_id": "effect-001",
            "created_at": "2026-07-15T21:59:58.832027+00:00",
        },
    )

    summary, receipts, effects = load_artifacts(tmp_path)

    assert summary == {"scenario": "payment_replay"}
    assert receipts[0]["receipt_id"] == "warrant-001"
    assert receipts[0]["_file_name"] == "warrant-001.json"
    assert effects[0]["effect_id"] == "effect-001"
    assert effects[0]["_file_name"] == "effect-001.json"


def test_malformed_warrant_does_not_block_valid_warrant(tmp_path):
    write_json(
        tmp_path / "demo_summary.json",
        {"scenario": "payment_replay"},
    )
    write_json(
        tmp_path / "receipts" / "warrant-valid.json",
        {
            "receipt_id": "warrant-valid",
            "created_at": "2026-07-15T21:59:58.831027+00:00",
        },
    )

    malformed_path = (
        tmp_path
        / "receipts"
        / "warrant-malformed.json"
    )
    malformed_path.write_text(
        '{"receipt_id": "warrant-malformed"',
        encoding="utf-8",
    )

    (tmp_path / "effects").mkdir()

    summary, receipts, effects, issues = (
        load_artifacts_with_issues(tmp_path)
    )

    assert summary == {"scenario": "payment_replay"}
    assert effects == []

    assert [item["receipt_id"] for item in receipts] == [
        "warrant-valid"
    ]

    assert len(issues) == 1
    assert issues[0]["artifact_type"] == "warrant"
    assert issues[0]["file_name"] == "warrant-malformed.json"
    assert issues[0]["status"] == "malformed_json"
    assert "line 1" in issues[0]["message"]


def test_wrong_top_level_json_type_is_reported(tmp_path):
    write_json(
        tmp_path / "demo_summary.json",
        ["not", "an", "object"],
    )
    create_empty_artifact_folders(tmp_path)

    summary, receipts, effects, issues = (
        load_artifacts_with_issues(tmp_path)
    )

    assert summary == {}
    assert receipts == []
    assert effects == []

    assert len(issues) == 1
    assert issues[0]["artifact_type"] == "summary"
    assert issues[0]["file_name"] == "demo_summary.json"
    assert issues[0]["status"] == "invalid_type"
    assert "list" in issues[0]["message"]


def test_missing_artifact_locations_are_distinct_from_malformed(tmp_path):
    summary, receipts, effects, issues = (
        load_artifacts_with_issues(tmp_path)
    )

    assert summary == {}
    assert receipts == []
    assert effects == []

    assert {
        (
            issue["artifact_type"],
            issue["status"],
            issue["file_name"],
        )
        for issue in issues
    } == {
        ("summary", "missing", "demo_summary.json"),
        ("warrant", "missing", "receipts"),
        ("effect", "missing", "effects"),
    }


def test_empty_warrant_object_is_reported(tmp_path):
    write_json(
        tmp_path / "demo_summary.json",
        {"scenario": "payment_replay"},
    )
    write_json(
        tmp_path / "receipts" / "warrant-empty.json",
        {},
    )
    (tmp_path / "effects").mkdir()

    _, receipts, _, issues = load_artifacts_with_issues(tmp_path)

    assert receipts == []
    assert len(issues) == 1
    assert issues[0]["artifact_type"] == "warrant"
    assert issues[0]["file_name"] == "warrant-empty.json"
    assert issues[0]["status"] == "empty_object"