from cage_lite.core.decision import CageDecision
from cage_lite.core.receipt import create_receipt, write_receipt


def test_receipt_records_decision():
    decision = CageDecision(
        action_id="payment-001",
        agent_id="finance-agent-01",
        action_type="payment",
        outcome="held",
        reason="Payment requires approval before binding.",
        policy_ref="policy/payment-threshold-v1",
        evidence_ref="evidence/payment-001",
        standing_ref="standing/finance-agent-01",
    )

    receipt = create_receipt(decision)

    assert receipt.action_id == decision.action_id
    assert receipt.agent_id == decision.agent_id
    assert receipt.outcome == "held"
    assert receipt.prebind is True
    assert len(receipt.digest) == 64


def test_receipt_can_be_written(tmp_path):
    decision = CageDecision(
        action_id="payment-002",
        agent_id="finance-agent-01",
        action_type="payment",
        outcome="admitted",
        reason="Payment satisfies standing and policy requirements.",
    )

    receipt = create_receipt(decision)
    path = write_receipt(receipt, tmp_path)

    assert path.exists()
    assert receipt.receipt_id in path.name