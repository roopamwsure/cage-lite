from cage_lite.core.evidence import EvidenceRecord, write_evidence


def test_evidence_record_can_be_created():
    record = EvidenceRecord.create(
        evidence_type="payment_request",
        subject_id="payment-001",
        summary="Finance agent requested a payment.",
        source="test",
        data={
            "amount": 75000,
            "currency": "USD",
        },
    )

    assert record.evidence_id.startswith("evidence-")
    assert record.evidence_type == "payment_request"
    assert record.subject_id == "payment-001"
    assert record.data["amount"] == 75000


def test_evidence_record_can_be_written(tmp_path):
    record = EvidenceRecord.create(
        evidence_type="manager_approval",
        subject_id="payment-002",
        summary="Manager approved the payment.",
        source="test",
    )

    path = write_evidence(record, tmp_path)

    assert path.exists()
    assert record.evidence_id in path.name