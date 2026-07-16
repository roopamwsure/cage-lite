from __future__ import annotations

import streamlit as st


def stack_card(
    title: str,
    description: str,
    tone: str = "",
) -> str:
    css_class = f" {tone}" if tone else ""

    return (
        f'<div class="cage-stack-card{css_class}">'
        f'<div class="cage-card-title">{title}</div>'
        f'<div class="cage-small">{description}</div>'
        "</div>"
    )


def render() -> None:
    st.markdown(
        '<div class="cage-page-title">Where CAGE Fits</div>'
        '<div class="cage-page-subtitle">'
        "CAGE sits between runtime governance and the "
        "business consequence boundary."
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cage-card blue">'
        '<div class="cage-kicker">CAGE positioning</div>'
        '<div class="cage-card-title" '
        'style="font-size:1.05rem;">'
        "Agent platforms govern how agents run. "
        "CAGE governs whether agent actions are allowed "
        "to become business consequences."
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cage-section-title">'
        "AI-agent stack"
        "</div>",
        unsafe_allow_html=True,
    )

    columns = st.columns(
        6,
        gap="small",
    )

    cards = [
        stack_card(
            "Model / LLM",
            "Reasoning and generation.",
        ),
        stack_card(
            "Agent Framework",
            "Planning, orchestration, memory, and workflows.",
        ),
        stack_card(
            "Tools and Protocols",
            "MCP, A2A, APIs, databases, and enterprise systems.",
        ),
        stack_card(
            "Runtime Governance",
            "IAM, guardrails, gateways, policy engines, "
            "and observability.",
        ),
        stack_card(
            "CAGE Prebind Assurance",
            "Standing, policy, approval, boundary decision, "
            "Effect Gate, and proof.",
            "cage",
        ),
        stack_card(
            "Business Consequence",
            "Payment, entitlement, disclosure, approval, "
            "or record update.",
            "boundary",
        ),
    ]

    for column, card in zip(columns, cards):
        with column:
            st.markdown(
                card,
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="cage-section-title">'
        "Different control questions"
        "</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns(
        2,
        gap="medium",
    )

    with left:
        st.markdown(
            '<div class="cage-card">'
            '<div class="cage-kicker">'
            "Runtime governance asks"
            "</div>"
            '<div class="cage-card-title" '
            'style="font-size:0.98rem;">'
            "Can the agent run and invoke this capability?"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            '<div class="cage-card blue">'
            '<div class="cage-kicker">'
            "CAGE asks"
            "</div>"
            '<div class="cage-card-title" '
            'style="font-size:0.98rem;">'
            "May this proposed action become binding?"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="cage-section-title">'
        "How CAGE provides assurance"
        "</div>",
        unsafe_allow_html=True,
    )

    before_binding, after_decision = st.columns(
        2,
        gap="medium",
    )

    with before_binding:
        st.markdown(
            '<div class="cage-card">'
            '<div class="cage-kicker">Before binding</div>'
            '<div class="cage-card-title">'
            "CAGE evaluates whether the action may proceed."
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
- Agent standing
- Policy requirements
- Approval state
- Boundary decision
            """
        )

    with after_decision:
        st.markdown(
            '<div class="cage-card blue">'
            '<div class="cage-kicker">After the decision</div>'
            '<div class="cage-card-title">'
            "CAGE records what happened at the consequence boundary."
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
- Effect disposition
- Tool execution status
- System-of-record outcome
- CAGE Warrant
- Linked replay
            """
        )

    st.info(
        "CAGE uses identity, policy, approval, and runtime signals "
        "to decide whether an action may cross the business "
        "consequence boundary. It then records proof of the result."
    )