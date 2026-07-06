from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4


@dataclass
class EvidenceRecord:
    evidence_id: str
    evidence_type: str
    subject_id: str
    summary: str
    source: str
    created_at: str
    data: dict[str, object] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        evidence_type: str,
        subject_id: str,
        summary: str,
        source: str,
        data: dict[str, object] | None = None,
    ) -> "EvidenceRecord":
        return cls(
            evidence_id=f"evidence-{uuid4().hex[:12]}",
            evidence_type=evidence_type,
            subject_id=subject_id,
            summary=summary,
            source=source,
            created_at=datetime.now(timezone.utc).isoformat(),
            data=data or {},
        )

    def to_dict(self) -> dict:
        return asdict(self)


def write_evidence(record: EvidenceRecord, folder: Path) -> Path:
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f"{record.evidence_id}.json"
    path.write_text(
        json.dumps(record.to_dict(), indent=2),
        encoding="utf-8",
    )

    return path