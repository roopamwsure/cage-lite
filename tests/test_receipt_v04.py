from types import SimpleNamespace

from cage_lite.core.action import ActionRequest
from cage_lite.core.approval import ApprovalRecord
from cage_lite.core.decision import CageDecision
from cage_lite.core.receipt import RECEIPT_SCHEMA_VERSION, create_receipt
from cage_lite.core.standing import AgentStanding


def test_v04_receipt_records_no_bind_effect_proof():
    action = ActionRequest(
        action_id="payment-75000",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=75000,
        currency="USD",
        evidence_ref="evidence/payment-75000",
    )

    standing = AgentStanding(
        agent_id="finance-agent-01",
        allowed_actions={"payment"},
        max_payment_amount=50000,
    )

    decision = CageDecision(
        action_id=action.action_id,
        agent_id=action.agent_id,
        action_type=action.action_type,
        outcome="held",
        reason="Payment exceeds the agent standing limit and requires approval before binding.",
        policy_ref="policy/payment-threshold-v1",
        evidence_ref=action.evidence_ref,
        standing_ref="standing/finance-agent-01",
    )

    effect_record = SimpleNamespace(
        effect_id="effect-no-bind-001",
        disposition="no_bind",
        executed=False,
        system_of_record_status="not_written",
    )
    effect_result = SimpleNamespace(
        effect_record=effect_record,
        bound=False,
        result=None,
    )

    receipt = create_receipt(
        decision=decision,
        action=action,
        standing=standing,
        effect_result=effect_result,
        movement_id="movement-vendor-payment-001",
        actor_id="finance-ops-user-01",
        delegation_chain=[
            "finance-ops-user-01",
            "finance-agent-01",
        ],
    )

    assert receipt.schema_version == RECEIPT_SCHEMA_VERSION
    assert receipt.boundary_outcome == "held"
    assert receipt.boundary_reason == decision.reason

    assert receipt.amount == 75000
    assert receipt.currency == "USD"
    assert receipt.standing_limit == 50000

    assert receipt.approval_required is True
    assert receipt.approval_present is False
    assert receipt.approval_ref is None

    assert receipt.effect_id == "effect-no-bind-001"
    assert receipt.effect_disposition == "no_bind"
    assert receipt.effect_attempted is True
    assert receipt.effect_executed is False
    assert receipt.system_of_record_status == "not_written"

    assert receipt.outcome == "held"
    assert receipt.prebind is True
    assert len(receipt.digest) == 64


def test_v04_receipt_links_replay_to_original_held_receipt():
    action = ActionRequest(
        action_id="payment-75000",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=75000,
        currency="USD",
        evidence_ref="evidence/payment-75000",
    )

    standing = AgentStanding(
        agent_id="finance-agent-01",
        allowed_actions={"payment"},
        max_payment_amount=50000,
    )

    approval = ApprovalRecord.issue(
        action=action,
        approved_by="manager-01",
        approved_amount=75000,
        evidence_ref="evidence/approval-payment-75000",
    )

    decision = CageDecision(
        action_id=action.action_id,
        agent_id=action.agent_id,
        action_type=action.action_type,
        outcome="admitted",
        reason="Payment satisfies standing, policy, and approval requirements.",
        policy_ref="policy/payment-threshold-v1",
        evidence_ref=action.evidence_ref,
        evidence_refs=[approval.evidence_ref],
        standing_ref="standing/finance-agent-01",
    )

    effect_record = SimpleNamespace(
        effect_id="effect-bound-001",
        disposition="bound",
        executed=True,
        system_of_record_status="written",
    )
    effect_result = SimpleNamespace(
        effect_record=effect_record,
        bound=True,
        result={"status": "sent"},
    )

    receipt = create_receipt(
        decision=decision,
        action=action,
        standing=standing,
        approval=approval,
        effect_result=effect_result,
        movement_id="movement-vendor-payment-001",
        replay_of_receipt_id="receipt-held-001",
    )

    assert receipt.boundary_outcome == "admitted"
    assert receipt.replay_of_receipt_id == "receipt-held-001"

    assert receipt.approval_required is True
    assert receipt.approval_present is True
    assert receipt.approval_ref == approval.approval_id

    assert receipt.effect_id == "effect-bound-001"
    assert receipt.effect_disposition == "bound"
    assert receipt.effect_executed is True
    assert receipt.system_of_record_status == "written"

    assert receipt.evidence_refs == [
        "evidence/payment-75000",
        "evidence/approval-payment-75000",
    ]