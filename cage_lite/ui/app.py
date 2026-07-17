from __future__ import annotations

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
        label = artifact_type.replace("_", " ").title()

        file_name = str(
            issue.get("file_name") or "unknown file"
        )
        status = str(
            issue.get("status") or "error"
        ).replace("_", " ").upper()
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

def render_overview_empty(root: Path) -> None:
    overview.page_heading(
        "Overview",
        "Current boundary decision, effect proof, "
        "recent runs, and replay status.",
    )

    st.info(
        "No CAGE Warrants were found in the selected artifact folder."
    )

    st.write(
        "Use Developer controls below to generate the replay demo, "
        "or select a folder containing existing CAGE-lite artifacts."
    )

    st.caption(f"Current artifact folder: {root}")


def render_page(
    page: str,
    root: Path,
    summary: dict,
    receipts: list[dict],
    effects: list[dict],
) -> None:
    if page == "Overview":
        if receipts:
            overview.render(
                summary,
                receipts,
                effects,
            )
        else:
            render_overview_empty(root)

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
        st.error(f"Unknown application page: {page}")


def main() -> None:
    viewer.render_css()
    render_styles()
    viewer.render_header()

    page = render_navigation()
    root = artifact_root()

    summary, receipts, effects, issues = (
        load_artifacts_with_issues(root)
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