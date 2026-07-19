from __future__ import annotations

import json
import runpy
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_FOLDER = REPOSITORY_ROOT / "examples"


def run_example(
    filename: str,
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    runpy.run_path(
        str(EXAMPLES_FOLDER / filename),
        run_name="__main__",
    )


def load_single_record(folder: Path) -> dict:
    files = list(folder.glob("*.json"))

    assert len(files) == 1

    return json.loads(
        files[0].read_text(encoding="utf-8")
    )


def test_no_bind_example_persists_effect_proof(
    tmp_path: Path,
    monkeypatch,
):
    run_example(
        "payment_no_bind_demo.py",
        tmp_path,
        monkeypatch,
    )

    playground = tmp_path / "playground"
    effect = load_single_record(playground / "effects")

    assert len(list((playground / "receipts").glob("*.json"))) == 1
    assert effect["tool_name"] == "vendor_payment_api"
    assert effect["decision_outcome"] == "held"
    assert effect["attempted"] is True
    assert effect["executed"] is False
    assert effect["disposition"] == "no_bind"
    assert effect["system_of_record_status"] == "not_written"


def test_approval_example_persists_bound_effect_proof(
    tmp_path: Path,
    monkeypatch,
):
    run_example(
        "payment_approval_demo.py",
        tmp_path,
        monkeypatch,
    )

    playground = tmp_path / "playground"
    effect = load_single_record(playground / "effects")

    assert len(list((playground / "receipts").glob("*.json"))) == 1
    assert effect["tool_name"] == "vendor_payment_api"
    assert effect["decision_outcome"] == "admitted"
    assert effect["attempted"] is True
    assert effect["executed"] is True
    assert effect["disposition"] == "bound"
    assert effect["system_of_record_status"] == "written"
    assert effect["result"]["payment_id"] == "pay-002"


def test_narrowed_example_persists_scoped_effect_proof(
    tmp_path: Path,
    monkeypatch,
):
    run_example(
        "payment_narrowed_demo.py",
        tmp_path,
        monkeypatch,
    )

    playground = tmp_path / "playground"
    effect = load_single_record(playground / "effects")

    assert len(list((playground / "receipts").glob("*.json"))) == 1
    assert effect["tool_name"] == "vendor_payment_api"
    assert effect["decision_outcome"] == "narrowed"
    assert effect["attempted"] is True
    assert effect["executed"] is True
    assert effect["disposition"] == "narrowed_bound"
    assert effect["system_of_record_status"] == "written"
    assert effect["result"]["amount"] == 50000
    assert effect["result"]["currency"] == "USD"