import os
import tempfile
import sqlite3
from db.database import DatabaseManager


def test_credit_usage_and_payment(tmp_path):
    db_file = tmp_path / "test.db"
    db = DatabaseManager(str(db_file))

    # Establecer límite
    db.update_credit_limit(100.0)

    # Agregar gasto con crédito
    db.add_transaction("Gasto", "Comida", 30.0, "2026-01-03", "Cena", "CreditoInterno")
    lim, used = db.get_credit_info()
    assert used == 30.0

    # Pagar crédito
    db.add_transaction("PagoCredito", "Financiero", 20.0, "2026-01-03", "Abono", "Transferencia")
    lim, used_after = db.get_credit_info()
    assert used_after == 10.0
