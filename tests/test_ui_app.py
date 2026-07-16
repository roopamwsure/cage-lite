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


def test_overview_with_artifacts_shows_controls(monkeypatch, tmp_path):
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