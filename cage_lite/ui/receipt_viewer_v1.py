from __future__ import annotations

import base64
import html
import json
from pathlib import Path
from typing import Any

import streamlit as st


st.set_page_config(
    page_title="CAGE-lite Warrant Dashboard",
    page_icon="🛡️",
    layout="wide",
)


DEFAULT_ARTIFACT_DIR = "playground/v04-replay-demo"
LOGO_PATH = Path(__file__).parent / "assets" / "cage_logo.png"


def esc(value: Any) -> str:
    if value is None:
        return "—"
    return html.escape(str(value))


def lower(value: Any) -> str:
    return str(value or "").strip().lower()


def money(amount: Any, currency: Any = "USD") -> str:
    if amount is None:
        return "—"

    try:
        number = float(amount)
        amount_text = f"{int(number):,}" if number.is_integer() else f"{number:,.2f}"
    except Exception:
        amount_text = str(amount)

    return f"{amount_text} {currency or ''}".strip()


def yes_no(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"

    text = lower(value)

    if text in {"true", "yes", "y", "1", "present"}:
        return "yes"

    if text in {"false", "no", "n", "0", "missing", "none"}:
        return "no"

    return str(value or "—")


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    return lower(value) in {"true", "yes", "y", "1", "executed", "written", "bound"}


def read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def read_json_folder(folder: Path) -> list[dict[str, Any]]:
    if not folder.exists():
        return []

    items: list[dict[str, Any]] = []

    for path in sorted(folder.glob("*.json")):
        data = read_json(path)
        if data:
            data["_file_name"] = path.name
            items.append(data)

    return sorted(
        items,
        key=lambda item: (
            str(item.get("created_at", "")),
            str(item.get("attempt_id", "")),
            str(item.get("receipt_id", "")),
        ),
    )


def load_artifacts(root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    summary = read_json(root / "demo_summary.json")
    receipts = read_json_folder(root / "receipts")
    effects = read_json_folder(root / "effects")
    return summary, receipts, effects


def receipt_outcome(receipt: dict[str, Any]) -> str:
    return lower(receipt.get("boundary_outcome") or receipt.get("outcome"))


def effect_disposition(effect: dict[str, Any]) -> str:
    return str(effect.get("effect_disposition") or effect.get("disposition") or "—")


def system_status(effect: dict[str, Any], receipt: dict[str, Any]) -> str:
    return str(
        receipt.get("system_of_record_status")
        or effect.get("system_of_record_status")
        or "—"
    )


def effect_executed(effect: dict[str, Any], receipt: dict[str, Any]) -> bool:
    if "effect_executed" in receipt:
        return as_bool(receipt.get("effect_executed"))

    if "executed" in effect:
        return as_bool(effect.get("executed"))

    if "effect_executed" in effect:
        return as_bool(effect.get("effect_executed"))

    return False


def find_effect(receipt: dict[str, Any], effects: list[dict[str, Any]]) -> dict[str, Any]:
    effect_id = receipt.get("effect_id")

    if effect_id:
        for effect in effects:
            if effect.get("effect_id") == effect_id:
                return effect

    attempt_id = receipt.get("attempt_id")
    action_id = receipt.get("action_id")

    for effect in effects:
        if attempt_id and effect.get("attempt_id") == attempt_id:
            return effect

        if action_id and effect.get("action_id") == action_id:
            return effect

    return {}


def latest_demo_pair(receipts: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    by_id = {
        str(receipt.get("receipt_id")): receipt
        for receipt in receipts
        if receipt.get("receipt_id")
    }

    admitted_replays = [
        receipt
        for receipt in receipts
        if receipt_outcome(receipt) == "admitted" and receipt.get("replay_of_receipt_id")
    ]

    if admitted_replays:
        admitted = admitted_replays[-1]
        held = by_id.get(str(admitted.get("replay_of_receipt_id")), {})
        if held:
            return held, admitted

    held_items = [receipt for receipt in receipts if receipt_outcome(receipt) == "held"]
    admitted_items = [receipt for receipt in receipts if receipt_outcome(receipt) == "admitted"]

    held = held_items[-1] if held_items else {}
    admitted = admitted_items[-1] if admitted_items else {}

    return held, admitted


def tone(value: Any) -> str:
    text = lower(value)

    if text in {"admitted", "bound", "written", "executed", "linked", "yes", "verified", "passed"}:
        return "good"

    if text in {"held", "no_bind", "not_written", "not executed", "blocked", "missing", "no"}:
        return "warn"

    if text in {"failed", "denied", "error", "not linked"}:
        return "bad"

    return "neutral"


def tag(value: Any, forced_tone: str | None = None) -> str:
    css = forced_tone or tone(value)
    return f'<span class="tag {css}">{esc(value)}</span>'


def html_block(markup: str) -> None:
    st.markdown(markup, unsafe_allow_html=True)


def logo_html() -> str:
    if LOGO_PATH.exists():
        encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
        return (
            '<div class="logo-card">'
            f'<img src="data:image/png;base64,{encoded}" class="logo-img" />'
            '</div>'
        )

    return '<div class="logo-fallback">C</div>'


def warrant_bundle(
    summary: dict[str, Any],
    held: dict[str, Any],
    admitted: dict[str, Any],
    held_effect: dict[str, Any],
    admitted_effect: dict[str, Any],
) -> str:
    bundle = {
        "artifact_name": "CAGE Warrant Bundle",
        "summary": summary,
        "held_warrant": held,
        "replay_warrant": admitted,
        "held_effect": held_effect,
        "replay_effect": admitted_effect,
    }

    return json.dumps(bundle, indent=2, sort_keys=True)


def render_css() -> None:
    st.markdown(
        """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.block-container {
    padding-top: 2.45rem;
    padding-bottom: 1.3rem;
    max-width: 1380px;
}

[data-testid="stVerticalBlock"] {
    gap: 0.5rem;
}

.cage-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.55rem;
}

.brand {
    display: flex;
    align-items: center;
    gap: 0.9rem;
}

.logo-card {
    width: 82px;
    height: 82px;
    border: 1px solid #e4e7ec;
    border-radius: 21px;
    background: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    box-shadow: 0 12px 26px rgba(16, 24, 40, 0.08);
}

.logo-img {
    width: 78px;
    height: 78px;
    object-fit: contain;
}

.logo-fallback {
    width: 64px;
    height: 64px;
    border-radius: 18px;
    background: #082a55;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    font-weight: 950;
    position: relative;
}

.logo-fallback:after {
    content: "✓";
    width: 23px;
    height: 23px;
    border-radius: 999px;
    background: #16a34a;
    border: 3px solid white;
    color: white;
    font-size: 0.78rem;
    font-weight: 950;
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    right: -6px;
    bottom: -6px;
}

.brand-title {
    color: #101828;
    font-size: 2.05rem;
    font-weight: 950;
    line-height: 1;
    letter-spacing: -0.06em;
}

.brand-subtitle {
    margin-top: 0.25rem;
    color: #475467;
    font-size: 0.96rem;
}

.success-banner {
    border: 1px solid #86efac;
    border-radius: 19px;
    background: linear-gradient(90deg, #dcfce7 0%, #ecfdf3 100%);
    color: #066033;
    padding: 0.78rem 0.95rem;
    font-size: 1.13rem;
    font-weight: 950;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.75rem;
}

.banner-icon {
    width: 33px;
    height: 33px;
    border-radius: 999px;
    background: #16a34a;
    color: white;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.12rem;
    font-weight: 950;
}

.dashboard {
    border: 1px solid #d0d5dd;
    border-radius: 25px;
    background:
        radial-gradient(circle at top right, rgba(22, 136, 63, 0.12), transparent 25%),
        linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    padding: 1rem;
    box-shadow: 0 16px 42px rgba(16, 24, 40, 0.075);
}

.hero-grid {
    display: grid;
    grid-template-columns: 1.2fr 0.8fr;
    gap: 0.9rem;
    align-items: stretch;
}

.hero {
    border: 1px solid #a6f4c5;
    border-radius: 23px;
    background: #ecfdf3;
    padding: 1.1rem;
}

.hero-kicker {
    color: #067647;
    font-size: 0.78rem;
    font-weight: 950;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.4rem;
}

.hero-title {
    color: #101828;
    font-size: 2.75rem;
    font-weight: 980;
    line-height: 1.01;
    letter-spacing: -0.075em;
    max-width: 880px;
    margin-bottom: 0.75rem;
}

.hero-text {
    color: #475467;
    font-size: 1rem;
    line-height: 1.38;
    max-width: 820px;
}

.proof-summary {
    display: grid;
    grid-template-columns: 1fr;
    gap: 0.55rem;
}

.proof-row {
    border: 1px solid #fedf89;
    border-radius: 17px;
    background: #fffcf5;
    padding: 0.72rem 0.78rem;
    display: grid;
    grid-template-columns: 36px 1fr auto;
    gap: 0.62rem;
    align-items: center;
}

.proof-icon {
    width: 36px;
    height: 36px;
    border-radius: 13px;
    background: #fff7ed;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.08rem;
}

.proof-label {
    color: #667085;
    font-size: 0.68rem;
    font-weight: 950;
    text-transform: uppercase;
    letter-spacing: 0.075em;
    margin-bottom: 0.12rem;
}

.proof-detail {
    color: #101828;
    font-size: 0.94rem;
    font-weight: 850;
    line-height: 1.22;
}

.chain-title,
.compare-title {
    color: #101828;
    font-size: 1rem;
    font-weight: 950;
    margin-top: 1.05rem;
    margin-bottom: 0.5rem;
}

.chain {
    display: grid;
    grid-template-columns: repeat(7, minmax(0, 1fr));
    gap: 0.52rem;
    position: relative;
}

.step {
    border: 1px solid #e4e7ec;
    border-radius: 18px;
    background: white;
    padding: 0.78rem 0.62rem;
    min-height: 123px;
    position: relative;
    box-shadow: 0 10px 24px rgba(16, 24, 40, 0.04);
}

.step:not(:last-child):after {
    content: "➜";
    position: absolute;
    right: -0.53rem;
    top: 50%;
    transform: translateY(-50%);
    color: #64748b;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    width: 23px;
    height: 23px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.82rem;
    font-weight: 950;
    z-index: 4;
}

.step.good {
    border-color: #a6f4c5;
    background: #f6fef9;
}

.step.warn {
    border-color: #fedf89;
    background: #fffcf5;
}

.step.blue {
    border-color: #b2ccff;
    background: #eff4ff;
}

.step-icon {
    font-size: 1.28rem;
    margin-bottom: 0.34rem;
}

.step-label {
    color: #667085;
    font-size: 0.64rem;
    font-weight: 950;
    letter-spacing: 0.075em;
    text-transform: uppercase;
    margin-bottom: 0.18rem;
}

.step-value {
    color: #101828;
    font-size: 1.02rem;
    font-weight: 950;
    line-height: 1.08;
}

.step-detail {
    color: #667085;
    font-size: 0.71rem;
    line-height: 1.18;
    margin-top: 0.22rem;
}

.compare {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.compare-card {
    border: 1px solid #e4e7ec;
    border-radius: 19px;
    background: white;
    padding: 0.88rem;
}

.compare-card.before {
    border-color: #fedf89;
    background: #fffcf5;
}

.compare-card.after {
    border-color: #a6f4c5;
    background: #f6fef9;
}

.compare-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.7rem;
    color: #101828;
    font-size: 1.05rem;
    font-weight: 950;
    margin-bottom: 0.55rem;
}

.status-line {
    display: flex;
    flex-wrap: wrap;
    gap: 0.38rem;
    margin-bottom: 0.55rem;
}

.compare-note {
    color: #475467;
    font-size: 0.9rem;
    line-height: 1.35;
}

.warrant-link {
    border: 1px solid #a6f4c5;
    background: #f6fef9;
    border-radius: 18px;
    margin-top: 0.75rem;
    padding: 0.78rem 0.9rem;
}

.warrant-link-title {
    color: #101828;
    font-size: 0.95rem;
    font-weight: 950;
    margin-bottom: 0.35rem;
}

.warrant-id-line {
    color: #475467;
    font-size: 0.82rem;
    line-height: 1.4;
    word-break: break-all;
}

.warrant-id-line strong {
    color: #101828;
    font-weight: 950;
}

.diff-note {
    border: 1px solid #bfdbfe;
    background: #eff6ff;
    border-radius: 18px;
    padding: 0.82rem 0.9rem;
    margin-top: 0.8rem;
    display: grid;
    grid-template-columns: 36px 1fr;
    gap: 0.7rem;
    align-items: start;
}

.diff-icon {
    width: 36px;
    height: 36px;
    border-radius: 13px;
    background: #dbeafe;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}

.diff-title {
    color: #101828;
    font-size: 0.95rem;
    font-weight: 950;
    margin-bottom: 0.15rem;
}

.diff-text {
    color: #475467;
    font-size: 0.86rem;
    line-height: 1.35;
}

.tag {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 0.22rem 0.55rem;
    font-size: 0.72rem;
    font-weight: 950;
    border: 1px solid transparent;
    white-space: nowrap;
}

.tag.good {
    color: #067647;
    background: #ecfdf3;
    border-color: #a6f4c5;
}

.tag.warn {
    color: #b54708;
    background: #fffaeb;
    border-color: #fedf89;
}

.tag.bad {
    color: #b42318;
    background: #fef3f2;
    border-color: #fecdca;
}

.tag.neutral {
    color: #344054;
    background: #f2f4f7;
    border-color: #e4e7ec;
}

.detail-panel {
    margin-top: 0.7rem;
}

.detail-line {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    border-bottom: 1px solid #f2f4f7;
    padding: 0.38rem 0;
    font-size: 0.84rem;
}

.detail-key {
    color: #667085;
    font-weight: 850;
}

.detail-value {
    color: #101828;
    text-align: right;
    font-weight: 850;
    word-break: break-all;
}

.demo-controls {
    margin-top: 0.7rem;
}

.demo-controls [data-testid="stTextInput"] input {
    min-height: 40px;
}

.demo-controls button {
    min-height: 40px;
}

@media (max-width: 1120px) {
    .hero-grid {
        grid-template-columns: 1fr;
    }

    .chain {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .step:not(:last-child):after {
        content: "";
    }

    .compare {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 720px) {
    .block-container {
        padding-top: 2rem;
    }

    .cage-header {
        align-items: flex-start;
        flex-direction: column;
    }

    .hero-title {
        font-size: 1.75rem;
    }

    .chain {
        grid-template-columns: 1fr;
    }

    .proof-row {
        grid-template-columns: 34px 1fr;
    }

    .proof-row .tag {
        grid-column: 2;
        width: fit-content;
    }
}
</style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------
# UI components
# -----------------------------

def render_header() -> None:
    html_block(
        '<div class="cage-header">'
        '<div class="brand">'
        f'{logo_html()}'
        '<div>'
        '<div class="brand-title">CAGE-lite</div>'
        '<div class="brand-subtitle">'
        'Prebind assurance for AI-agent actions at the '
        'business consequence boundary.'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )


def proof_row(icon: str, label: str, detail: str, value: Any) -> str:
    return (
        '<div class="proof-row">'
        f'<div class="proof-icon">{esc(icon)}</div>'
        '<div>'
        f'<div class="proof-label">{esc(label)}</div>'
        f'<div class="proof-detail">{esc(detail)}</div>'
        '</div>'
        f'<div>{tag(value)}</div>'
        '</div>'
    )


def step_card(icon: str, label: str, value: Any, detail: str, css: str) -> str:
    return (
        f'<div class="step {css}">'
        f'<div class="step-icon">{esc(icon)}</div>'
        f'<div class="step-label">{esc(label)}</div>'
        f'<div class="step-value">{esc(value)}</div>'
        f'<div class="step-detail">{esc(detail)}</div>'
        '</div>'
    )


def compare_card(
    title: str,
    css: str,
    badge: str,
    status_tags: list[Any],
    note: str,
) -> str:
    statuses = ''.join(tag(item) for item in status_tags)

    return (
        f'<div class="compare-card {css}">'
        '<div class="compare-head">'
        f'<div>{esc(title)}</div>'
        f'{tag(badge)}'
        '</div>'
        f'<div class="status-line">{statuses}</div>'
        f'<div class="compare-note">{esc(note)}</div>'
        '</div>'
    )


def detail_line(key: str, value: Any) -> str:
    return (
        '<div class="detail-line">'
        f'<div class="detail-key">{esc(key)}</div>'
        f'<div class="detail-value">{esc(value)}</div>'
        '</div>'
    )


def render_dashboard(
    held: dict[str, Any],
    admitted: dict[str, Any],
    held_effect: dict[str, Any],
    admitted_effect: dict[str, Any],
) -> None:
    amount_text = money(held.get("amount"), held.get("currency", "USD"))
    standing_limit = money(held.get("standing_limit"), held.get("currency", "USD"))

    held_boundary = held.get("boundary_outcome") or held.get("outcome") or "—"
    held_reason = held.get("boundary_reason") or held.get("reason") or "Standing exceeded and approval missing."
    held_disposition = held.get("effect_disposition") or effect_disposition(held_effect)
    held_system = system_status(held_effect, held)
    held_api = "executed" if effect_executed(held_effect, held) else "not executed"

    admitted_boundary = admitted.get("boundary_outcome") or admitted.get("outcome") or "—"
    admitted_disposition = admitted.get("effect_disposition") or effect_disposition(admitted_effect)
    admitted_system = system_status(admitted_effect, admitted)

    held_id = held.get("receipt_id")
    admitted_id = admitted.get("receipt_id")
    replay_of = admitted.get("replay_of_receipt_id")
    linked = bool(replay_of and held_id and replay_of == held_id)

    proof = (
        proof_row("🧭", "Boundary decision", held_reason, held_boundary)
        + proof_row("⛔", "Effect gate", "Protected payment effect did not bind.", held_disposition)
        + proof_row("🔌", "Payment API", "Protected payment call was blocked.", held_api)
        + proof_row("🗄️", "System of record", "No durable payment write occurred.", held_system)
    )

    chain = (
        step_card("💸", "Payment", amount_text, "agent requested payment", "blue")
        + step_card("📏", "Standing", "exceeded", f"limit {standing_limit}", "warn")
        + step_card("🧾", "Approval", "missing", f"required: {yes_no(held.get('approval_required'))}", "warn")
        + step_card("🛡️", "Boundary", held_boundary, "held before bind", "warn")
        + step_card("⛔", "Effect", held_disposition, "no protected effect", "warn")
        + step_card("🔌", "API", "blocked", "payment call stopped", "warn")
        + step_card("🗄️", "System", held_system, "record stayed clean", "warn")
    )

    replay = (
        compare_card(
            "Initial attempt",
            "before",
            "blocked",
            [held_boundary, held_disposition, held_system],
            "Approval was missing. CAGE held the action and prevented binding.",
        )
        + compare_card(
            "Replay with approval",
            "after",
            "admitted",
            [admitted_boundary, admitted_disposition, admitted_system],
            "Approval was added. The same action replay was admitted and written.",
        )
    )

    html_block(
        '<div class="success-banner">'
        '<span class="banner-icon">✓</span>'
        '<span>PREBIND ASSURANCE: NO-BIND VERIFIED</span>'
        '</div>'
        '<div class="dashboard">'
        '<div class="hero-grid">'
        '<div class="hero">'
        '<div class="hero-kicker">CAGE Warrant</div>'
        f'<div class="hero-title">{esc(amount_text)} vendor payment was held before it could bind.</div>'
        '<div class="hero-text">'
        'CAGE stopped the protected payment effect before business consequence formation. '
        'The payment API was not executed and the system of record was not written.'
        '</div>'
        '</div>'
        f'<div class="proof-summary">{proof}</div>'
        '</div>'
        '<div class="chain-title">Consequence boundary path</div>'
        f'<div class="chain">{chain}</div>'
        '<div class="compare-title">Before / after replay</div>'
        f'<div class="compare">{replay}</div>'
        '<div class="warrant-link">'
        '<div class="warrant-link-title">Warrant linkage</div>'
        f'<div class="warrant-id-line"><strong>Held warrant:</strong> {esc(held_id)}</div>'
        f'<div class="warrant-id-line"><strong>Replay warrant:</strong> {esc(admitted_id)}</div>'
        f'<div class="warrant-id-line"><strong>Replay links to held warrant:</strong> {esc(replay_of)} {tag("linked" if linked else "not linked", "good" if linked else "bad")}</div>'
        '</div>'
        '<div class="diff-note">'
        '<div class="diff-icon">✦</div>'
        '<div>'
        '<div class="diff-title">Why this is different from basic policy enforcement</div>'
        '<div class="diff-text">'
        'A policy engine can say “approval required.” CAGE proves the action did not become binding '
        'until that approval existed: no payment API execution, no system-of-record write, and a linked replay warrant.'
        '</div>'
        '</div>'
        '</div>'
        '</div>'
    )


def render_detail_panel(
    summary: dict[str, Any],
    held: dict[str, Any],
    admitted: dict[str, Any],
    held_effect: dict[str, Any],
    admitted_effect: dict[str, Any],
    receipts: list[dict[str, Any]],
    effects: list[dict[str, Any]],
) -> None:
    st.markdown('<div class="detail-panel">', unsafe_allow_html=True)

    with st.expander("More proof details, raw JSON, and export"):
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Held warrant", "Replay warrant", "Artifacts", "Raw JSON"]
        )

        with tab1:
            html_block(
                detail_line("Warrant ID", held.get("receipt_id"))
                + detail_line("Action ID", held.get("action_id"))
                + detail_line("Amount", money(held.get("amount"), held.get("currency", "USD")))
                + detail_line("Standing limit", money(held.get("standing_limit"), held.get("currency", "USD")))
                + detail_line("Approval present", yes_no(held.get("approval_present")))
                + detail_line("Boundary", held.get("boundary_outcome") or held.get("outcome"))
                + detail_line("Effect", held.get("effect_disposition") or effect_disposition(held_effect))
                + detail_line("System", system_status(held_effect, held))
            )

        with tab2:
            html_block(
                detail_line("Warrant ID", admitted.get("receipt_id"))
                + detail_line("Replay of", admitted.get("replay_of_receipt_id"))
                + detail_line("Approval present", yes_no(admitted.get("approval_present")))
                + detail_line("Approval ref", admitted.get("approval_ref"))
                + detail_line("Boundary", admitted.get("boundary_outcome") or admitted.get("outcome"))
                + detail_line("Effect", admitted.get("effect_disposition") or effect_disposition(admitted_effect))
                + detail_line("System", system_status(admitted_effect, admitted))
            )

        with tab3:
            c1, c2 = st.columns(2)
            c1.metric("Warrants found", len(receipts))
            c2.metric("Effects found", len(effects))

            st.download_button(
                "Download Full Warrant Bundle",
                data=warrant_bundle(summary, held, admitted, held_effect, admitted_effect),
                file_name="cage_warrant_bundle.json",
                mime="application/json",
                use_container_width=True,
            )

        with tab4:
            raw_tab1, raw_tab2, raw_tab3, raw_tab4, raw_tab5 = st.tabs(
                ["Summary", "Held", "Replay", "Held effect", "Replay effect"]
            )

            with raw_tab1:
                st.json(summary or {})
            with raw_tab2:
                st.json(held or {})
            with raw_tab3:
                st.json(admitted or {})
            with raw_tab4:
                st.json(held_effect or {})
            with raw_tab5:
                st.json(admitted_effect or {})

    st.markdown('</div>', unsafe_allow_html=True)


def render_demo_controls() -> Path:
    root = Path(DEFAULT_ARTIFACT_DIR)

    with st.expander("Demo controls"):
        st.markdown('<div class="demo-controls">', unsafe_allow_html=True)

        left, right = st.columns([4, 1.25], vertical_alignment="bottom")

        with left:
            artifact_dir = st.text_input(
                "Artifact folder",
                value=DEFAULT_ARTIFACT_DIR,
            )

        with right:
            generate = st.button("Generate replay demo", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        root = Path(artifact_dir.strip().strip('"'))

        if generate:
            try:
                from cage_lite.demo.payment_replay import run_replay_demo

                run_replay_demo(root)
                st.success(f"Replay demo generated at {root}")
            except Exception as exc:
                st.error(f"Could not generate replay demo: {exc}")

    return root


def render_empty(root: Path) -> None:
    st.info("No warrants were found yet. Open Demo controls and generate the replay demo.")
    st.code(
        "python -m cage_lite.demo.payment_replay\n"
        "streamlit run cage_lite\\ui\\app.py",
        language="powershell",
    )
    st.caption(f"Current artifact folder: {root}")


def main() -> None:
    render_css()
    render_header()

    root = render_demo_controls()

    summary, receipts, effects = load_artifacts(root)

    if not receipts:
        render_empty(root)
        return

    held, admitted = latest_demo_pair(receipts)

    if not held:
        st.warning("Warrant artifacts were found, but no HELD warrant was detected.")
        return

    if not admitted:
        st.warning("HELD warrant found, but no admitted replay warrant was detected.")
        admitted = {}

    held_effect = find_effect(held, effects)
    admitted_effect = find_effect(admitted, effects) if admitted else {}

    render_dashboard(held, admitted, held_effect, admitted_effect)
    render_detail_panel(
        summary,
        held,
        admitted,
        held_effect,
        admitted_effect,
        receipts,
        effects,
    )


if __name__ == "__main__":
    main()