from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cage_lite.ui import receipt_viewer_v1 as viewer


ArtifactIssue = dict[str, str]


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
    summary, receipts, effects, _ = load_artifacts_with_issues(root)
    return summary, receipts, effects


def load_artifacts_with_issues(
    root: Path,
) -> tuple[
    dict,
    list[dict],
    list[dict],
    list[ArtifactIssue],
]:
    issues: list[ArtifactIssue] = []

    summary = _read_json_object(
        root / "demo_summary.json",
        artifact_type="summary",
        issues=issues,
    )

    receipts = _read_json_folder(
        root / "receipts",
        artifact_type="warrant",
        issues=issues,
    )

    effects = _read_json_folder(
        root / "effects",
        artifact_type="effect",
        issues=issues,
    )

    return summary or {}, receipts, effects, issues


def _read_json_object(
    path: Path,
    artifact_type: str,
    issues: list[ArtifactIssue],
) -> dict | None:
    if not path.exists():
        issues.append(
            _load_issue(
                artifact_type=artifact_type,
                path=path,
                status="missing",
                message="Artifact was not found.",
            )
        )
        return None

    if not path.is_file():
        issues.append(
            _load_issue(
                artifact_type=artifact_type,
                path=path,
                status="read_error",
                message="Expected a JSON file.",
            )
        )
        return None

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        issues.append(
            _load_issue(
                artifact_type=artifact_type,
                path=path,
                status="malformed_json",
                message=(
                    "Malformed JSON at "
                    f"line {exc.lineno}, column {exc.colno}."
                ),
            )
        )
        return None
    except UnicodeError as exc:
        issues.append(
            _load_issue(
                artifact_type=artifact_type,
                path=path,
                status="read_error",
                message=f"Could not decode file as UTF-8: {exc}",
            )
        )
        return None
    except OSError as exc:
        issues.append(
            _load_issue(
                artifact_type=artifact_type,
                path=path,
                status="read_error",
                message=f"Could not read file: {exc}",
            )
        )
        return None

    if not isinstance(data, dict):
        issues.append(
            _load_issue(
                artifact_type=artifact_type,
                path=path,
                status="invalid_type",
                message=(
                    "Expected a JSON object, found "
                    f"{type(data).__name__}."
                ),
            )
        )
        return None

    return data


def _read_json_folder(
    folder: Path,
    artifact_type: str,
    issues: list[ArtifactIssue],
) -> list[dict]:
    if not folder.exists():
        issues.append(
            _load_issue(
                artifact_type=artifact_type,
                path=folder,
                status="missing",
                message="Artifact folder was not found.",
            )
        )
        return []

    if not folder.is_dir():
        issues.append(
            _load_issue(
                artifact_type=artifact_type,
                path=folder,
                status="read_error",
                message="Expected an artifact folder.",
            )
        )
        return []

    try:
        paths = sorted(folder.glob("*.json"))
    except OSError as exc:
        issues.append(
            _load_issue(
                artifact_type=artifact_type,
                path=folder,
                status="read_error",
                message=f"Could not list artifact folder: {exc}",
            )
        )
        return []

    items: list[dict] = []

    for path in paths:
        data = _read_json_object(
            path,
            artifact_type=artifact_type,
            issues=issues,
        )

        if data is None:
            continue

        # Preserve the legacy behaviour that excludes empty artifact files,
        # but report the file instead of silently dropping it.
        if not data:
            issues.append(
                _load_issue(
                    artifact_type=artifact_type,
                    path=path,
                    status="empty_object",
                    message="Artifact contains an empty JSON object.",
                )
            )
            continue

        data["_file_name"] = path.name
        items.append(data)

    return sorted(
        items,
        key=lambda item: (
            str(item.get("created_at", "")),
            str(item.get("attempt_id", "")),
            str(item.get("receipt_id", "")),
        ),
    )


def _load_issue(
    artifact_type: str,
    path: Path,
    status: str,
    message: str,
) -> ArtifactIssue:
    return {
        "artifact_type": artifact_type,
        "file_name": path.name,
        "path": str(path),
        "status": status,
        "message": message,
    }


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
    value = str(receipt.get("created_at") or "").strip()

    if not value:
        return "—"

    try:
        timestamp = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return value

    if timestamp.tzinfo is not None:
        timestamp = timestamp.astimezone(timezone.utc)

    milliseconds = timestamp.microsecond // 1000

    return (
        f"{timestamp:%Y-%m-%d %H:%M:%S}."
        f"{milliseconds:03d} UTC"
    )


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