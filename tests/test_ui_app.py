import pytest

from cage_lite.ui import app
from cage_lite.ui.app_data import short_time


def test_empty_overview_shows_controls(monkeypatch, tmp_path):
    calls = []

    monkeypatch.setattr(
        app,
        "render_overview_empty",
        lambda root: calls.append(("empty", root)),
    )
    monkeypatch.setattr(
        app,
        "render_developer_controls",
        lambda: calls.append(("controls", None)),
    )
    monkeypatch.setattr(
        app.st,
        "divider",
        lambda: calls.append(("divider", None)),
    )
    monkeypatch.setattr(
        app.overview,
        "render",
        lambda *args: calls.append(("overview", None)),
    )

    app.render_page(
        page="Overview",
        root=tmp_path,
        summary={},
        receipts=[],
        effects=[],
    )

    assert calls == [
        ("empty", tmp_path),
        ("divider", None),
        ("controls", None),
    ]


def test_overview_with_artifacts_shows_controls(
    monkeypatch,
    tmp_path,
):
    calls = []
    summary = {"scenario": "payment_replay"}
    receipts = [{"receipt_id": "warrant-001"}]
    effects = [{"receipt_id": "warrant-001"}]

    monkeypatch.setattr(
        app.overview,
        "render",
        lambda summary, receipts, effects: calls.append(
            ("overview", summary, receipts, effects)
        ),
    )
    monkeypatch.setattr(
        app,
        "render_developer_controls",
        lambda: calls.append(("controls",)),
    )
    monkeypatch.setattr(
        app,
        "render_overview_empty",
        lambda root: calls.append(("empty", root)),
    )
    monkeypatch.setattr(
        app.st,
        "divider",
        lambda: calls.append(("divider",)),
    )

    app.render_page(
        page="Overview",
        root=tmp_path,
        summary=summary,
        receipts=receipts,
        effects=effects,
    )

    assert calls == [
        ("overview", summary, receipts, effects),
        ("divider",),
        ("controls",),
    ]


@pytest.mark.parametrize(
    "page",
    [
        "Boundary Runs",
        "Warrants",
        "Replay",
        "Architecture",
    ],
)
def test_other_pages_do_not_show_developer_controls(
    monkeypatch,
    tmp_path,
    page,
):
    calls = []

    monkeypatch.setattr(
        app,
        "render_developer_controls",
        lambda: calls.append("controls"),
    )
    monkeypatch.setattr(
        app.boundary_runs,
        "render",
        lambda *args: calls.append("page"),
    )
    monkeypatch.setattr(
        app.warrants,
        "render",
        lambda *args: calls.append("page"),
    )
    monkeypatch.setattr(
        app.replay,
        "render",
        lambda *args: calls.append("page"),
    )
    monkeypatch.setattr(
        app.architecture,
        "render",
        lambda: calls.append("page"),
    )

    app.render_page(
        page=page,
        root=tmp_path,
        summary={},
        receipts=[],
        effects=[],
    )

    assert calls == ["page"]


def test_short_time_keeps_milliseconds():
    receipt = {
        "created_at": "2026-07-15T21:59:58.831027+00:00"
    }

    assert short_time(receipt) == (
        "2026-07-15 21:59:58.831 UTC"
    )


def test_short_time_distinguishes_runs_in_the_same_second():
    held = {
        "created_at": "2026-07-15T21:59:58.831027+00:00"
    }
    replay = {
        "created_at": "2026-07-15T21:59:58.835974+00:00"
    }

    assert short_time(held) != short_time(replay)


@pytest.mark.parametrize(
    "issues",
    [
        [],
        [
            {
                "artifact_type": "summary",
                "file_name": "demo_summary.json",
                "path": "demo_summary.json",
                "status": "missing",
                "message": "Artifact was not found.",
            }
        ],
    ],
)
def test_artifact_load_messages_ignore_missing_issues(
    monkeypatch,
    issues,
):
    calls = []

    monkeypatch.setattr(
        app.st,
        "warning",
        lambda message: calls.append(("warning", message)),
    )
    monkeypatch.setattr(
        app.st,
        "error",
        lambda message: calls.append(("error", message)),
    )

    app.render_artifact_load_issues(
        summary={},
        receipts=[],
        effects=[],
        issues=issues,
    )

    assert calls == []


def test_partial_artifact_load_shows_warning(monkeypatch):
    calls = []

    monkeypatch.setattr(
        app.st,
        "warning",
        lambda message: calls.append(("warning", message)),
    )
    monkeypatch.setattr(
        app.st,
        "error",
        lambda message: calls.append(("error", message)),
    )

    issues = [
        {
            "artifact_type": "warrant",
            "file_name": "warrant-malformed.json",
            "path": "receipts/warrant-malformed.json",
            "status": "malformed_json",
            "message": "Malformed JSON at line 1, column 34.",
        }
    ]

    app.render_artifact_load_issues(
        summary={"scenario": "payment_replay"},
        receipts=[{"receipt_id": "warrant-valid"}],
        effects=[],
        issues=issues,
    )

    assert len(calls) == 1
    message_type, message = calls[0]

    assert message_type == "warning"
    assert "Valid artifacts are still shown" in message
    assert "warrant-malformed.json" in message
    assert "MALFORMED JSON" in message
    assert "line 1, column 34" in message


def test_failed_artifact_load_shows_error(monkeypatch):
    calls = []

    monkeypatch.setattr(
        app.st,
        "warning",
        lambda message: calls.append(("warning", message)),
    )
    monkeypatch.setattr(
        app.st,
        "error",
        lambda message: calls.append(("error", message)),
    )

    issues = [
        {
            "artifact_type": "warrant",
            "file_name": "warrant-malformed.json",
            "path": "receipts/warrant-malformed.json",
            "status": "malformed_json",
            "message": "Malformed JSON at line 1, column 34.",
        }
    ]

    app.render_artifact_load_issues(
        summary={},
        receipts=[],
        effects=[],
        issues=issues,
    )

    assert len(calls) == 1
    message_type, message = calls[0]

    assert message_type == "error"
    assert "No usable artifacts were loaded" in message
    assert "warrant-malformed.json" in message
    assert "MALFORMED JSON" in message


def test_main_reports_artifact_issues_before_rendering_page(
    monkeypatch,
    tmp_path,
):
    calls = []

    summary = {"scenario": "payment_replay"}
    receipts = [{"receipt_id": "warrant-valid"}]
    effects = []
    issues = [
        {
            "artifact_type": "warrant",
            "file_name": "warrant-malformed.json",
            "path": "receipts/warrant-malformed.json",
            "status": "malformed_json",
            "message": "Malformed JSON at line 1, column 34.",
        }
    ]

    monkeypatch.setattr(
        app.viewer,
        "render_css",
        lambda: None,
    )
    monkeypatch.setattr(
        app,
        "render_styles",
        lambda: None,
    )
    monkeypatch.setattr(
        app.viewer,
        "render_header",
        lambda: None,
    )
    monkeypatch.setattr(
        app,
        "render_navigation",
        lambda: "Overview",
    )
    monkeypatch.setattr(
        app,
        "artifact_root",
        lambda: tmp_path,
    )
    monkeypatch.setattr(
        app,
        "load_artifacts_with_issues",
        lambda root: (
            summary,
            receipts,
            effects,
            issues,
        ),
    )
    monkeypatch.setattr(
        app,
        "render_pending_message",
        lambda: calls.append(("pending",)),
    )
    monkeypatch.setattr(
        app,
        "render_artifact_load_issues",
        lambda loaded_summary,
        loaded_receipts,
        loaded_effects,
        loaded_issues: calls.append(
            (
                "issues",
                loaded_summary,
                loaded_receipts,
                loaded_effects,
                loaded_issues,
            )
        ),
    )
    monkeypatch.setattr(
        app,
        "render_page",
        lambda page,
        root,
        loaded_summary,
        loaded_receipts,
        loaded_effects: calls.append(
            (
                "page",
                page,
                root,
                loaded_summary,
                loaded_receipts,
                loaded_effects,
            )
        ),
    )

    app.main()

    assert calls == [
        ("pending",),
        (
            "issues",
            summary,
            receipts,
            effects,
            issues,
        ),
        (
            "page",
            "Overview",
            tmp_path,
            summary,
            receipts,
            effects,
        ),
    ]