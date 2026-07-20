from pathlib import Path

from cage_lite.core.decision import CageDecision
from cage_lite.core.effect import execute_if_admitted
from cage_lite.core.ledger import FileLedger


def test_held_decision_does_not_execute_effect(tmp_path: Path):
    ledger = FileLedger(tmp_path)

    decision = CageDecision(
        action_id="payment-test-001",
        agent_id="finance-agent-01",
        action_type="payment",
        outcome="held",
        reason="Approval is required for this payment.",
        policy_ref="policy/payment-threshold-v1",
        standing_ref="standing/finance-agent-01",
        receipt_id="receipt-test-001",
    )

    calls = {"count": 0}

    def payment_api():
        calls["count"] += 1
        return {"status": "sent"}

    result = execute_if_admitted(
        decision=decision,
        effect=payment_api,
        tool_name="mock_vendor_payment_api",
        ledger=ledger,
    )

    assert result.bound is False
    assert result.disposition == "no_bind"
    assert result.system_of_record_status == "not_written"
    assert calls["count"] == 0

    effects = ledger.list_effects()

    assert len(effects) == 1
    assert effects[0]["tool_name"] == "mock_vendor_payment_api"
    assert effects[0]["decision_outcome"] == "held"
    assert effects[0]["attempted"] is True
    assert effects[0]["executed"] is False
    assert effects[0]["disposition"] == "no_bind"
    assert effects[0]["system_of_record_status"] == "not_written"


def test_admitted_decision_executes_effect_once(tmp_path: Path):
    ledger = FileLedger(tmp_path)

    decision = CageDecision(
        action_id="payment-test-002",
        agent_id="finance-agent-01",
        action_type="payment",
        outcome="admitted",
        reason="Approval is present.",
        policy_ref="policy/payment-threshold-v1",
        standing_ref="standing/finance-agent-01",
        receipt_id="receipt-test-002",
    )

    calls = {"count": 0}

    def payment_api():
        calls["count"] += 1
        return {
            "status": "sent",
            "payment_id": "demo-payment-001",
        }

    result = execute_if_admitted(
        decision=decision,
        effect=payment_api,
        tool_name="mock_vendor_payment_api",
        ledger=ledger,
    )

    assert result.bound is True
    assert result.disposition == "bound"
    assert result.system_of_record_status == "written"
    assert calls["count"] == 1

    effects = ledger.list_effects()

    assert len(effects) == 1
    assert effects[0]["tool_name"] == "mock_vendor_payment_api"
    assert effects[0]["decision_outcome"] == "admitted"
    assert effects[0]["attempted"] is True
    assert effects[0]["executed"] is True
    assert effects[0]["disposition"] == "bound"
    assert effects[0]["system_of_record_status"] == "written"
    assert effects[0]["result"]["payment_id"] == "demo-payment-001"