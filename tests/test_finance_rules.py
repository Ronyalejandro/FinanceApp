from decimal import Decimal
import pytest

# Tests for services.finance_rules (Phase 1)

def test_validate_amount_accepts_positive():
    from services import finance_rules
    amt = Decimal('123.45')
    # Should not raise
    assert finance_rules.validate_amount(amt) == amt


def test_validate_amount_rejects_zero_or_negative():
    from services import finance_rules
    with pytest.raises(ValueError):
        finance_rules.validate_amount(Decimal('0'))
    with pytest.raises(ValueError):
        finance_rules.validate_amount(Decimal('-1'))


def test_validate_credit_payment_against_used_balance():
    from services import finance_rules
    used = Decimal('500.00')
    ok_payment = Decimal('200.00')
    large_payment = Decimal('600.00')
    # ok should pass
    assert finance_rules.validate_credit_payment(ok_payment, used) == ok_payment
    # too large should raise
    with pytest.raises(ValueError):
        finance_rules.validate_credit_payment(large_payment, used)


def test_validate_savings_contribution_limits():
    from services import finance_rules
    goal_remaining = Decimal('1000.00')
    contrib_ok = Decimal('250.00')
    contrib_too_large = Decimal('2000.00')
    assert finance_rules.validate_savings_contribution(contrib_ok, goal_remaining) == contrib_ok
    with pytest.raises(ValueError):
        finance_rules.validate_savings_contribution(contrib_too_large, goal_remaining)
