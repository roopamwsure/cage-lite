from __future__ import annotations

from cage_lite.ui.views import overview


class DummyColumn:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


def test_boundary_card_tone_matches_decision_status():
    assert overview.boundary_card_tone("ADMITTED") == "good"
    assert overview.boundary_card_tone("allowed") == "good"

    assert overview.boundary_card_tone("HELD") == "warn"
    assert overview.boundary_card_tone("blocked") == "warn"
    assert overview.boundary_card_tone("denied") == "warn"

    assert overview.boundary_card_tone("review") == "blue"


def test_latest_decision_message_for_admitted_warrant(
    monkeypatch,
):
    monkeypatch.setattr(
        overview,
        "money",
        lambda amount, currency: "75,000 USD",
    )

    receipt = {
        "amount": 75000,
        "currency": "USD",
    }

    message = overview.latest_decision_message(
        receipt,
        "ADMITTED",
    )

    assert message == (
        "75,000 USD vendor payment was admitted "
        "at the consequence boundary."
    )


def test_latest_decision_message_for_held_warrant(
    monkeypatch,
):
    monkeypatch.setattr(
        overview,
        "money",
        lambda amount, currency: "75,000 USD",
    )

    receipt = {
        "amount": 75000,
        "currency": "USD",
    }

    message = overview.latest_decision_message(
        receipt,
        "HELD",
    )

    assert message == (
        "75,000 USD vendor payment was held "
        "before binding."
    )


def test_render_uses_newest_warrant_for_latest_summary(
    monkeypatch,
):
    latest = {
        "receipt_id": "receipt-newest",
        "created_at": "2026-07-18T15:23:01.390000+00:00",
        "boundary_outcome": "admitted",
    }

    older = {
        "receipt_id": "receipt-older",
        "created_at": "2026-07-18T15:23:01.387000+00:00",
        "boundary_outcome": "held",
    }

    held = {
        "receipt_id": "receipt-held",
        "boundary_outcome": "held",
    }

    admitted = {
        "receipt_id": "receipt-replay",
        "boundary_outcome": "admitted",
    }

    receipts = [
        older,
        latest,
    ]

    effects = [
        {
            "effect_id": "effect-001",
        }
    ]

    calls = {}

    monkeypatch.setattr(
        overview,
        "page_heading",
        lambda title, subtitle: calls.setdefault(
            "heading",
            (title, subtitle),
        ),
    )

    monkeypatch.setattr(
        overview,
        "sorted_receipts",
        lambda items: [
            latest,
            older,
        ],
    )

    monkeypatch.setattr(
        overview,
        "latest_replay_pair",
        lambda items: (
            held,
            admitted,
        ),
    )

    monkeypatch.setattr(
        overview,
        "render_latest_summary",
        lambda receipt, effect_items: calls.setdefault(
            "latest",
            (receipt, effect_items),
        ),
    )

    monkeypatch.setattr(
        overview,
        "render_original_held_flow",
        lambda receipt, effect_items: calls.setdefault(
            "held_flow",
            (receipt, effect_items),
        ),
    )

    monkeypatch.setattr(
        overview,
        "render_recent_runs",
        lambda receipt_items, effect_items: calls.setdefault(
            "recent",
            (receipt_items, effect_items),
        ),
    )

    monkeypatch.setattr(
        overview,
        "render_latest_replay",
        lambda held_item, admitted_item, effect_items: calls.setdefault(
            "replay",
            (
                held_item,
                admitted_item,
                effect_items,
            ),
        ),
    )

    monkeypatch.setattr(
        overview.st,
        "columns",
        lambda *args, **kwargs: (
            DummyColumn(),
            DummyColumn(),
        ),
    )

    overview.render(
        summary={},
        receipts=receipts,
        effects=effects,
    )

    assert calls["latest"] == (
        latest,
        effects,
    )

    assert calls["held_flow"] == (
        held,
        effects,
    )

    assert calls["recent"] == (
        receipts,
        effects,
    )

    assert calls["replay"] == (
        held,
        admitted,
        effects,
    )


def test_render_handles_empty_warrant_list(
    monkeypatch,
):
    warnings = []

    monkeypatch.setattr(
        overview,
        "page_heading",
        lambda *args: None,
    )

    monkeypatch.setattr(
        overview,
        "sorted_receipts",
        lambda receipts: [],
    )

    monkeypatch.setattr(
        overview.st,
        "warning",
        lambda message: warnings.append(message),
    )

    overview.render(
        summary={},
        receipts=[],
        effects=[],
    )

    assert warnings == [
        "No Warrants were found in the selected artifact folder."
    ]


def test_overview_uses_clean_unicode_characters():
    assert overview.ITEM_SEPARATOR == " · "
    assert overview.EMPTY_VALUE == "—"

    assert "Â" not in overview.ITEM_SEPARATOR
    assert "â" not in overview.EMPTY_VALUE