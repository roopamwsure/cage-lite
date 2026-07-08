import json
from pathlib import Path

import streamlit as st

from cage_lite.demo.payment_replay import run_replay_demo


DEFAULT_DEMO_DIR = Path("playground/v04-replay-demo")


def main():
    st.set_page_config(
        page_title="CAGE-lite v0.4",
        page_icon="🧾",
        layout="wide",
    )

    demo_dir = sidebar()
    summary_path = demo_dir / "demo_summary.json"

    st.title("CAGE-lite v0.4")
    st.caption(
        "Prebind assurance for AI-agent actions at the business consequence boundary."
    )

    if not summary_path.exists():
        st.info("Generate the replay demo from the sidebar to view the dashboard.")
        return

    summary = read_json(summary_path)

    render_assurance_banner(summary)
    render_hero(summary)
    render_boundary_path(summary)
    render_no_bind_proof(summary)
    render_replay(summary)
    render_receipts(summary, demo_dir)


def sidebar() -> Path:
    with st.sidebar:
        st.header("CAGE-lite demo")

        demo_dir_text = st.text_input(
            "Demo output folder",
            value=str(DEFAULT_DEMO_DIR),
        )

        demo_dir = Path(demo_dir_text)

        if st.button("Generate replay demo", use_container_width=True):
            run_replay_demo(demo_dir)
            st.success("Demo generated.")

        st.divider()
        st.caption("Reads local file")
        st.code(str(demo_dir / "demo_summary.json"))

    return demo_dir


def render_assurance_banner(summary: dict):
    held = summary["held"]

    if no_bind_verified(held):
        st.success("Prebind Assurance: NO-BIND VERIFIED")
    else:
        st.warning("Prebind Assurance: check required")


def render_hero(summary: dict):
    held = summary["held"]

    amount = f"{summary['amount']:,} {summary['currency']}"

    with st.container(border=True):
        st.caption("Flagship scenario")
        st.header(f"{amount} vendor payment was held before it could bind")

        st.write(
            "CAGE evaluated the finance agent's payment action before it became "
            "a business consequence. Approval was missing, so the action was held. "
            "The protected payment API did not execute and the system of record was not written."
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Boundary outcome", held["boundary_outcome"].upper())
        col2.metric("Effect disposition", held["effect_disposition"])
        col3.metric("Payment API executed", str(held["effect_executed"]))
        col4.metric("System of record", held["system_of_record_status"])


def render_boundary_path(summary: dict):
    held = summary["held"]

    st.subheader("Boundary path")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        step_card(
            "1",
            "Attempted action",
            f"{summary['amount']:,} {summary['currency']} vendor payment",
            "received",
        )

    with col2:
        step_card(
            "2",
            "Standing check",
            f"agent limit is {summary['standing_limit']:,} {summary['currency']}",
            "exceeded",
        )

    with col3:
        approval_status = "present" if held["approval_present"] else "missing"
        step_card(
            "3",
            "Approval check",
            f"approval {approval_status}",
            "blocked",
        )

    with col4:
        step_card(
            "4",
            "Boundary decision",
            held["boundary_outcome"],
            "held",
        )


def render_no_bind_proof(summary: dict):
    held = summary["held"]

    st.subheader("No-bind proof")

    st.write(
        "The receipt proves that the first attempt did not bind. "
        "These are the four checks CAGE-lite v0.4 exposes for the demo."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        proof_check(
            "Boundary held",
            held["boundary_outcome"] == "held",
            held["boundary_outcome"],
        )

    with col2:
        proof_check(
            "Effect did not bind",
            held["effect_disposition"] == "no_bind",
            held["effect_disposition"],
        )

    with col3:
        proof_check(
            "Payment API blocked",
            held["effect_executed"] is False,
            "not executed",
        )

    with col4:
        proof_check(
            "System not written",
            held["system_of_record_status"] == "not_written",
            held["system_of_record_status"],
        )

    rows = [
        {
            "Check": "Boundary outcome",
            "Expected": "held",
            "Actual": held["boundary_outcome"],
            "Pass": held["boundary_outcome"] == "held",
        },
        {
            "Check": "Effect disposition",
            "Expected": "no_bind",
            "Actual": held["effect_disposition"],
            "Pass": held["effect_disposition"] == "no_bind",
        },
        {
            "Check": "Payment API executed",
            "Expected": "False",
            "Actual": str(held["effect_executed"]),
            "Pass": held["effect_executed"] is False,
        },
        {
            "Check": "System of record",
            "Expected": "not_written",
            "Actual": held["system_of_record_status"],
            "Pass": held["system_of_record_status"] == "not_written",
        },
    ]

    st.table(rows)


def render_replay(summary: dict):
    held = summary["held"]
    replay = summary["replay"]

    st.subheader("Replay after approval")

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            st.markdown("### Initial attempt")
            st.caption("Approval missing")

            st.metric("Boundary outcome", held["boundary_outcome"])
            st.metric("Effect disposition", held["effect_disposition"])
            st.metric("System of record", held["system_of_record_status"])

            st.write("Receipt")
            st.code(held["receipt_id"])

    with right:
        with st.container(border=True):
            st.markdown("### Replay attempt")
            st.caption("Approval present")

            st.metric("Boundary outcome", replay["boundary_outcome"])
            st.metric("Effect disposition", replay["effect_disposition"])
            st.metric("System of record", replay["system_of_record_status"])

            st.write("Replay of")
            st.code(replay["replay_of_receipt_id"])

    if replay["replay_of_receipt_id"] == held["receipt_id"]:
        st.success("Replay receipt links back to the original held receipt.")
    else:
        st.error("Replay receipt does not link back to the original held receipt.")


def render_receipts(summary: dict, demo_dir: Path):
    held = summary["held"]
    replay = summary["replay"]

    st.subheader("Receipt evidence")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("### Held receipt")
            st.code(held["receipt_id"])
            st.caption(f"digest: {short_digest(held['digest'])}")

            held_path = demo_dir / "receipts" / f"{held['receipt_id']}.json"
            download_receipt("Download held receipt", held_path)

    with col2:
        with st.container(border=True):
            st.markdown("### Replay receipt")
            st.code(replay["receipt_id"])
            st.caption(f"replay_of_receipt_id: {replay['replay_of_receipt_id']}")

            replay_path = demo_dir / "receipts" / f"{replay['receipt_id']}.json"
            download_receipt("Download replay receipt", replay_path)

    with st.expander("Show receipt fields"):
        left, right = st.columns(2)

        with left:
            st.markdown("#### Held")
            st.json(important_fields(held))

        with right:
            st.markdown("#### Replay")
            st.json(important_fields(replay))

    with st.expander("Show raw demo summary"):
        st.json(summary)


def step_card(number: str, title: str, body: str, status: str):
    with st.container(border=True):
        st.caption(f"Step {number}")
        st.markdown(f"**{title}**")
        st.write(body)
        st.code(status)


def proof_check(title: str, passed: bool, value: str):
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.metric("Observed", value)

        if passed:
            st.success("pass")
        else:
            st.error("fail")


def important_fields(receipt: dict) -> dict:
    return {
        "receipt_id": receipt["receipt_id"],
        "action_id": receipt["action_id"],
        "movement_id": receipt["movement_id"],
        "replay_of_receipt_id": receipt["replay_of_receipt_id"],
        "approval_required": receipt["approval_required"],
        "approval_present": receipt["approval_present"],
        "approval_ref": receipt["approval_ref"],
        "boundary_outcome": receipt["boundary_outcome"],
        "effect_id": receipt["effect_id"],
        "effect_disposition": receipt["effect_disposition"],
        "effect_executed": receipt["effect_executed"],
        "system_of_record_status": receipt["system_of_record_status"],
        "digest": receipt["digest"],
    }


def download_receipt(label: str, path: Path):
    if not path.exists():
        st.warning("Receipt file not found.")
        return

    st.download_button(
        label,
        data=path.read_text(encoding="utf-8"),
        file_name=path.name,
        mime="application/json",
        use_container_width=True,
    )


def no_bind_verified(receipt: dict) -> bool:
    return (
        receipt["boundary_outcome"] == "held"
        and receipt["effect_disposition"] == "no_bind"
        and receipt["effect_executed"] is False
        and receipt["system_of_record_status"] == "not_written"
    )


def short_digest(digest: str) -> str:
    return f"{digest[:18]}..."


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()