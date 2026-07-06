from cage_lite.core.action import ActionRequest
from cage_lite.core.standing import AgentStanding
from cage_lite.policies.payment import evaluate_payment


def test_small_payment_is_admitted():
    action = ActionRequest(
        action_id="payment-001",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=25000,
        currency="USD",
    )

    standing = AgentStanding(
        agent_id="finance-agent-01",
        allowed_actions={"payment"},
        max_payment_amount=50000,
    )

    decision = evaluate_payment(action, standing)

    assert decision.outcome == "admitted"


def test_large_payment_without_approval_is_held():
    action = ActionRequest(
        action_id="payment-002",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=75000,
        currency="USD",
    )

    standing = AgentStanding(
        agent_id="finance-agent-01",
        allowed_actions={"payment"},
        max_payment_amount=50000,
    )

    decision = evaluate_payment(action, standing)

    assert decision.outcome == "held"


def test_large_payment_with_approval_is_admitted():
    action = ActionRequest(
        action_id="payment-003",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=75000,
        currency="USD",
        approved_by="manager-01",
    )

    standing = AgentStanding(
        agent_id="finance-agent-01",
        allowed_actions={"payment"},
        max_payment_amount=50000,
    )

    decision = evaluate_payment(action, standing)

    assert decision.outcome == "admitted"


def test_agent_without_payment_standing_is_refused():
    action = ActionRequest(
        action_id="payment-004",
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