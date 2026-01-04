"""Script de migración ligero para la base de datos.

Este script aplica cambios no destructivos: crea índices y asegura
que exista una fila en `credito_config`. Para cambios estructurales
mayores (CHECK en tablas existentes) se recomienda un proceso manual
de migración que respalde la BD y reconstruya tablas.
"""
import sqlite3
from pathlib import Path


def migrate(db_path: str = "finanzas_personales.db") -> None:
    p = Path(db_path)
    if not p.exists():
        print(f"DB {db_path} no existe; la operación de migración no es necesaria.")
        return

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        # Índices no destructivos
        cur.execute("CREATE INDEX IF NOT EXISTS idx_transacciones_fecha ON transacciones(fecha)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_transacciones_tipo ON transacciones(tipo)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_transacciones_categoria ON transacciones(categoria)")

        # Asegurar fila única en credito_config
        cur.execute("SELECT count(*) FROM credito_config")
        row = cur.fetchone()
        if row is None or row[0] == 0:
            cur.execute("INSERT INTO credito_config (limite_total, saldo_utilizado) VALUES (500, 0)")

        conn.commit()
        print("Migración ligera completada: índices creados y crédito asegurado.")
    finally:
        conn.close()


if __name__ == '__main__':
    migrate()
