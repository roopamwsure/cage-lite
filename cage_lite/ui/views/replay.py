from __future__ import annotations

import json

import streamlit as st

from cage_lite.ui.app_data import action_label
from cage_lite.ui.app_data import boundary_outcome
from cage_lite.ui.app_data import display_status
from cage_lite.ui.app_data import effect_outcome
from cage_lite.ui.app_data import find_effect
from cage_lite.ui.app_data import money
from cage_lite.ui.app_data import receipt_by_id
from cage_lite.ui.app_data import sorted_receipts
from cage_lite.ui.app_data import system_status


def changed(before: object, after: object) -> str:
    if str(before) == str(after):
        return "No"

    return "Yes"


def render(
    receipts: list[dict],
    effects: list[dict],
) -> None:
    st.markdown(
        '<div class="cage-page-title">Replay</div>'
        '<div class="cage-page-subtitle">'
        "Compare an original Warrant with a new run "
        "after conditions change."
        "</div>",
        unsafe_allow_html=True,
    )

    replay_items = [
        item
        for item in sorted_receipts(receipts)
        if item.get("replay_of_receipt_id")
    ]

    if not replay_items:
        st.info("No linked replay Warrants were found.")
        return

    warrants = receipt_by_id(receipts)

    replay_ids = [
        str(item.get("receipt_id"))
        for item in replay_items
        if item.get("receipt_id")
    ]

    selected_replay_id = st.selectbox(
        "Select replay Warrant",
        replay_ids,
        format_func=lambda receipt_id: (
            f"{receipt_id} · replay of "
            f"{warrants[receipt_id].get('replay_of_receipt_id')}"
        ),
    )

    replay_warrant = warrants[selected_replay_id]

    original_id = str(
        replay_warrant.get("replay_of_receipt_id")
    )

    original_warrant = warrants.get(original_id)

    if not original_warrant:
        st.error(
            f"Original Warrant was not found: {original_id}"
        )
        return

    original_effect = find_effect(
        original_warrant,
        effects,
    )

    replay_effect = find_effect(
        replay_warrant,
        effects,
    )

    st.markdown(
        '<div class="cage-card blue">'
        '<div class="cage-card-title">Replay chain</div>'
        f'<div class="cage-small">'
        f"Original Warrant: {original_id}"
        "<br>"
        "↓"
        "<br>"
        f"Replay Warrant: {selected_replay_id}"
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    original_approval = (
        "Present"
        if original_warrant.get("approval_present")
        else "Missing"
    )

    replay_approval = (
        "Present"
        if replay_warrant.get("approval_present")
        else "Missing"
    )

    comparison = [
        {
            "Condition": "Action",
            "Original": action_label(original_warrant),
            "Replay": action_label(replay_warrant),
        },
        {
            "Condition": "Amount",
            "Original": money(
                original_warrant.get("amount"),
                original_warrant.get("currency", "USD"),
            ),
            "Replay": money(
                replay_warrant.get("amount"),
                replay_warrant.get("currency", "USD"),
            ),
        },
        {
            "Condition": "Standing limit",
            "Original": money(
                original_warrant.get("standing_limit"),
                original_warrant.get("currency", "USD"),
            ),
            "Replay": money(
                replay_warrant.get("standing_limit"),
                replay_warrant.get("currency", "USD"),
            ),
        },
        {
            "Condition": "Policy",
            "Original": original_warrant.get("policy_ref"),
            "Replay": replay_warrant.get("policy_ref"),
        },
        {
            "Condition": "Approval",
            "Original": original_approval,
            "Replay": replay_approval,
        },
        {
            "Condition": "Boundary",
            "Original": display_status(
                boundary_outcome(original_warrant)
            ),
            "Replay": display_status(
                boundary_outcome(replay_warrant)
            ),
        },
        {
            "Condition": "Effect",
            "Original": display_status(
                effect_outcome(
                    original_warrant,
                    original_effect,
                )
            ),
            "Replay": display_status(
                effect_outcome(
                    replay_warrant,
                    replay_effect,
                )
            ),
        },
        {
            "Condition": "System of Record",
            "Original": display_status(
                system_status(
                    original_warrant,
                    original_effect,
                )
            ),
            "Replay": display_status(
                system_status(
                    replay_warrant,
                    replay_effect,
                )
            ),
        },
    ]

    for row in comparison:
        row["Changed"] = changed(
            row["Original"],
            row["Replay"],
        )

    st.markdown(
        '<div class="cage-section-title">'
        "What changed"
        "</div>",
        unsafe_allow_html=True,
    )

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
    )

    changed_inputs = []

    if original_approval != replay_approval:
        changed_inputs.append(
            f"approval changed from "
            f"{original_approval.lower()} "
            f"to {replay_approval.lower()}"
        )

    if (
        original_warrant.get("standing_limit")
        != replay_warrant.get("standing_limit")
    ):
        changed_inputs.append(
            "standing limit changed"
        )

    if (
        original_warrant.get("policy_ref")
        != replay_warrant.get("policy_ref")
    ):
        changed_inputs.append(
            "policy changed"
        )

    if changed_inputs:
        reason = (
            "The decision changed because "
            + ", ".join(changed_inputs)
            + ". The original Warrant was preserved, "
            "and the replay created a new linked Warrant."
        )

        st.success(reason)

    else:
        st.warning(
            "The outcome changed, but no changed input "
            "was identified from the fields stored "
            "in these Warrants."
        )

    download_data = {
        "artifact_name": "CAGE Replay Comparison",
        "original_warrant": original_warrant,
        "original_effect": original_effect,
        "replay_warrant": replay_warrant,
        "replay_effect": replay_effect,
    }

    st.download_button(
        "Download Replay Comparison JSON",
        data=json.dumps(
            download_data,
            indent=2,
            sort_keys=True,
        ),
        file_name=(
            f"replay-{original_id}-"
            f"to-{selected_replay_id}.json"
        ),
        mime="application/json",
        use_container_width=True,
    )