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


ITEM_SEPARATOR = " \u00b7 "
EMPTY_VALUE = "\u2014"


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


def boundary_card_tone(outcome: str) -> str:
    normalized = outcome.strip().lower()

    if normalized in {"admitted", "allowed"}:
        return "good"

    if normalized in {"held", "blocked", "denied"}:
        return "warn"

    return "blue"


def latest_decision_message(
    receipt: dict,
    outcome: str,
) -> str:
    amount = money(
        receipt.get("amount"),
        receipt.get("currency", "USD"),
    )

    normalized = outcome.strip().lower()

    if normalized in {"admitted", "allowed"}:
        return (
            f"{amount} vendor payment was admitted "
            "at the consequence boundary."
        )

    if normalized in {"held", "blocked", "denied"}:
        return (
            f"{amount} vendor payment was held "
            "before binding."
        )

    return (
        f"{amount} vendor payment received a "
        f"{display_status(outcome)} boundary decision."
    )


def render_latest_summary(
    latest: dict,
    effects: list[dict],
) -> None:
    latest_effect_record = find_effect(
        latest,
        effects,
    )

    latest_outcome = boundary_outcome(latest)

    latest_effect = effect_outcome(
        latest,
        latest_effect_record,
    )

    latest_system = system_status(
        latest,
        latest_effect_record,
    )

    latest_reason = (
        latest.get("boundary_reason")
        or latest.get("reason")
        or "No boundary reason was recorded."
    )

    card_tone = boundary_card_tone(
        latest_outcome,
    )

    left, right = st.columns(
        [1.35, 0.65],
        gap="medium",
    )

    with left:
        st.markdown(
            f'<div class="cage-card {card_tone}">'
            '<div class="cage-kicker">'
            "Latest boundary decision"
            "</div>"
            '<div class="cage-card-title" '
            'style="font-size:1.45rem;">'
            f"{escape(latest_decision_message(latest, latest_outcome))}"
            "</div>"
            '<div class="cage-small">'
            f"{escape(latest_reason)}"
            "</div>"
            '<div class="cage-small" '
            'style="margin-top:0.45rem;">'
            f"{escape(short_time(latest))}"
            f"{ITEM_SEPARATOR}"
            f"{escape(latest.get('receipt_id') or EMPTY_VALUE)}"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            '<div class="cage-card">'
            '<div class="cage-card-title">'
            "Decision summary"
            "</div>"
            '<div class="cage-detail-row">'
            '<div class="cage-detail-label">Agent</div>'
            '<div class="cage-detail-value">'
            f"{escape(latest.get('agent_id') or EMPTY_VALUE)}"
            "</div>"
            "</div>"
            '<div class="cage-detail-row">'
            '<div class="cage-detail-label">Boundary</div>'
            '<div class="cage-detail-value">'
            f"{badge(latest_outcome)}"
            "</div>"
            "</div>"
            '<div class="cage-detail-row">'
            '<div class="cage-detail-label">Effect</div>'
            '<div class="cage-detail-value">'
            f"{badge(latest_effect)}"
            "</div>"
            "</div>"
            '<div class="cage-detail-row">'
            '<div class="cage-detail-label">System</div>'
            '<div class="cage-detail-value">'
            f"{badge(latest_system)}"
            "</div>"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )


def render_original_held_flow(
    held: dict | None,
    effects: list[dict],
) -> None:
    st.markdown(
        '<div class="cage-section-title">'
        "Original held boundary flow"
        "</div>",
        unsafe_allow_html=True,
    )

    if not held:
        st.info(
            "No HELD Warrant was found in the selected artifact folder."
        )
        return

    held_effect_record = find_effect(
        held,
        effects,
    )

    held_outcome = boundary_outcome(
        held,
    )

    held_effect = effect_outcome(
        held,
        held_effect_record,
    )

    held_system = system_status(
        held,
        held_effect_record,
    )

    amount = money(
        held.get("amount"),
        held.get("currency", "USD"),
    )

    standing_limit = money(
        held.get("standing_limit"),
        held.get("currency", "USD"),
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
            display_status(held_outcome),
            "Decision before effect",
            "warn",
        ),
        flow_card(
            "Effect Gate",
            display_status(held_effect),
            "Protected effect prevented",
            "warn",
        ),
        flow_card(
            "System of Record",
            display_status(held_system),
            "No durable write",
            "warn",
        ),
    ]

    for column, card in zip(
        columns,
        cards,
    ):
        with column:
            st.markdown(
                card,
                unsafe_allow_html=True,
            )


def render_recent_runs(
    receipts: list[dict],
    effects: list[dict],
) -> None:
    recent_items = sorted_receipts(
        receipts,
    )[:3]

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

        agent_id = str(
            item.get("agent_id")
            or EMPTY_VALUE
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
                    f"{short_time(item)}"
                    f"{ITEM_SEPARATOR}"
                    f"{agent_id}"
                    f"{ITEM_SEPARATOR}"
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


def render_latest_replay(
    held: dict | None,
    admitted: dict | None,
    effects: list[dict],
) -> None:
    if not held or not admitted:
        st.info(
            "No complete held-to-admitted replay pair was found."
        )
        return

    held_effect_record = find_effect(
        held,
        effects,
    )

    admitted_effect_record = find_effect(
        admitted,
        effects,
    )

    before = ITEM_SEPARATOR.join(
        [
            display_status(
                boundary_outcome(held)
            ),
            display_status(
                effect_outcome(
                    held,
                    held_effect_record,
                )
            ),
            display_status(
                system_status(
                    held,
                    held_effect_record,
                )
            ),
        ]
    )

    after = ITEM_SEPARATOR.join(
        [
            display_status(
                boundary_outcome(admitted)
            ),
            display_status(
                effect_outcome(
                    admitted,
                    admitted_effect_record,
                )
            ),
            display_status(
                system_status(
                    admitted,
                    admitted_effect_record,
                )
            ),
        ]
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
            '<div class="cage-kicker">'
            "After approval"
            "</div>"
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


def render(
    summary: dict,
    receipts: list[dict],
    effects: list[dict],
) -> None:
    page_heading(
        "Overview",
        (
            "Latest boundary decision, original held flow, "
            "recent runs, and replay status."
        ),
    )

    items = sorted_receipts(
        receipts,
    )

    if not items:
        st.warning(
            "No Warrants were found in the selected artifact folder."
        )
        return

    latest = items[0]

    held, admitted = latest_replay_pair(
        receipts,
    )

    render_latest_summary(
        latest,
        effects,
    )

    render_original_held_flow(
        held,
        effects,
    )

    recent_column, replay_column = st.columns(
        [1.25, 0.75],
        gap="medium",
        vertical_alignment="top",
    )

    with recent_column:
        st.markdown(
            '<div class="cage-section-title">'
            "Recent boundary runs"
            "</div>",
            unsafe_allow_html=True,
        )

        render_recent_runs(
            receipts,
            effects,
        )

    with replay_column:
        st.markdown(
            '<div class="cage-section-title">'
            "Latest replay"
            "</div>",
            unsafe_allow_html=True,
        )

        render_latest_replay(
            held,
            admitted,
            effects,
        )