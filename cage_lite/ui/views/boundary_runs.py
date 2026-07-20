from __future__ import annotations

import streamlit as st

from cage_lite.ui.app_data import badge
from cage_lite.ui.app_data import boundary_outcome
from cage_lite.ui.app_data import display_status
from cage_lite.ui.app_data import effect_outcome
from cage_lite.ui.app_data import escape
from cage_lite.ui.app_data import find_effect
from cage_lite.ui.app_data import money
from cage_lite.ui.app_data import short_time
from cage_lite.ui.app_data import sorted_receipts
from cage_lite.ui.app_data import system_status


VISIBLE_SCENARIO_LIMIT = 6
VISIBLE_EXECUTION_LIMIT = 6

ITEM_SEPARATOR = " \u00b7 "
EMPTY_VALUE = "\u2014"


def open_warrant(receipt_id: str) -> None:
    st.session_state.selected_receipt_id = receipt_id
    st.session_state.cage_page = "Warrants"
    st.rerun()


def build_action_histories(
    receipts: list[dict],
) -> list[dict]:
    items = sorted_receipts(receipts)

    receipts_by_id = {
        str(item.get("receipt_id")): item
        for item in items
        if item.get("receipt_id")
    }

    replays_by_original: dict[str, list[dict]] = {}

    for item in items:
        original_id = item.get(
            "replay_of_receipt_id"
        )

        if not original_id:
            continue

        original_id = str(original_id)

        replays_by_original.setdefault(
            original_id,
            [],
        ).append(item)

    histories = []
    seen_history_ids = set()

    for item in items:
        receipt_id = str(
            item.get("receipt_id") or ""
        )

        original_id = item.get(
            "replay_of_receipt_id"
        )

        if (
            original_id
            and str(original_id) in receipts_by_id
        ):
            history_id = str(original_id)
        else:
            history_id = receipt_id

        if (
            not history_id
            or history_id in seen_history_ids
        ):
            continue

        seen_history_ids.add(history_id)

        original = receipts_by_id.get(
            history_id,
            item,
        )

        replays = sorted_receipts(
            replays_by_original.get(
                history_id,
                [],
            )
        )

        history_items = [
            original,
            *replays,
        ]

        latest = sorted_receipts(
            history_items,
        )[0]

        histories.append(
            {
                "history_id": history_id,
                "original": original,
                "latest": latest,
                "replays": replays,
            }
        )

    return histories


def scenario_key(
    history: dict,
) -> tuple[str, ...]:
    original = history["original"]

    return (
        str(original.get("agent_id") or ""),
        str(original.get("action_type") or ""),
        str(original.get("action_summary") or ""),
        str(original.get("amount") or ""),
        str(original.get("currency") or "USD"),
        str(original.get("standing_limit") or ""),
    )


def group_scenarios(
    histories: list[dict],
) -> list[dict]:
    grouped: dict[
        tuple[str, ...],
        list[dict],
    ] = {}

    for history in histories:
        key = scenario_key(history)

        grouped.setdefault(
            key,
            [],
        ).append(history)

    scenarios = []

    for key, scenario_histories in grouped.items():
        scenarios.append(
            {
                "scenario_key": key,
                "latest_history": scenario_histories[0],
                "histories": scenario_histories,
            }
        )

    return scenarios


def scenario_has_replay(
    scenario: dict,
) -> bool:
    return any(
        bool(history["replays"])
        for history in scenario["histories"]
    )


def scenario_matches_search(
    scenario: dict,
    search: str,
) -> bool:
    latest_history = scenario["latest_history"]
    original = latest_history["original"]

    searchable_parts = [
        str(original.get("agent_id") or ""),
        str(original.get("action_type") or ""),
        str(original.get("action_summary") or ""),
        str(original.get("amount") or ""),
        str(original.get("currency") or ""),
    ]

    for history in scenario["histories"]:
        searchable_parts.extend(
            [
                str(
                    history["original"].get(
                        "receipt_id"
                    )
                    or ""
                ),
                str(
                    history["latest"].get(
                        "receipt_id"
                    )
                    or ""
                ),
            ]
        )

    searchable = " ".join(
        searchable_parts
    ).lower()

    return search in searchable


def action_title(
    receipt: dict,
) -> str:
    amount_text = money(
        receipt.get("amount"),
        receipt.get("currency", "USD"),
    )

    action_type = str(
        receipt.get("action_type")
        or "action"
    )

    action_type = (
        action_type
        .replace("_", " ")
        .title()
    )

    return f"{amount_text} {action_type}"


def status_summary(
    receipt: dict,
    effects: list[dict],
) -> str:
    effect = find_effect(
        receipt,
        effects,
    )

    return ITEM_SEPARATOR.join(
        [
            display_status(
                boundary_outcome(receipt)
            ),
            display_status(
                effect_outcome(
                    receipt,
                    effect,
                )
            ),
            display_status(
                system_status(
                    receipt,
                    effect,
                )
            ),
        ]
    )


def status_tone(
    receipt: dict,
) -> str:
    outcome = boundary_outcome(
        receipt
    ).strip().lower()

    if outcome in {
        "admitted",
        "allowed",
    }:
        return "good"

    if outcome in {
        "held",
        "blocked",
        "denied",
    }:
        return "warn"

    return "blue"


def status_card(
    label: str,
    receipt: dict,
    effects: list[dict],
) -> str:
    tone = status_tone(receipt)

    return (
        f'<div class="cage-card {tone}" '
        'style="min-height:115px;">'
        '<div class="cage-kicker">'
        f"{escape(label)}"
        "</div>"
        '<div class="cage-card-title">'
        f"{escape(status_summary(receipt, effects))}"
        "</div>"
        "</div>"
    )


def render_execution_history(
    scenario: dict,
) -> None:
    histories = scenario["histories"]

    visible_histories = histories[
        :VISIBLE_EXECUTION_LIMIT
    ]

    visible_count = len(
        visible_histories
    )

    total_count = len(
        histories
    )

    if total_count > visible_count:
        expander_label = (
            f"Recent executions "
            f"({visible_count} of {total_count})"
        )
    else:
        execution_word = (
            "execution"
            if total_count == 1
            else "executions"
        )

        expander_label = (
            f"{total_count} {execution_word}"
        )

    scenario_history_id = str(
        scenario["latest_history"].get(
            "history_id"
        )
        or "scenario"
    )

    with st.expander(
        expander_label
    ):
        for index, history in enumerate(
            visible_histories
        ):
            original = history["original"]
            latest = history["latest"]

            has_replay = bool(
                history["replays"]
            )

            row = st.columns(
                [1.45, 1.8, 0.55],
                vertical_alignment="center",
            )

            with row[0]:
                st.caption(
                    short_time(latest)
                )

                if has_replay:
                    st.caption(
                        "Held-to-admitted replay"
                    )
                else:
                    st.caption(
                        "Original attempt"
                    )

            with row[1]:
                original_badge = badge(
                    boundary_outcome(original)
                )

                if has_replay:
                    latest_badge = badge(
                        boundary_outcome(latest)
                    )

                    flow = (
                        f"{original_badge}"
                        "&nbsp;&nbsp;→&nbsp;&nbsp;"
                        f"{latest_badge}"
                    )
                else:
                    flow = original_badge

                st.markdown(
                    flow,
                    unsafe_allow_html=True,
                )

            with row[2]:
                button_key = (
                    "execution_open_"
                    f"{scenario_history_id}_"
                    f"{index}_"
                    f"{history['history_id']}"
                )

                if st.button(
                    "Open",
                    key=button_key,
                    use_container_width=True,
                ):
                    open_warrant(
                        str(
                            latest.get(
                                "receipt_id"
                            )
                        )
                    )

            if index < visible_count - 1:
                st.divider()


def render_replay_result(
    original: dict,
    latest: dict,
    effects: list[dict],
) -> None:
    before_column, arrow_column, after_column = (
        st.columns(
            [1, 0.08, 1],
            gap="small",
            vertical_alignment="center",
        )
    )

    with before_column:
        st.markdown(
            status_card(
                "Original attempt",
                original,
                effects,
            ),
            unsafe_allow_html=True,
        )

    with arrow_column:
        st.markdown(
            '<div style="'
            "text-align:center;"
            "font-size:1.7rem;"
            "font-weight:700;"
            'color:#64748b;">'
            "→"
            "</div>",
            unsafe_allow_html=True,
        )

    with after_column:
        st.markdown(
            status_card(
                "After approval",
                latest,
                effects,
            ),
            unsafe_allow_html=True,
        )


def render_original_result(
    original: dict,
    effects: list[dict],
) -> None:
    result_column, spacer_column = st.columns(
        [1, 1],
        gap="medium",
    )

    with result_column:
        st.markdown(
            status_card(
                "Original result",
                original,
                effects,
            ),
            unsafe_allow_html=True,
        )

    with spacer_column:
        st.empty()


def render_scenario(
    scenario: dict,
    effects: list[dict],
    scenario_index: int,
) -> None:
    latest_history = scenario[
        "latest_history"
    ]

    original = latest_history[
        "original"
    ]

    latest = latest_history[
        "latest"
    ]

    histories = scenario[
        "histories"
    ]

    has_replay = bool(
        latest_history["replays"]
    )

    execution_count = len(
        histories
    )

    execution_word = (
        "execution"
        if execution_count == 1
        else "executions"
    )

    agent_id = str(
        original.get("agent_id")
        or EMPTY_VALUE
    )

    latest_receipt_id = str(
        latest.get("receipt_id")
        or latest_history["history_id"]
    )

    with st.container(
        border=True
    ):
        header = st.columns(
            [3.8, 0.7],
            vertical_alignment="center",
        )

        with header[0]:
            st.markdown(
                f"### {escape(action_title(original))}"
            )

            st.caption(
                f"{agent_id}"
                f"{ITEM_SEPARATOR}"
                f"Latest activity "
                f"{short_time(latest)}"
                f"{ITEM_SEPARATOR}"
                f"{execution_count} "
                f"{execution_word}"
            )

        with header[1]:
            if st.button(
                "Open latest",
                key=(
                    "scenario_open_"
                    f"{scenario_index}_"
                    f"{latest_receipt_id}"
                ),
                use_container_width=True,
            ):
                open_warrant(
                    latest_receipt_id
                )

        if has_replay:
            render_replay_result(
                original,
                latest,
                effects,
            )

            st.markdown(
                '<div style="'
                "margin:0.85rem 0 0.75rem 0.1rem;"
                "font-size:0.95rem;"
                'color:#64748b;">'
                "The original Warrant remains preserved and "
                "linked to the admitted replay."
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            render_original_result(
                original,
                effects,
            )

        render_execution_history(
            scenario
        )


def render(
    receipts: list[dict],
    effects: list[dict],
) -> None:
    st.markdown(
        '<div class="cage-page-title">'
        "Boundary Runs"
        "</div>"
        '<div class="cage-page-subtitle">'
        "Consequential action histories. "
        "Repeated executions of the same scenario are grouped."
        "</div>",
        unsafe_allow_html=True,
    )

    histories = build_action_histories(
        receipts
    )

    scenarios = group_scenarios(
        histories
    )

    filters = st.columns(
        [1, 1, 1.4]
    )

    with filters[0]:
        outcomes = [
            "All",
            *sorted(
                {
                    display_status(
                        boundary_outcome(
                            scenario[
                                "latest_history"
                            ]["latest"]
                        )
                    )
                    for scenario in scenarios
                }
            ),
        ]

        outcome_filter = st.selectbox(
            "Latest boundary outcome",
            outcomes,
        )

    with filters[1]:
        replay_filter = st.selectbox(
            "Replay status",
            [
                "All",
                "Replayed",
                "Original only",
            ],
        )

    with filters[2]:
        search = st.text_input(
            "Search",
            placeholder=(
                "Agent, action, or Warrant ID"
            ),
        ).strip().lower()

    filtered = []

    for scenario in scenarios:
        latest = scenario[
            "latest_history"
        ]["latest"]

        has_replay = scenario_has_replay(
            scenario
        )

        if outcome_filter != "All":
            latest_outcome = display_status(
                boundary_outcome(latest)
            )

            if latest_outcome != outcome_filter:
                continue

        if (
            replay_filter == "Replayed"
            and not has_replay
        ):
            continue

        if (
            replay_filter == "Original only"
            and has_replay
        ):
            continue

        if (
            search
            and not scenario_matches_search(
                scenario,
                search,
            )
        ):
            continue

        filtered.append(
            scenario
        )

    visible_scenarios = filtered[
        :VISIBLE_SCENARIO_LIMIT
    ]

    visible_count = len(
        visible_scenarios
    )

    total_scenarios = len(
        filtered
    )

    total_executions = sum(
        len(scenario["histories"])
        for scenario in filtered
    )

    scenario_word = (
        "scenario"
        if total_scenarios == 1
        else "scenarios"
    )

    execution_word = (
        "execution"
        if total_executions == 1
        else "executions"
    )

    if total_scenarios > visible_count:
        st.caption(
            f"{visible_count} of "
            f"{total_scenarios} "
            f"{scenario_word} shown"
            f"{ITEM_SEPARATOR}"
            f"{total_executions} "
            f"{execution_word}"
        )
    else:
        st.caption(
            f"{total_scenarios} "
            f"{scenario_word}"
            f"{ITEM_SEPARATOR}"
            f"{total_executions} "
            f"{execution_word}"
        )

    if not visible_scenarios:
        st.info(
            "No boundary runs match the selected filters."
        )
        return

    for scenario_index, scenario in enumerate(
        visible_scenarios
    ):
        render_scenario(
            scenario,
            effects,
            scenario_index,
        )