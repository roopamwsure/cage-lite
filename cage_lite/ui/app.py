from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from cage_lite.ui import receipt_viewer_v1 as viewer
from cage_lite.ui.app_data import load_artifacts_with_issues
from cage_lite.ui.app_styles import render_styles
from cage_lite.ui.views import architecture
from cage_lite.ui.views import boundary_runs
from cage_lite.ui.views import overview
from cage_lite.ui.views import replay
from cage_lite.ui.views import warrants


PAGES = [
    "Overview",
    "Boundary Runs",
    "Warrants",
    "Replay",
    "Architecture",
]

DEVELOPER_CONTROLS_ENV = "CAGE_LITE_SHOW_DEV_CONTROLS"
TRUE_ENV_VALUES = {
    "1",
    "true",
    "yes",
    "on",
}

EXPECTED_MISSING_ARTIFACTS = {
    ("summary", "demo_summary.json"),
    ("warrant", "receipts"),
    ("effect", "effects"),
}


def developer_controls_enabled() -> bool:
    value = os.getenv(
        DEVELOPER_CONTROLS_ENV,
        "",
    )

    return value.strip().lower() in TRUE_ENV_VALUES


def render_navigation() -> str:
    if "cage_page" not in st.session_state:
        st.session_state.cage_page = "Overview"

    columns = st.columns(len(PAGES))

    for column, page in zip(columns, PAGES):
        with column:
            is_active = st.session_state.cage_page == page

            if st.button(
                page,
                key=f"nav_{page.lower().replace(' ', '_')}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.session_state.cage_page = page
                st.rerun()

    return st.session_state.cage_page


def artifact_root() -> Path:
    if "artifact_dir" not in st.session_state:
        st.session_state.artifact_dir = viewer.DEFAULT_ARTIFACT_DIR

    value = str(st.session_state.artifact_dir)
    value = value.strip().strip('"')

    return Path(value)



def generate_replay_demo(output_dir: Path) -> dict:
    from cage_lite.demo.payment_replay import run_replay_demo

    return run_replay_demo(output_dir)


def should_bootstrap_demo(
    summary: dict,
    receipts: list[dict],
    effects: list[dict],
    issues: list[dict[str, str]],
) -> bool:
    """Return True only when the complete artifact set is absent."""

    if summary or receipts or effects:
        return False

    if len(issues) != len(EXPECTED_MISSING_ARTIFACTS):
        return False

    if any(issue.get("status") != "missing" for issue in issues):
        return False

    missing_artifacts = {
        (
            str(issue.get("artifact_type") or ""),
            str(issue.get("file_name") or ""),
        )
        for issue in issues
    }

    return missing_artifacts == EXPECTED_MISSING_ARTIFACTS


def load_artifacts_for_app(
    root: Path,
) -> tuple[
    dict,
    list[dict],
    list[dict],
    list[dict[str, str]],
]:
    summary, receipts, effects, issues = (
        load_artifacts_with_issues(root)
    )

    if not should_bootstrap_demo(
        summary,
        receipts,
        effects,
        issues,
    ):
        return summary, receipts, effects, issues

    try:
        generate_replay_demo(root)
    except Exception as exc:
        summary, receipts, effects, issues = (
            load_artifacts_with_issues(root)
        )

        issues.append(
            {
                "artifact_type": "demo_generation",
                "file_name": root.name or str(root),
                "path": str(root),
                "status": "generation_failed",
                "message": (
                    "Could not generate the default replay demo: "
                    f"{exc}"
                ),
            }
        )

        return summary, receipts, effects, issues

    return load_artifacts_with_issues(root)

def render_developer_controls() -> None:
    with st.expander("Developer controls"):
        st.caption(
            "Generate or load local demo artifacts. "
            "These controls are kept outside the main product experience."
        )

        left, right = st.columns(
            [4, 1.2],
            vertical_alignment="bottom",
        )

        with left:
            st.text_input(
                "Artifact folder",
                key="artifact_dir",
            )

        with right:
            generate = st.button(
                "Generate replay demo",
                key="generate_replay_demo",
                use_container_width=True,
            )

        if not generate:
            return

        try:
            from cage_lite.demo.payment_replay import run_replay_demo

            output_dir = artifact_root()
            result = run_replay_demo(output_dir)

            held_id = result.get("held_receipt_id")
            replay_id = result.get("replay_receipt_id")

            st.session_state.demo_notice = (
                "Replay generated successfully: "
                f"{held_id} → {replay_id}"
            )

            # Return to Overview so the new records are immediately visible.
            st.session_state.cage_page = "Overview"
            st.rerun()

        except Exception as exc:
            st.session_state.demo_error = str(exc)
            st.rerun()


def render_pending_message() -> None:
    notice = st.session_state.pop(
        "demo_notice",
        None,
    )

    if notice:
        st.success(notice)

    error = st.session_state.pop(
        "demo_error",
        None,
    )

    if error:
        st.error(
            f"Could not generate replay demo: {error}"
        )


def render_artifact_load_issues(
    summary: dict,
    receipts: list[dict],
    effects: list[dict],
    issues: list[dict[str, str]],
) -> None:
    failures = [
        issue
        for issue in issues
        if issue.get("status") != "missing"
    ]

    if not failures:
        return

    details = []

    for issue in failures:
        artifact_type = str(
            issue.get("artifact_type") or "artifact"
        )

        label = artifact_type.replace(
            "_",
            " ",
        ).title()

        file_name = str(
            issue.get("file_name") or "unknown file"
        )

        status = str(
            issue.get("status") or "error"
        ).replace(
            "_",
            " ",
        ).upper()

        message = str(
            issue.get("message")
            or "The artifact could not be loaded."
        )

        details.append(
            f"- **{label}:** `{file_name}` "
            f"[{status}] - {message}"
        )

    usable_artifacts_loaded = bool(
        summary or receipts or effects
    )

    if usable_artifacts_loaded:
        heading = (
            "Some artifacts could not be loaded. "
            "Valid artifacts are still shown."
        )

        st.warning(
            heading + "\n\n" + "\n".join(details)
        )
        return

    heading = (
        "Artifact loading failed. "
        "No usable artifacts were loaded."
    )

    st.error(
        heading + "\n\n" + "\n".join(details)
    )


def render_overview_empty(
    root: Path,
    show_developer_controls: bool,
) -> None:
    overview.page_heading(
        "Overview",
        (
            "Latest boundary decision, original held flow, "
            "recent runs, and replay status."
        ),
    )

    st.info(
        "No CAGE Warrants are available."
    )

    if show_developer_controls:
        st.write(
            "Use Developer controls below to generate the replay demo, "
            "or select a folder containing existing CAGE-lite artifacts."
        )

        st.caption(
            f"Current artifact folder: {root}"
        )
        return

    st.write(
        "No artifact set has been loaded for this deployment."
    )


def render_page(
    page: str,
    root: Path,
    summary: dict,
    receipts: list[dict],
    effects: list[dict],
) -> None:
    show_developer_controls = developer_controls_enabled()

    if page == "Overview":
        if receipts:
            overview.render(
                summary,
                receipts,
                effects,
            )
        else:
            render_overview_empty(
                root,
                show_developer_controls,
            )

        if show_developer_controls:
            st.divider()
            render_developer_controls()

    elif page == "Boundary Runs":
        boundary_runs.render(
            receipts,
            effects,
        )

    elif page == "Warrants":
        warrants.render(
            receipts,
            effects,
        )

    elif page == "Replay":
        replay.render(
            receipts,
            effects,
        )

    elif page == "Architecture":
        architecture.render()

    else:
        st.error(
            f"Unknown application page: {page}"
        )


def main() -> None:
    viewer.render_css()
    render_styles()
    viewer.render_header()

    page = render_navigation()
    root = artifact_root()

    summary, receipts, effects, issues = (
        load_artifacts_for_app(root)
    )

    render_pending_message()

    render_artifact_load_issues(
        summary,
        receipts,
        effects,
        issues,
    )

    render_page(
        page,
        root,
        summary,
        receipts,
        effects,
    )


if __name__ == "__main__":
    main()