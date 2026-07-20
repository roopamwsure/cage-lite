from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FileLedger:
    """Local JSON storage for CAGE receipts and effect records."""

    def __init__(self, root: str | Path = "playground") -> None:
        self.root = Path(root)
        self.receipts_dir = self.root / "receipts"
        self.effects_dir = self.root / "effects"

        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        self.effects_dir.mkdir(parents=True, exist_ok=True)

    def append_receipt(self, receipt: Any) -> Path:
        data = receipt.to_dict() if hasattr(receipt, "to_dict") else dict(receipt)
        path = self.receipts_dir / f"{data['receipt_id']}.json"
        self._write_json(path, data)
        return path

    def append_effect(self, effect_record: Any) -> Path:
        data = (
            effect_record.to_dict()
            if hasattr(effect_record, "to_dict")
            else dict(effect_record)
        )
        path = self.effects_dir / f"{data['effect_id']}.json"
        self._write_json(path, data)
        return path

    def list_receipts(self) -> list[dict[str, Any]]:
        return self._list_json(self.receipts_dir)

    def list_effects(self) -> list[dict[str, Any]]:
        return self._list_json(self.effects_dir)

    def get_receipt(self, receipt_id: str) -> dict[str, Any]:
        return self._read_json(self.receipts_dir / f"{receipt_id}.json")

    def get_effect(self, effect_id: str) -> dict[str, Any]:
        return self._read_json(self.effects_dir / f"{effect_id}.json")

    def _list_json(self, directory: Path) -> list[dict[str, Any]]:
        return [self._read_json(path) for path in sorted(directory.glob("*.json"))]

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Ledger record not found: {path}")

        return json.loads(path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        path.write_text(
            json.dumps(data, indent=2, sort_keys=True),
            encoding="utf-8",
        )