from cage_lite.core.action import ActionRequest
from cage_lite.core.approval import ApprovalRecord
from cage_lite.core.standing import AgentStanding
from cage_lite.policies.payment import evaluate_payment


def payment_standing(agent_id="finance-agent-01"):
    return AgentStanding(
        agent_id=agent_id,
        allowed_actions={"payment"},
        max_payment_amount=50000,
    )


def test_small_payment_is_admitted():
    action = ActionRequest(
        action_id="payment-001",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=25000,
        currency="USD",
    )

    decision = evaluate_payment(action, payment_standing())

    assert decision.outcome == "admitted"


def test_large_payment_without_approval_is_held():
    action = ActionRequest(
        action_id="payment-002",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=75000,
        currency="USD",
    )

    decision = evaluate_payment(action, payment_standing())

    assert decision.outcome == "held"


def test_large_payment_with_valid_approval_is_admitted():
    action = ActionRequest(
        action_id="payment-003",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=75000,
        currency="USD",
    )

    approval = ApprovalRecord.issue(
        action=action,
        approved_by="manager-01",
        approved_amount=75000,
        evidence_ref="approval/payment-003",
    )

    decision = evaluate_payment(
        action=action,
        standing=payment_standing(),
        approval=approval,
    )

    assert decision.outcome == "admitted"


def test_large_payment_with_wrong_approval_is_held():
    action = ActionRequest(
        action_id="payment-004",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=75000,
        currency="USD",
    )

    other_action = ActionRequest(
        action_id="payment-999",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=75000,
        currency="USD",
    )

    approval = ApprovalRecord.issue(
        action=other_action,
        approved_by="manager-01",
        approved_amount=75000,
        evidence_ref="approval/payment-999",
    )

    decision = evaluate_payment(
        action=action,
        standing=payment_standing(),
        approval=approval,
    )

    assert decision.outcome == "held"


def test_agent_without_payment_standing_is_refused():
    action = ActionRequest(
        action_id="payment-005",
        agent_id="support-agent-01",
        action_type="payment",
        amount=1000,
        currency="USD",
    )

    standing = AgentStanding(
        agent_id="support-agent-01",
        allowed_actions={"case_update"},
    )

    decision = evaluate_payment(action, standing)

    assert decision.outcome == "refused"