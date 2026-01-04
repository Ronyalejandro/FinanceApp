"""Servicios que encapsulan lógica de negocio sobre transacciones."""
from typing import Optional
from db.database import DatabaseManager


class TransactionService:
    """Servicio ligero para validar y crear transacciones.

    Mantiene la API simple para la UI: `create_transaction(...)`.
    """
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or DatabaseManager()

    def create_transaction(self, tipo: str, categoria: str, monto: float, fecha: str, descripcion: str, metodo: str) -> int:
        # Validaciones simples
        if monto < 0:
            raise ValueError("El monto debe ser no negativo")
        if tipo not in ("Ingreso", "Gasto", "PagoCredito"):
            raise ValueError("Tipo de transacción inválido")

        # Delegar a DB (operación atómica internamente)
        return self.db.add_transaction(tipo, categoria, monto, fecha, descripcion, metodo)
