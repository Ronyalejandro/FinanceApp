"""Servicio para la exportación y gestión de datos."""
import csv
import shutil
import os
from datetime import datetime
from config import DB_PATH
from db.database import DatabaseManager

class DataService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def export_transactions_csv(self, filepath: str) -> None:
        """Exporta todas las transacciones a un archivo CSV."""
        transactions = self.db.get_transactions(limit=10000) # Obtener todas/muchas
        if not transactions:
            return

        # Definir encabezados basados en la estructura de la BD
        headers = ["ID", "Tipo", "Categoría", "Monto", "Fecha", "Descripción", "Método"]

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(transactions)

    def backup_database(self, target_dir: str) -> str:
        """Crea una copia de seguridad del archivo de base de datos."""
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.db"
        target_path = os.path.join(target_dir, filename)
        
        shutil.copy2(DB_PATH, target_path)
        return target_path
