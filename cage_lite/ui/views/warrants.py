from __future__ import annotations

import json

import streamlit as st

from cage_lite.core.receipt import DIGEST_STATUS_LEGACY
from cage_lite.core.receipt import DIGEST_STATUS_MISMATCH
from cage_lite.core.receipt import DIGEST_STATUS_NOT_AVAILABLE
from cage_lite.core.receipt import DIGEST_STATUS_VERIFIED
from cage_lite.core.receipt import verify_receipt_digest
from cage_lite.ui.app_data import action_label
from cage_lite.ui.app_data import badge
from cage_lite.ui.app_data import boundary_outcome
from cage_lite.ui.app_data import display_status
from cage_lite.ui.app_data import effect_outcome
from cage_lite.ui.app_data import escape
from cage_lite.ui.app_data import find_effect
from cage_lite.ui.app_data import money
from cage_lite.ui.app_data import receipt_by_id
from cage_lite.ui.app_data import replay_children
from cage_lite.ui.app_data import short_time
from cage_lite.ui.app_data import sorted_receipts
from cage_lite.ui.app_data import system_status
from cage_lite.ui.app_data import yes_no


ITEM_SEPARATOR = " \u00b7 "
REPLAY_ARROW = "\u2192"


def detail_row(label: str, value: object) -> str:
    return (
        '<div class="cage-detail-row">'
        f'<div class="cage-detail-label">{escape(label)}</div>'
        f'<div class="cage-detail-value">{escape(value)}</div>'
        "</div>"
    )


def detail_html_row(label: str, value_html: str) -> str:
    return (
        '<div class="cage-detail-row">'
        f'<div class="cage-detail-label">{escape(label)}</div>'
        f'<div class="cage-detail-value">{value_html}</div>'
        "</div>"
    )


def hash_block(label: str, value: object) -> str:
    display_value = value

    if display_value is None or display_value == "":
        display_value = "Not recorded"

    return (
        '<div class="cage-hash-field">'
        f'<div class="cage-hash-label">{escape(label)}</div>'
        f'<div class="cage-hash-value">{escape(display_value)}</div>'
        "</div>"
    )


def integrity_badge(status: str) -> str:
    badge_class = {
        DIGEST_STATUS_VERIFIED: "good",
        DIGEST_STATUS_MISMATCH: "bad",
        DIGEST_STATUS_NOT_AVAILABLE: "warn",
        DIGEST_STATUS_LEGACY: "neutral",
    }.get(status, "neutral")

    return (
        f'<span class="cage-badge {badge_class}">'
        f"{escape(status)}"
        "</span>"
    )


def verification_detail(status: str, reason: str) -> str:
    if status == DIGEST_STATUS_VERIFIED:
        return "Recorded digest matches recomputed schema 0.4 content."

    if status == DIGEST_STATUS_MISMATCH:
        return "Recorded digest does not match recomputed schema 0.4 content."

    if status == DIGEST_STATUS_NOT_AVAILABLE:
        return "No valid recorded digest is available for verification."

    return reason


def integrity_card_html(warrant: dict) -> str:
    verification = verify_receipt_digest(warrant)

    integrity_rows = (
        detail_row(
            "Schema version",
            warrant.get("schema_version"),
        )
        + detail_row(
            "Created at",
            short_time(warrant),
        )
        + detail_html_row(
            "Digest verification",
            integrity_badge(verification.status),
        )
    )

    detail = verification_detail(
        verification.status,
        verification.reason,
    )

    return (
        '<div class="cage-card cage-integrity-card cage-stacked-card">'
        '<div class="cage-card-title">Integrity</div>'
        f"{integrity_rows}"
        f'{hash_block("Payload hash", warrant.get("action_payload_hash"))}'
        f'{hash_block("Recorded digest", warrant.get("digest"))}'
        '<div class="cage-integrity-detail">'
        f"{escape(detail)}"
        "</div>"
        '<div class="cage-integrity-note">'
        "Digest verification confirms content consistency with the "
        "recorded digest. It does not prove signer identity or "
        "external notarization."
        "</div>"
        "</div>"
    )


def render_integrity_card(warrant: dict) -> None:
    st.markdown(
        integrity_card_html(warrant),
        unsafe_allow_html=True,
    )


def render(
    receipts: list[dict],
    effects: list[dict],
) -> None:
    st.markdown(
        '<div class="cage-page-title">CAGE Warrants</div>'
        '<div class="cage-page-subtitle">'
        "Decision proof and effect proof for each evaluated action."
        "</div>",
        unsafe_allow_html=True,
    )

    items = sorted_receipts(receipts)

    if not items:
        st.info("No Warrants were found.")
        return

    warrants = receipt_by_id(items)
    warrant_ids = list(warrants.keys())

    selected_id = str(
        st.session_state.get("selected_receipt_id")
        or warrant_ids[0]
    )

    if selected_id not in warrants:
        selected_id = warrant_ids[0]

    selected_id = st.selectbox(
        "Select Warrant",
        warrant_ids,
        index=warrant_ids.index(selected_id),
        format_func=lambda receipt_id: (
            f"{receipt_id}"
            f"{ITEM_SEPARATOR}"
            f"{display_status(boundary_outcome(warrants[receipt_id]))}"
            f"{ITEM_SEPARATOR}"
            f"{action_label(warrants[receipt_id])}"
        ),
    )

    st.session_state.selected_receipt_id = selected_id

    warrant = warrants[selected_id]
    effect = find_effect(warrant, effects)

    outcome = boundary_outcome(warrant)
    disposition = effect_outcome(warrant, effect)
    system = system_status(warrant, effect)

    st.markdown(
        '<div class="cage-card blue">'
        '<div class="cage-kicker">CAGE Warrant</div>'
        f'<div class="cage-warrant-id">{escape(selected_id)}</div>'
        '<div class="cage-small">'
        f"{escape(action_label(warrant))}"
        f"{ITEM_SEPARATOR}"
        f"{escape(short_time(warrant))}"
        "</div>"
        f'<div style="margin-top:0.5rem;">{badge(outcome)}</div>'
        "</div>"
        '<div aria-hidden="true" style="height:1rem;"></div>',
        unsafe_allow_html=True,
    )

    decision_rows = (
        detail_row(
            "Actor",
            warrant.get("actor_id"),
        )
        + detail_row(
            "Agent",
            warrant.get("agent_id"),
        )
        + detail_row(
            "Action",
            action_label(warrant),
        )
        + detail_row(
            "Amount",
            money(
                warrant.get("amount"),
                warrant.get("currency", "USD"),
            ),
        )
        + detail_row(
            "Standing reference",
            warrant.get("standing_ref"),
        )
        + detail_row(
            "Standing limit",
            money(
                warrant.get("standing_limit"),
                warrant.get("currency", "USD"),
            ),
        )
        + detail_row(
            "Policy",
            warrant.get("policy_ref"),
        )
        + detail_row(
            "Approval required",
            yes_no(warrant.get("approval_required")),
        )
        + detail_row(
            "Approval present",
            yes_no(warrant.get("approval_present")),
        )
        + detail_row(
            "Approval reference",
            warrant.get("approval_ref"),
        )
        + detail_row(
            "Boundary",
            display_status(outcome),
        )
        + detail_row(
            "Reason",
            warrant.get("boundary_reason")
            or warrant.get("reason"),
        )
    )

    evidence_refs = warrant.get("evidence_refs") or []

    if evidence_refs:
        evidence_rows = "".join(
            detail_row(
                "Evidence reference",
                reference,
            )
            for reference in evidence_refs
        )
    else:
        evidence_rows = detail_row(
            "Evidence reference",
            "None recorded",
        )

    effect_rows = (
        detail_row(
            "Effect ID",
            warrant.get("effect_id")
            or effect.get("effect_id"),
        )
        + detail_row(
            "Disposition",
            display_status(disposition),
        )
        + detail_row(
            "Invocation attempted",
            yes_no(warrant.get("effect_attempted")),
        )
        + detail_row(
            "Effect executed",
            yes_no(
                warrant.get("effect_executed")
                if "effect_executed" in warrant
                else effect.get("executed")
            ),
        )
        + detail_row(
            "System of record",
            display_status(system),
        )
        + detail_row(
            "Attempt ID",
            warrant.get("attempt_id"),
        )
        + detail_row(
            "Movement ID",
            warrant.get("movement_id"),
        )
    )

    left_column, right_column = st.columns(
        2,
        gap="medium",
    )

    with left_column:
        left_column_html = (
            '<div class="cage-card">'
            '<div class="cage-card-title">Decision Proof</div>'
            f"{decision_rows}"
            "</div>"
            '<div class="cage-card cage-stacked-card">'
            '<div class="cage-card-title">Evidence</div>'
            f"{evidence_rows}"
            "</div>"
        )

        st.markdown(
            left_column_html,
            unsafe_allow_html=True,
        )

    with right_column:
        right_column_html = (
            '<div class="cage-card">'
            '<div class="cage-card-title">Effect Proof</div>'
            f"{effect_rows}"
            "</div>"
            f"{integrity_card_html(warrant)}"
        )

        st.markdown(
            right_column_html,
            unsafe_allow_html=True,
        )

    parent_id = str(
        warrant.get("replay_of_receipt_id")
        or ""
    )

    children = replay_children(
        selected_id,
        receipts,
    )

    if parent_id or children:
        st.markdown(
            '<div class="cage-section-title">'
            "Replay chain"
            "</div>",
            unsafe_allow_html=True,
        )

        if parent_id and parent_id in warrants:
            parent = warrants[parent_id]

            st.write(
                f"Original Warrant `{parent_id}` "
                f"({display_status(boundary_outcome(parent))}) "
                f"{REPLAY_ARROW} "
                f"Replay Warrant `{selected_id}` "
                f"({display_status(outcome)})"
            )

        elif children:
            child = sorted_receipts(children)[0]
            child_id = str(child.get("receipt_id"))

            st.write(
                f"Original Warrant `{selected_id}` "
                f"({display_status(outcome)}) "
                f"{REPLAY_ARROW} "
                f"Replay Warrant `{child_id}` "
                f"({display_status(boundary_outcome(child))})"
            )

    download_data = {
        "artifact_name": "CAGE Warrant",
        "warrant": warrant,
        "effect": effect,
    }

    st.download_button(
        "Download Warrant JSON",
        data=json.dumps(
            download_data,
            indent=2,
            sort_keys=True,
        ),
        file_name=f"{selected_id}.json",
        mime="application/json",
        use_container_width=True,
    )

    with st.expander("Raw Warrant JSON"):
        st.json(warrant)

        st.markdown("**Effect record**")
        st.json(effect)