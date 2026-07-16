from __future__ import annotations

import streamlit as st

from cage_lite.ui.app_data import action_label
from cage_lite.ui.app_data import badge
from cage_lite.ui.app_data import boundary_outcome
from cage_lite.ui.app_data import display_status
from cage_lite.ui.app_data import effect_outcome
from cage_lite.ui.app_data import find_effect
from cage_lite.ui.app_data import money
from cage_lite.ui.app_data import short_time
from cage_lite.ui.app_data import sorted_receipts


def open_warrant(receipt_id: str) -> None:
    st.session_state.selected_receipt_id = receipt_id
    st.session_state.cage_page = "Warrants"
    st.rerun()


def render(
    receipts: list[dict],
    effects: list[dict],
) -> None:
    st.markdown(
        '<div class="cage-page-title">Boundary Runs</div>'
        '<div class="cage-page-subtitle">'
        "Chronological history of consequential actions evaluated by CAGE."
        "</div>",
        unsafe_allow_html=True,
    )

    items = sorted_receipts(receipts)

    filters = st.columns([1, 1, 1.4])

    with filters[0]:
        outcomes = ["All"] + sorted(
            {
                display_status(boundary_outcome(item))
                for item in items
            }
        )

        outcome_filter = st.selectbox(
            "Boundary outcome",
            outcomes,
        )

    with filters[1]:
        run_type = st.selectbox(
            "Run type",
            ["All", "Original", "Replay"],
        )

    with filters[2]:
        search = st.text_input(
            "Search",
            placeholder="Agent, action, or Warrant ID",
        ).strip().lower()

    filtered = []

    for item in items:
        if outcome_filter != "All":
            item_outcome = display_status(
                boundary_outcome(item)
            )

            if item_outcome != outcome_filter:
                continue

        is_replay = bool(
            item.get("replay_of_receipt_id")
        )

        if run_type == "Original" and is_replay:
            continue

        if run_type == "Replay" and not is_replay:
            continue

        if search:
            searchable = " ".join(
                [
                    str(item.get("receipt_id") or ""),
                    str(item.get("agent_id") or ""),
                    str(item.get("action_type") or ""),
                    str(item.get("action_summary") or ""),
                ]
            ).lower()

            if search not in searchable:
                continue

        filtered.append(item)

    run_word = "run" if len(filtered) == 1 else "runs"
    st.caption(f"{len(filtered)} {run_word} shown")

    header = st.columns(
        [1.2, 1.2, 1.5, 0.85, 0.85, 0.85, 0.55]
    )

    labels = [
        "Time",
        "Agent",
        "Action",
        "Approval",
        "Boundary",
        "Effect",
        "",
    ]

    for column, label in zip(header, labels):
        with column:
            st.markdown(
                f'<div class="cage-table-header">'
                f"{label}"
                f"</div>",
                unsafe_allow_html=True,
            )

    for item in filtered:
        effect = find_effect(item, effects)

        approval = (
            "present"
            if item.get("approval_present")
            else "missing"
        )

        row = st.columns(
            [1.2, 1.2, 1.5, 0.85, 0.85, 0.85, 0.55],
            vertical_alignment="center",
        )

        with row[0]:
            st.caption(short_time(item))

            if item.get("replay_of_receipt_id"):
                st.caption("Replay")

        with row[1]:
            st.markdown(
                f"**{item.get('agent_id') or '—'}**"
            )

        with row[2]:
            st.markdown(
                f"**{action_label(item)}**"
            )

            st.caption(
                money(
                    item.get("amount"),
                    item.get("currency", "USD"),
                )
            )

        with row[3]:
            st.markdown(
                badge(approval),
                unsafe_allow_html=True,
            )

        with row[4]:
            st.markdown(
                badge(boundary_outcome(item)),
                unsafe_allow_html=True,
            )

        with row[5]:
            st.markdown(
                badge(
                    effect_outcome(item, effect)
                ),
                unsafe_allow_html=True,
            )

        with row[6]:
            if st.button(
                "Open",
                key=f"run_{item.get('receipt_id')}",
                use_container_width=True,
            ):
                open_warrant(
                    str(item.get("receipt_id"))
                )

        st.divider()