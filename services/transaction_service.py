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
        from models.schemas import TransactionCreate
        from pydantic import ValidationError

        try:
            # Validar con Pydantic
            tx_data = TransactionCreate(
                tipo=tipo,
                categoria=categoria,
                monto=monto,
                fecha=fecha,
                descripcion=descripcion,
                metodo_pago=metodo
            )
            
            # Delegar a DB usando datos validados
            return self.db.add_transaction(
                tx_data.tipo, 
                tx_data.categoria, 
                tx_data.monto, 
                tx_data.fecha, 
                tx_data.descripcion, 
                tx_data.metodo_pago
            )
        except ValidationError as e:
            # Simplificar mensaje de error para la UI
            errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise ValueError("\n".join(errors))
