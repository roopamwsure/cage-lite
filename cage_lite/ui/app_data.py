from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from cage_lite.ui import receipt_viewer_v1 as viewer


def escape(value: Any) -> str:
    if value is None or value == "":
        return "—"

    return html.escape(str(value))


def display_status(value: Any) -> str:
    text = str(value or "—").strip()
    return text.replace("_", " ").upper()


def money(amount: Any, currency: Any = "USD") -> str:
    return viewer.money(amount, currency)


def yes_no(value: Any) -> str:
    return "YES" if viewer.as_bool(value) else "NO"


def status_tone(value: Any) -> str:
    text = str(value or "").strip().lower()

    if text in {
        "admitted",
        "bound",
        "written",
        "executed",
        "linked",
        "present",
        "yes",
        "verified",
        "changed",
    }:
        return "good"

    if text in {
        "held",
        "no_bind",
        "not_written",
        "not executed",
        "blocked",
        "missing",
        "no",
        "exceeded",
    }:
        return "warn"

    if text in {
        "refused",
        "failed",
        "denied",
        "error",
        "quarantined",
        "not linked",
    }:
        return "bad"

    return "neutral"


def badge(value: Any, tone: str | None = None) -> str:
    css_class = tone or status_tone(value)

    return (
        f'<span class="cage-badge {css_class}">'
        f"{escape(display_status(value))}"
        "</span>"
    )


def load_artifacts(
    root: Path,
) -> tuple[dict, list[dict], list[dict]]:
    return viewer.load_artifacts(root)


def sorted_receipts(receipts: list[dict]) -> list[dict]:
    return sorted(
        receipts,
        key=lambda item: (
            str(item.get("created_at", "")),
            str(item.get("attempt_id", "")),
            str(item.get("receipt_id", "")),
        ),
        reverse=True,
    )


def boundary_outcome(receipt: dict) -> str:
    return str(
        receipt.get("boundary_outcome")
        or receipt.get("outcome")
        or "—"
    )


def find_effect(
    receipt: dict,
    effects: list[dict],
) -> dict:
    return viewer.find_effect(receipt, effects)


def effect_outcome(
    receipt: dict,
    effect: dict,
) -> str:
    return str(
        receipt.get("effect_disposition")
        or effect.get("disposition")
        or effect.get("effect_disposition")
        or "—"
    )


def system_status(
    receipt: dict,
    effect: dict,
) -> str:
    return viewer.system_status(effect, receipt)


def action_label(receipt: dict) -> str:
    summary = receipt.get("action_summary")

    if summary:
        return str(summary).rstrip(".")

    action_type = str(receipt.get("action_type") or "action")
    return action_type.replace("_", " ").title()


def short_time(receipt: dict) -> str:
    value = str(receipt.get("created_at") or "")

    if not value:
        return "—"

    if "T" not in value:
        return value

    date_part, time_part = value.split("T", 1)
    return f"{date_part} {time_part[:8]} UTC"


def latest_replay_pair(
    receipts: list[dict],
) -> tuple[dict, dict]:
    return viewer.latest_demo_pair(receipts)


def receipt_by_id(
    receipts: list[dict],
) -> dict[str, dict]:
    return {
        str(item.get("receipt_id")): item
        for item in receipts
        if item.get("receipt_id")
    }


def replay_children(
    receipt_id: str,
    receipts: list[dict],
) -> list[dict]:
    return [
        item
        for item in receipts
        if str(item.get("replay_of_receipt_id") or "") == receipt_id
    ]