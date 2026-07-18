from copy import deepcopy

from cage_lite.core.action import ActionRequest
from cage_lite.core.decision import CageDecision
from cage_lite.core.receipt import create_receipt
from cage_lite.ui.views import warrants


def current_warrant():
    action = ActionRequest(
        action_id="payment-ui-digest-001",
        agent_id="finance-agent-01",
        action_type="payment",
        amount=75000,
        currency="USD",
        evidence_ref="evidence/payment-ui-digest-001",
    )

    decision = CageDecision(
        action_id=action.action_id,
        agent_id=action.agent_id,
        action_type=action.action_type,
        outcome="held",
        reason="Payment requires approval before binding.",
        policy_ref="policy/payment-threshold-v1",
        evidence_ref=action.evidence_ref,
        standing_ref="standing/finance-agent-01",
    )

    return create_receipt(
        decision=decision,
        action=action,
    ).to_dict()


def rendered_integrity_card(monkeypatch, warrant):
    calls = []

    monkeypatch.setattr(
        warrants.st,
        "markdown",
        lambda content, unsafe_allow_html=False: calls.append(
            (content, unsafe_allow_html)
        ),
    )

    warrants.render_integrity_card(warrant)

    assert len(calls) == 1
    assert calls[0][1] is True

    return calls[0][0]


def test_integrity_card_separates_recorded_digest_and_verification(
    monkeypatch,
):
    warrant = current_warrant()

    content = rendered_integrity_card(
        monkeypatch,
        warrant,
    )

    assert "Recorded digest" in content
    assert warrant["digest"] in content
    assert "Digest verification" in content
    assert "VERIFIED" in content
    assert "cage-badge good" in content


def test_integrity_card_uses_stacked_hash_fields(monkeypatch):
    warrant = current_warrant()

    content = rendered_integrity_card(
        monkeypatch,
        warrant,
    )

    assert content.count("cage-hash-field") == 2
    assert "Payload hash" in content
    assert warrant["action_payload_hash"] in content
    assert "Recorded digest" in content
    assert warrant["digest"] in content


def test_integrity_card_uses_formatted_timestamp(monkeypatch):
    warrant = current_warrant()
    warrant["created_at"] = "2026-07-17T15:21:40.421056+00:00"

    content = rendered_integrity_card(
        monkeypatch,
        warrant,
    )

    assert "2026-07-17 15:21:40.421 UTC" in content
    assert "2026-07-17T15:21:40.421056+00:00" not in content


def test_integrity_card_shows_compact_verified_detail(monkeypatch):
    warrant = current_warrant()

    content = rendered_integrity_card(
        monkeypatch,
        warrant,
    )

    assert (
        "Recorded digest matches recomputed schema 0.4 content."
        in content
    )


def test_integrity_card_shows_mismatch(monkeypatch):
    warrant = current_warrant()
    warrant["boundary_outcome"] = "admitted"

    content = rendered_integrity_card(
        monkeypatch,
        warrant,
    )

    assert "MISMATCH" in content
    assert "cage-badge bad" in content
    assert (
        "Recorded digest does not match recomputed schema 0.4 content."
        in content
    )


def test_integrity_card_shows_not_available(monkeypatch):
    warrant = current_warrant()
    warrant.pop("digest")

    content = rendered_integrity_card(
        monkeypatch,
        warrant,
    )

    assert "NOT AVAILABLE" in content
    assert "cage-badge warn" in content
    assert "Not recorded" in content
    assert (
        "No valid recorded digest is available for verification."
        in content
    )


def test_integrity_card_shows_legacy(monkeypatch):
    warrant = current_warrant()
    warrant["schema_version"] = "0.3"

    content = rendered_integrity_card(
        monkeypatch,
        warrant,
    )

    assert "LEGACY" in content
    assert "cage-badge neutral" in content
    assert "schema version &#x27;0.3&#x27;" in content


def test_integrity_card_explains_digest_limitations(monkeypatch):
    warrant = current_warrant()

    content = rendered_integrity_card(
        monkeypatch,
        warrant,
    )

    assert "content consistency" in content
    assert "does not prove signer identity" in content
    assert "external notarization" in content


def test_integrity_card_does_not_mutate_warrant(monkeypatch):
    warrant = current_warrant()
    warrant["_file_name"] = "receipt-payment-ui-digest-001.json"
    original = deepcopy(warrant)

    rendered_integrity_card(
        monkeypatch,
        warrant,
    )

    assert warrant == original