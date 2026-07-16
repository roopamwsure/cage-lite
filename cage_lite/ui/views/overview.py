from __future__ import annotations

import streamlit as st

from cage_lite.ui.app_data import action_label
from cage_lite.ui.app_data import badge
from cage_lite.ui.app_data import boundary_outcome
from cage_lite.ui.app_data import display_status
from cage_lite.ui.app_data import effect_outcome
from cage_lite.ui.app_data import escape
from cage_lite.ui.app_data import find_effect
from cage_lite.ui.app_data import latest_replay_pair
from cage_lite.ui.app_data import money
from cage_lite.ui.app_data import short_time
from cage_lite.ui.app_data import sorted_receipts
from cage_lite.ui.app_data import system_status


def page_heading(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="cage-page-title">{escape(title)}</div>'
        f'<div class="cage-page-subtitle">{escape(subtitle)}</div>',
        unsafe_allow_html=True,
    )


def flow_card(
    label: str,
    value: str,
    detail: str,
    tone: str = "",
) -> str:
    css_class = f" {tone}" if tone else ""

    return (
        f'<div class="cage-flow-card{css_class}">'
        f'<div class="cage-flow-label">{escape(label)}</div>'
        f'<div class="cage-flow-value">{escape(value)}</div>'
        f'<div class="cage-flow-detail">{escape(detail)}</div>'
        "</div>"
    )


def open_warrant(receipt_id: str) -> None:
    st.session_state.selected_receipt_id = receipt_id
    st.session_state.cage_page = "Warrants"
    st.rerun()


def render(
    summary: dict,
    receipts: list[dict],
    effects: list[dict],
) -> None:
    page_heading(
        "Overview",
        "Current boundary decision, effect proof, recent runs, and replay status.",
    )

    held, admitted = latest_replay_pair(receipts)

    if not held:
        st.warning(
            "No HELD Warrant was found in the selected artifact folder."
        )
        return

    held_effect = find_effect(held, effects)

    if admitted:
        admitted_effect = find_effect(admitted, effects)
    else:
        admitted_effect = {}

    outcome = boundary_outcome(held)
    effect = effect_outcome(held, held_effect)
    system = system_status(held, held_effect)

    amount = money(
        held.get("amount"),
        held.get("currency", "USD"),
    )

    standing_limit = money(
        held.get("standing_limit"),
        held.get("currency", "USD"),
    )

    left, right = st.columns(
        [1.35, 0.65],
        gap="medium",
    )

    with left:
        st.markdown(
            '<div class="cage-card warn">'
            '<div class="cage-kicker">Latest boundary decision</div>'
            '<div class="cage-card-title" '
            'style="font-size:1.45rem;">'
            f"{escape(amount)} vendor payment was held before binding."
            "</div>"
            '<div class="cage-small">'
            f'{escape(held.get("boundary_reason") or held.get("reason"))}'
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            '<div class="cage-card">'
            '<div class="cage-card-title">Decision summary</div>'
            '<div class="cage-detail-row">'
            '<div class="cage-detail-label">Agent</div>'
            '<div class="cage-detail-value">'
            f'{escape(held.get("agent_id"))}'
            "</div>"
            "</div>"
            '<div class="cage-detail-row">'
            '<div class="cage-detail-label">Boundary</div>'
            f'<div class="cage-detail-value">{badge(outcome)}</div>'
            "</div>"
            '<div class="cage-detail-row">'
            '<div class="cage-detail-label">Effect</div>'
            f'<div class="cage-detail-value">{badge(effect)}</div>'
            "</div>"
            '<div class="cage-detail-row">'
            '<div class="cage-detail-label">System</div>'
            f'<div class="cage-detail-value">{badge(system)}</div>'
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="cage-section-title">'
        "Consequence boundary flow"
        "</div>",
        unsafe_allow_html=True,
    )

    columns = st.columns(
        6,
        gap="small",
    )

    cards = [
        flow_card(
            "Agent Request",
            amount,
            action_label(held),
            "blue",
        ),
        flow_card(
            "Standing",
            "Limit exceeded",
            f"Direct limit {standing_limit}",
            "warn",
        ),
        flow_card(
            "Policy + Approval",
            "Approval missing",
            f"Required above {standing_limit}",
            "warn",
        ),
        flow_card(
            "CAGE Boundary",
            display_status(outcome),
            "Decision before effect",
            "warn",
        ),
        flow_card(
            "Effect Gate",
            display_status(effect),
            "Protected effect prevented",
            "warn",
        ),
        flow_card(
            "System of Record",
            display_status(system),
            "No durable write",
            "warn",
        ),
    ]

    for column, card in zip(columns, cards):
        with column:
            st.markdown(
                card,
                unsafe_allow_html=True,
            )

    recent_column, replay_column = st.columns(
        [1.25, 0.75],
        gap="medium",
    )

    with recent_column:
        st.markdown(
            '<div class="cage-section-title">'
            "Recent boundary runs"
            "</div>",
            unsafe_allow_html=True,
        )

        # The Overview only shows a small snapshot.
        # The Boundary Runs page contains the complete history.
        recent_items = sorted_receipts(receipts)[:3]

        for item in recent_items:
            item_effect = find_effect(
                item,
                effects,
            )

            is_replay = bool(
                item.get("replay_of_receipt_id")
            )

            run_label = (
                "Replay"
                if is_replay
                else "Original"
            )

            amount_text = money(
                item.get("amount"),
                item.get("currency", "USD"),
            )

            action_type = str(
                item.get("action_type")
                or "action"
            )

            action_type = (
                action_type
                .replace("_", " ")
                .title()
            )

            with st.container(border=True):
                row = st.columns(
                    [2.5, 0.8, 0.8, 0.7],
                    vertical_alignment="center",
                )

                with row[0]:
                    st.markdown(
                        f"**{escape(amount_text)} "
                        f"{escape(action_type)}**"
                    )

                    st.caption(
                        f"{short_time(item)} · "
                        f"{item.get('agent_id') or '—'} · "
                        f"{run_label}"
                    )

                with row[1]:
                    st.markdown(
                        badge(
                            boundary_outcome(item)
                        ),
                        unsafe_allow_html=True,
                    )

                with row[2]:
                    st.markdown(
                        badge(
                            effect_outcome(
                                item,
                                item_effect,
                            )
                        ),
                        unsafe_allow_html=True,
                    )

                with row[3]:
                    if st.button(
                        "View",
                        key=(
                            f"overview_"
                            f"{item.get('receipt_id')}"
                        ),
                        use_container_width=True,
                    ):
                        open_warrant(
                            str(
                                item.get("receipt_id")
                            )
                        )

    with replay_column:
        st.markdown(
            '<div class="cage-section-title">'
            "Latest replay"
            "</div>",
            unsafe_allow_html=True,
        )

        if not admitted:
            st.info(
                "No linked replay Warrant was found."
            )
            return

        before = (
            f"{display_status(boundary_outcome(held))} · "
            f"{display_status(effect_outcome(held, held_effect))} · "
            f"{display_status(system_status(held, held_effect))}"
        )

        after = (
            f"{display_status(boundary_outcome(admitted))} · "
            f"{display_status(effect_outcome(admitted, admitted_effect))} · "
            f"{display_status(system_status(admitted, admitted_effect))}"
        )

        original_column, replay_result_column = st.columns(
            2,
            gap="small",
        )

        with original_column:
            st.markdown(
                '<div class="cage-card warn" '
                'style="min-height:105px;">'
                '<div class="cage-kicker">Original</div>'
                '<div class="cage-card-title">'
                f"{escape(before)}"
                "</div>"
                "</div>",
                unsafe_allow_html=True,
            )

        with replay_result_column:
            st.markdown(
                '<div class="cage-card good" '
                'style="min-height:105px;">'
                '<div class="cage-kicker">After approval</div>'
                '<div class="cage-card-title">'
                f"{escape(after)}"
                "</div>"
                "</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
            '<div class="cage-replay-note">'
            "Only approval changed. "
            "The original Warrant remains preserved."
            "</div>",
            unsafe_allow_html=True,
        )

        if st.button(
            "Compare replay",
            use_container_width=True,
        ):
            st.session_state.cage_page = "Replay"
            st.rerun()