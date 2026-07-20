from __future__ import annotations

import streamlit as st


def render_styles() -> None:
    st.markdown(
        """
<style>
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1420px;
    padding-top: 1.6rem;
    padding-bottom: 2rem;
}

[data-testid="stVerticalBlock"] {
    gap: 0.55rem;
}

/* General typography */
.stApp,
.stApp button,
.stApp input,
.stApp textarea,
.stApp select {
    font-family: "Segoe UI", Arial, sans-serif;
}

/* Active navigation button */
[data-testid="stBaseButton-primary"],
button[kind="primary"] {
    background: #0b2f57 !important;
    border-color: #0b2f57 !important;
    color: #ffffff !important;
}

[data-testid="stBaseButton-primary"]:hover,
button[kind="primary"]:hover {
    background: #082541 !important;
    border-color: #082541 !important;
}

/* Page headings */
.cage-page-title {
    color: #101828;
    font-size: 1.25rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-top: 0.65rem;
}

.cage-page-subtitle {
    color: #667085;
    font-size: 0.86rem;
    margin-top: 0.15rem;
    margin-bottom: 0.65rem;
}

/* General cards */
.cage-card {
    border: 1px solid #d8dee8;
    border-radius: 16px;
    background: #ffffff;
    padding: 0.85rem;
    box-shadow: 0 7px 20px rgba(16, 24, 40, 0.035);
}

.cage-stacked-card {
    margin-top: 0.85rem;
}

.cage-card.warn {
    border-color: #fedf89;
    background: #fffcf5;
}

.cage-card.good {
    border-color: #a6f4c5;
    background: #f6fef9;
}

.cage-card.blue {
    border-color: #b2ccff;
    background: #eff4ff;
}

.cage-card-title {
    color: #101828;
    font-size: 0.9rem;
    font-weight: 800;
    margin-bottom: 0.45rem;
}

.cage-kicker {
    color: #0b6b47;
    font-size: 0.66rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

/* Status badges */
.cage-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 999px;
    padding: 0.22rem 0.55rem;
    border: 1px solid transparent;
    font-size: 0.66rem;
    font-weight: 800;
    line-height: 1;
    white-space: nowrap;
}

.cage-badge.good {
    color: #067647;
    background: #ecfdf3;
    border-color: #a6f4c5;
}

.cage-badge.warn {
    color: #b54708;
    background: #fffaeb;
    border-color: #fedf89;
}

.cage-badge.bad {
    color: #b42318;
    background: #fef3f2;
    border-color: #fecdca;
}

.cage-badge.neutral {
    color: #344054;
    background: #f2f4f7;
    border-color: #e4e7ec;
}

/* Warrant details */
.cage-detail-row {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding: 0.4rem 0;
    border-bottom: 1px solid #f0f2f5;
    font-size: 0.78rem;
}

.cage-detail-row:last-child {
    border-bottom: 0;
}

.cage-detail-label {
    color: #667085;
    font-weight: 700;
}

.cage-detail-value {
    color: #101828;
    font-weight: 800;
    text-align: right;
    word-break: break-word;
}
.cage-integrity-card .cage-detail-row {
    align-items: center;
}

.cage-hash-field {
    padding: 0.55rem 0;
    border-top: 1px solid #f0f2f5;
}

.cage-hash-label {
    color: #667085;
    font-size: 0.72rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}

.cage-hash-value {
    color: #101828;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
        "Liberation Mono", "Courier New", monospace;
    font-size: 0.67rem;
    font-weight: 650;
    line-height: 1.45;
    overflow-wrap: anywhere;
    word-break: break-word;
}

.cage-integrity-detail {
    margin-top: 0.45rem;
    padding: 0.55rem 0.65rem;
    border-radius: 10px;
    background: #f8fafc;
    color: #344054;
    font-size: 0.72rem;
    font-weight: 650;
    line-height: 1.4;
}

.cage-integrity-note {
    margin-top: 0.55rem;
    color: #667085;
    font-size: 0.68rem;
    line-height: 1.45;
}

/* Consequence-boundary flow */
.cage-flow-card {
    border: 1px solid #d8dee8;
    border-radius: 15px;
    background: #ffffff;
    padding: 0.72rem 0.62rem;
    min-height: 112px;
}

.cage-flow-card.warn {
    border-color: #fedf89;
    background: #fffcf5;
}

.cage-flow-card.blue {
    border-color: #b2ccff;
    background: #eff4ff;
}

.cage-flow-label {
    color: #667085;
    font-size: 0.61rem;
    font-weight: 800;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}

.cage-flow-value {
    color: #101828;
    font-size: 0.86rem;
    font-weight: 800;
    line-height: 1.15;
    margin-top: 0.28rem;
}

.cage-flow-detail {
    color: #667085;
    font-size: 0.67rem;
    line-height: 1.25;
    margin-top: 0.22rem;
}

/* Section headings and tables */
.cage-section-title {
    color: #101828;
    font-size: 0.95rem;
    font-weight: 800;
    margin-top: 0.9rem;
    margin-bottom: 0.4rem;
}

.cage-table-header {
    color: #667085;
    font-size: 0.66rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.cage-small {
    color: #667085;
    font-size: 0.72rem;
    line-height: 1.4;
}

.cage-warrant-id {
    color: #101828;
    font-size: 1.02rem;
    font-weight: 800;
    word-break: break-all;
}

/* Replay text */
.cage-replay-note {
    color: #667085;
    font-size: 0.78rem;
    line-height: 1.4;
    margin-top: 0.65rem;
    margin-bottom: 0.55rem;
}

/* Architecture page */
.cage-stack-card {
    border: 1px solid #d8dee8;
    border-radius: 15px;
    background: #ffffff;
    padding: 0.7rem;
    min-height: 112px;
}

.cage-stack-card.cage {
    border-color: #b2ccff;
    background: #eff4ff;
}

.cage-stack-card.boundary {
    border-color: #a6f4c5;
    background: #f6fef9;
}
</style>
        """,
        unsafe_allow_html=True,
    )