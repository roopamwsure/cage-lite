from cage_lite.core.action import ActionRequest
from cage_lite.core.boundary import evaluate_prebind
from cage_lite.core.decision import CageDecision
from cage_lite.core.standing import AgentStanding


def simple_policy(action, standing):
    return CageDecision(
        action_id=action.action_id,
        agent_id=action.agent_id,
        action_type=action.action_type,
        outcome="admitted",
        reason="Allowed by test policy.",
        policy_ref="policy/test",
        standing_ref=f"standing/{standing.agent_id}",
    )


def test_prebind_boundary_adds_receipt_id():
    action = ActionRequest(
        action_id="test-action-001",
        agent_id="agent-001",
        action_type="test_action",
    )

    standing = AgentStanding(
        agent_id="agent-001",
        allowed_actions={"test_action"},
    )

    decision = evaluate_prebind(action, standing, simple_policy)

    assert decision.outcome == "admitted"
    assert decision.receipt_id is not None
    assert decision.receipt_id.startswith("receipt-")


def test_prebind_boundary_writes_receipt(tmp_path):
    action = ActionRequest(
        action_id="test-action-002",
        agent_id="agent-001",
        action_type="test_action",
    )

    standing = AgentStanding(
        agent_id="agent-001",
        allowed_actions={"test_action"},
    )

    decision = evaluate_prebind(
        action=action,
        standing=standing,
        policy=simple_policy,
        receipt_folder=tmp_path,
    )

    receipts = list(tmp_path.glob("*.json"))

    assert decision.receipt_id is not None
    assert len(receipts) == 1