from cage_lite.core.decision import CageDecision
from cage_lite.core.effect import execute_if_admitted


def test_admitted_action_executes_effect():
    decision = CageDecision(
        action_id="payment-001",
        agent_id="finance-agent-01",
        action_type="payment",
        outcome="admitted",
        reason="Payment satisfies policy requirements.",
        receipt_id="receipt-001",
    )

    result = execute_if_admitted(
        decision,
        lambda: {"status": "sent"},
    )

    assert result.bound is True
    assert result.result == {"status": "sent"}
    assert result.receipt_id == "receipt-001"


def test_held_action_does_not_execute_effect():
    called = False

    def blocked_effect():
        nonlocal called
        called = True
        return {"status": "sent"}

    decision = CageDecision(
        action_id="payment-002",
        agent_id="finance-agent-01",
        action_type="payment",
        outcome="held",
        reason="Payment requires approval before binding.",
        receipt_id="receipt-002",
    )

    result = execute_if_admitted(decision, blocked_effect)

    assert result.bound is False
    assert result.result is None
    assert called is False


def test_refused_action_does_not_execute_effect():
    decision = CageDecision(
        action_id="payment-003",
        agent_id="support-agent-01",
        action_type="payment",
        outcome="refused",
        reason="Agent does not have standing.",
    )

    result = execute_if_admitted(
        decision,
        lambda: {"status": "sent"},
    )

    assert result.bound is False