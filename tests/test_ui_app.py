import pytest

from cage_lite.ui import app
from cage_lite.ui.app_data import short_time


def test_developer_controls_are_disabled_by_default(
    monkeypatch,
):
    monkeypatch.delenv(
        app.DEVELOPER_CONTROLS_ENV,
        raising=False,
    )

    assert app.developer_controls_enabled() is False


@pytest.mark.parametrize(
    "value",
    [
        "1",
        "true",
        "TRUE",
        "yes",
        "on",
        " On ",
    ],
)
def test_developer_controls_accept_truthy_environment_values(
    monkeypatch,
    value,
):
    monkeypatch.setenv(
        app.DEVELOPER_CONTROLS_ENV,
        value,
    )

    assert app.developer_controls_enabled() is True


@pytest.mark.parametrize(
    "value",
    [
        "",
        "0",
        "false",
        "no",
        "off",
        "random",
    ],
)
def test_developer_controls_reject_non_truthy_values(
    monkeypatch,
    value,
):
    monkeypatch.setenv(
        app.DEVELOPER_CONTROLS_ENV,
        value,
    )

    assert app.developer_controls_enabled() is False


def test_empty_overview_hides_controls_by_default(
    monkeypatch,
    tmp_path,
):
    calls = []

    monkeypatch.setattr(
        app,
        "developer_controls_enabled",
        lambda: False,
    )
    monkeypatch.setattr(
        app,
        "render_overview_empty",
        lambda root, show_controls: calls.append(
            (
                "empty",
                root,
                show_controls,
            )
        ),
    )
    monkeypatch.setattr(
        app,
        "render_developer_controls",
        lambda: calls.append(("controls",)),
    )
    monkeypatch.setattr(
        app.st,
        "divider",
        lambda: calls.append(("divider",)),
    )
    monkeypatch.setattr(
        app.overview,
        "render",
        lambda *args: calls.append(("overview",)),
    )

    app.render_page(
        page="Overview",
        root=tmp_path,
        summary={},
        receipts=[],
        effects=[],
    )

    assert calls == [
        (
            "empty",
            tmp_path,
            False,
        ),
    ]


def test_overview_with_artifacts_hides_controls_by_default(
    monkeypatch,
    tmp_path,
):
    calls = []

    summary = {
        "scenario": "payment_replay",
    }
    receipts = [
        {
            "receipt_id": "warrant-001",
        }
    ]
    effects = [
        {
            "receipt_id": "warrant-001",
        }
    ]

    monkeypatch.setattr(
        app,
        "developer_controls_enabled",
        lambda: False,
    )
    monkeypatch.setattr(
        app.overview,
        "render",
        lambda summary, receipts, effects: calls.append(
            (
                "overview",
                summary,
                receipts,
                effects,
            )
        ),
    )
    monkeypatch.setattr(
        app,
        "render_developer_controls",
        lambda: calls.append(("controls",)),
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
        (
            "overview",
            summary,
            receipts,
            effects,
        ),
    ]


def test_empty_overview_shows_controls_in_developer_mode(
    monkeypatch,
    tmp_path,
):
    calls = []

    monkeypatch.setattr(
        app,
        "developer_controls_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        app,
        "render_overview_empty",
        lambda root, show_controls: calls.append(
            (
                "empty",
                root,
                show_controls,
            )
        ),
    )
    monkeypatch.setattr(
        app,
        "render_developer_controls",
        lambda: calls.append(("controls",)),
    )
    monkeypatch.setattr(
        app.st,
        "divider",
        lambda: calls.append(("divider",)),
    )

    app.render_page(
        page="Overview",
        root=tmp_path,
        summary={},
        receipts=[],
        effects=[],
    )

    assert calls == [
        (
            "empty",
            tmp_path,
            True,
        ),
        ("divider",),
        ("controls",),
    ]


def test_overview_with_artifacts_shows_controls_in_developer_mode(
    monkeypatch,
    tmp_path,
):
    calls = []

    summary = {
        "scenario": "payment_replay",
    }
    receipts = [
        {
            "receipt_id": "warrant-001",
        }
    ]
    effects = [
        {
            "receipt_id": "warrant-001",
        }
    ]

    monkeypatch.setattr(
        app,
        "developer_controls_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        app.overview,
        "render",
        lambda summary, receipts, effects: calls.append(
            (
                "overview",
                summary,
                receipts,
                effects,
            )
        ),
    )
    monkeypatch.setattr(
        app,
        "render_developer_controls",
        lambda: calls.append(("controls",)),
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
        (
            "overview",
            summary,
            receipts,
            effects,
        ),
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

    # Even when developer mode is enabled, controls belong only
    # on the Overview page.
    monkeypatch.setattr(
        app,
        "developer_controls_enabled",
        lambda: True,
    )
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


def test_empty_overview_uses_product_message_by_default(
    monkeypatch,
    tmp_path,
):
    calls = []

    monkeypatch.setattr(
        app.overview,
        "page_heading",
        lambda title, subtitle: calls.append(
            (
                "heading",
                title,
                subtitle,
            )
        ),
    )
    monkeypatch.setattr(
        app.st,
        "info",
        lambda message: calls.append(
            (
                "info",
                message,
            )
        ),
    )
    monkeypatch.setattr(
        app.st,
        "write",
        lambda message: calls.append(
            (
                "write",
                message,
            )
        ),
    )
    monkeypatch.setattr(
        app.st,
        "caption",
        lambda message: calls.append(
            (
                "caption",
                message,
            )
        ),
    )

    app.render_overview_empty(
        tmp_path,
        show_developer_controls=False,
    )

    assert (
        "info",
        "No CAGE Warrants are available.",
    ) in calls

    assert (
        "write",
        "No artifact set has been loaded for this deployment.",
    ) in calls

    assert not any(
        call[0] == "caption"
        for call in calls
    )

    assert not any(
        "Developer controls" in str(call)
        for call in calls
    )


def test_empty_overview_explains_developer_controls_when_enabled(
    monkeypatch,
    tmp_path,
):
    messages = []

    monkeypatch.setattr(
        app.overview,
        "page_heading",
        lambda *args: None,
    )
    monkeypatch.setattr(
        app.st,
        "info",
        lambda message: messages.append(message),
    )
    monkeypatch.setattr(
        app.st,
        "write",
        lambda message: messages.append(message),
    )
    monkeypatch.setattr(
        app.st,
        "caption",
        lambda message: messages.append(message),
    )

    app.render_overview_empty(
        tmp_path,
        show_developer_controls=True,
    )

    assert any(
        "Use Developer controls below" in message
        for message in messages
    )

    assert any(
        str(tmp_path) in message
        for message in messages
    )


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

    summary = {
        "scenario": "payment_replay",
    }
    receipts = [
        {
            "receipt_id": "warrant-valid",
        }
    ]
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

def _missing_artifact_issues(root):
    return [
        {
            "artifact_type": "summary",
            "file_name": "demo_summary.json",
            "path": str(root / "demo_summary.json"),
            "status": "missing",
            "message": "Artifact was not found.",
        },
        {
            "artifact_type": "warrant",
            "file_name": "receipts",
            "path": str(root / "receipts"),
            "status": "missing",
            "message": "Artifact folder was not found.",
        },
        {
            "artifact_type": "effect",
            "file_name": "effects",
            "path": str(root / "effects"),
            "status": "missing",
            "message": "Artifact folder was not found.",
        },
    ]


def test_missing_artifacts_generate_demo_and_reload(
    monkeypatch,
    tmp_path,
):
    generated_artifacts = (
        {
            "scenario": "75000_vendor_payment_replay",
        },
        [
            {
                "receipt_id": "warrant-held",
            },
            {
                "receipt_id": "warrant-replay",
            },
        ],
        [
            {
                "effect_id": "effect-held",
            },
            {
                "effect_id": "effect-replay",
            },
        ],
        [],
    )

    load_results = iter(
        [
            (
                {},
                [],
                [],
                _missing_artifact_issues(tmp_path),
            ),
            generated_artifacts,
        ]
    )

    calls = []

    def fake_load(root):
        calls.append(("load", root))
        return next(load_results)

    def fake_generate(root):
        calls.append(("generate", root))

    monkeypatch.setattr(
        app,
        "load_artifacts_with_issues",
        fake_load,
    )
    monkeypatch.setattr(
        app,
        "generate_replay_demo",
        fake_generate,
    )

    result = app.load_artifacts_for_app(tmp_path)

    assert result == generated_artifacts
    assert calls == [
        ("load", tmp_path),
        ("generate", tmp_path),
        ("load", tmp_path),
    ]


def test_existing_artifacts_are_not_overwritten(
    monkeypatch,
    tmp_path,
):
    existing_artifacts = (
        {
            "scenario": "payment_replay",
        },
        [
            {
                "receipt_id": "warrant-existing",
            },
        ],
        [
            {
                "effect_id": "effect-existing",
            },
        ],
        [],
    )

    monkeypatch.setattr(
        app,
        "load_artifacts_with_issues",
        lambda root: existing_artifacts,
    )
    monkeypatch.setattr(
        app,
        "generate_replay_demo",
        lambda root: pytest.fail(
            "Existing artifacts must not be regenerated."
        ),
    )

    result = app.load_artifacts_for_app(tmp_path)

    assert result == existing_artifacts


def test_partial_artifact_set_is_not_replaced(
    monkeypatch,
    tmp_path,
):
    missing_issues = _missing_artifact_issues(tmp_path)

    partial_artifacts = (
        {},
        [],
        [],
        [
            missing_issues[0],
            missing_issues[2],
        ],
    )

    monkeypatch.setattr(
        app,
        "load_artifacts_with_issues",
        lambda root: partial_artifacts,
    )
    monkeypatch.setattr(
        app,
        "generate_replay_demo",
        lambda root: pytest.fail(
            "Partial artifact sets must not be replaced."
        ),
    )

    result = app.load_artifacts_for_app(tmp_path)

    assert result == partial_artifacts


def test_malformed_artifact_set_is_not_replaced(
    monkeypatch,
    tmp_path,
):
    malformed_artifacts = (
        {},
        [],
        [],
        [
            {
                "artifact_type": "summary",
                "file_name": "demo_summary.json",
                "path": str(tmp_path / "demo_summary.json"),
                "status": "malformed_json",
                "message": "Malformed JSON at line 1, column 8.",
            },
        ],
    )

    monkeypatch.setattr(
        app,
        "load_artifacts_with_issues",
        lambda root: malformed_artifacts,
    )
    monkeypatch.setattr(
        app,
        "generate_replay_demo",
        lambda root: pytest.fail(
            "Malformed artifacts must not be replaced."
        ),
    )

    result = app.load_artifacts_for_app(tmp_path)

    assert result == malformed_artifacts


def test_demo_generation_failure_uses_issue_reporting(
    monkeypatch,
    tmp_path,
):
    load_count = 0

    def fake_load(root):
        nonlocal load_count
        load_count += 1

        return (
            {},
            [],
            [],
            _missing_artifact_issues(root),
        )

    def fail_generation(root):
        raise OSError("Deployment filesystem is read-only.")

    monkeypatch.setattr(
        app,
        "load_artifacts_with_issues",
        fake_load,
    )
    monkeypatch.setattr(
        app,
        "generate_replay_demo",
        fail_generation,
    )

    summary, receipts, effects, issues = (
        app.load_artifacts_for_app(tmp_path)
    )

    assert load_count == 2

    generation_issues = [
        issue
        for issue in issues
        if issue.get("status") == "generation_failed"
    ]

    assert len(generation_issues) == 1
    assert generation_issues[0]["artifact_type"] == (
        "demo_generation"
    )
    assert generation_issues[0]["path"] == str(tmp_path)
    assert "read-only" in generation_issues[0]["message"]

    messages = []

    monkeypatch.setattr(
        app.st,
        "warning",
        lambda message: messages.append(
            ("warning", message)
        ),
    )
    monkeypatch.setattr(
        app.st,
        "error",
        lambda message: messages.append(
            ("error", message)
        ),
    )

    app.render_artifact_load_issues(
        summary,
        receipts,
        effects,
        issues,
    )

    assert len(messages) == 1
    assert messages[0][0] == "error"
    assert "GENERATION FAILED" in messages[0][1]
    assert "read-only" in messages[0][1]
