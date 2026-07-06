from pathlib import Path
from typing import Any, Callable

from cage_lite.core.action import ActionRequest
from cage_lite.core.decision import CageDecision
from cage_lite.core.receipt import create_receipt, write_receipt
from cage_lite.core.standing import AgentStanding


PolicyEvaluator = Callable[..., CageDecision]


def evaluate_prebind(
    action: ActionRequest,
    standing: AgentStanding,
    policy: PolicyEvaluator,
    receipt_folder: Path | None = None,
    policy_context: dict[str, Any] | None = None,
) -> CageDecision:
    context = policy_context or {}

    decision = policy(action, standing, **context)

    receipt = create_receipt(decision, prebind=True)
    decision.receipt_id = receipt.receipt_id

    if receipt_folder:
        write_receipt(receipt, receipt_folder)

    return decision