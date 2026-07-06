from cage_lite.core.decision import CageDecision
from cage_lite.core.effect import execute_if_admitted
from cage_lite.core.effect import execute_if_admitted, execute_narrowed


def test_admitted_action_executes_effect():
    decision = CageDecision(
        action_id="payment-001",
        agent_id="finance-agent-01",
        action_type="payment",
        outcome="admitted",
        reason="Payment satisfies standing and policy requirements.",
        receipt_id="receipt-001",
    )

    result = execute_if_admitted(
        decision=decision,
        effect=lambda: {"status": "sent"},
    )

    assert result.bound is True
    assert result.result == {"status": "sent"}
    assert result.receipt_id == "receipt-001"


def test_held_action_does_not_execute_effect():
    payment_was_sent = False

    def send_payment():
        nonlocal payment_was_sent
        payment_was_sent = True
        return {"status": "sent"}

    decision = CageDecision(
        action_id="payment-002",
        agent_id="finance-agent-01",
        action_type="payment",
        outcome="held",
        reason="Payment requires approval before binding.",
        receipt_id="receipt-002",
    )

    result = execute_if_admitted(
        decision=decision,
        effect=send_payment,
    )

    assert result.bound is False
    assert result.result is None
    assert payment_was_sent is False


def test_refused_action_does_not_execute_effect():
    decision = CageDecision(
        action_id="payment-003",
        agent_id="support-agent-01",
        action_type="payment",
        outcome="refused",
        reason="Agent does not have standing to perform payment actions.",
        receipt_id="receipt-003",
    )

    result = execute_if_admitted(
        decision=decision,
        effect=lambda: {"status": "sent"},
    )

    assert result.bound is False
    assert result.result is None


def test_no_bind_action_does_not_execute_effect():
    decision = CageDecision(
        action_id="payment-004",
        agent_id="finance-agent-01",
        action_type="payment",
        outcome="no-bind",
        reason="Action was rendered non-effective.",
        receipt_id="receipt-004",
    )

    result = execute_if_admitted(
        decision=decision,
        effect=lambda: {"status": "sent"},
    )

    assert result.bound is False
    assert result.result is None

def test_narrowed_action_executes_only_allowed_scope():
    decision = CageDecision(
        action_id="payment-004",
        agent_id="finance-agent-01",
        action_type="payment",
        outcome="narrowed",
        reason="Payment was narrowed to the standing limit.",
        receipt_id="receipt-004",
        allowed_scope={
            "amount": 50000,
            "currency": "USD",
        },
    )

    result = execute_narrowed(
        decision=decision,
        effect=lambda scope: {
            "status": "sent",
            "amount": scope["amount"],
            "currency": scope["currency"],
        },
    )

    assert result.bound is True
    assert result.result["amount"] == 50000
    assert result.result["currency"] == "USD"


def test_narrowed_action_without_allowed_scope_does_not_execute():
    payment_was_sent = False

    def send_payment(scope):
        nonlocal payment_was_sent
        payment_was_sent = True
        return {"status": "sent"}

    decision = CageDecision(
        action_id="payment-005",
        agent_id="finance-agent-01",
        action_type="payment",
        outcome="narrowed",
        reason="Payment was narrowed, but scope is missing.",
        receipt_id="receipt-005",
    )

    result = execute_narrowed(
        decision=decision,
        effect=send_payment,
    )

    assert result.bound is False
    assert result.result is None
    assert payment_was_sent is False
