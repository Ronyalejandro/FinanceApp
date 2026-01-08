from decimal import Decimal
import pytest

# Tests that describe expected behavior of services.finance_service

def test_create_transaction_rejects_invalid_type():
    from services import finance_service
    payload = {'type': 'INVALID', 'amount': Decimal('10.00')}
    with pytest.raises(ValueError):
        finance_service.create_transaction(payload)


def test_create_credit_payment_enforces_rules(monkeypatch):
    from services import finance_service
    from services.transaction_type import TransactionType
    # Simulate DB layer returning a used credit balance
    class DummyDB:
        def get_credit_used(self):
            return Decimal('500.00')
    monkeypatch.setattr('services.finance_service.DatabaseManager', lambda: DummyDB())

    # Valid payment
    payload_ok = {'type': TransactionType.PagoCredito.name, 'amount': Decimal('300.00')}
    # Should not raise
    finance_service.create_transaction(payload_ok)

    # Too large payment
    payload_bad = {'type': TransactionType.PagoCredito.name, 'amount': Decimal('600.00')}
    with pytest.raises(ValueError):
        finance_service.create_transaction(payload_bad)
