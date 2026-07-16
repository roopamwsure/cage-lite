from __future__ import annotations

from pathlib import Path

import streamlit as st

from cage_lite.ui import receipt_viewer_v1 as viewer
from cage_lite.ui.app_data import load_artifacts
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


def main() -> None:
    viewer.render_css()
    render_styles()
    viewer.render_header()

    page = render_navigation()
    root = artifact_root()

    summary, receipts, effects = load_artifacts(root)

    render_pending_message()

    if page == "Architecture":
        architecture.render()

    elif not receipts:
        viewer.render_empty(root)

    elif page == "Overview":
        overview.render(
            summary,
            receipts,
            effects,
        )

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

    elif page == "Overview":
        st.divider()
        render_developer_controls()


if __name__ == "__main__":
    main()