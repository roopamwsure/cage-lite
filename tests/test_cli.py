from cage_lite.cli import run_payment


def test_cli_payment_without_approval_is_held(tmp_path):
    decision, effect_result = run_payment(
        amount=75000,
        approved=False,
        output_dir=tmp_path,
    )

    assert decision.outcome == "held"
    assert effect_result.bound is False


def test_cli_payment_with_approval_is_admitted(tmp_path):
    decision, effect_result = run_payment(
        amount=75000,
        approved=True,
        output_dir=tmp_path,
    )

    assert decision.outcome == "admitted"
    assert effect_result.bound is True


def test_cli_small_payment_is_admitted(tmp_path):
    decision, effect_result = run_payment(
        amount=25000,
        approved=False,
        output_dir=tmp_path,
    )

    assert decision.outcome == "admitted"
    assert effect_result.bound is True