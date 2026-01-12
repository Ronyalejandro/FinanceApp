"""DatabaseManager movido a módulo separado.

Contiene la implementación del gestor SQLite y garantiza operaciones
atómicas para las transacciones financieras (especialmente crédito interno).
"""
import sqlite3
from typing import Optional, Tuple, List


from config import DB_PATH

class DatabaseManager:
    """Gestor de la base de datos SQLite."""
    def __init__(self, db_name: str = None) -> None:
        self.db_name = db_name or str(DB_PATH)
        self.init_db()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        return conn

    def init_db(self) -> None:
        """Inicializa las tablas si no existen y añade índices."""
        with self.connect() as conn:
            cursor = conn.cursor()

            # Tabla de Transacciones (Ingresos y Gastos)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transacciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL,
                    categoria TEXT,
                    monto REAL NOT NULL CHECK(monto >= 0),
                    fecha TEXT NOT NULL,
                    descripcion TEXT,
                    metodo_pago TEXT
                )
            ''')

            # Tabla de Configuración de Crédito (Sistema Cashéa)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credito_config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    limite_total REAL DEFAULT 0,
                    saldo_utilizado REAL DEFAULT 0
                )
            ''')

            # Inicializar crédito si está vacío
            cursor.execute("SELECT count(*) FROM credito_config")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO credito_config (limite_total, saldo_utilizado) VALUES (500, 0)")

            # Tabla de Metas de Ahorro (Legacy - to be migrated if needed, or kept)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metas_ahorro (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    monto_objetivo REAL NOT NULL CHECK(monto_objetivo >= 0),
                    monto_actual REAL DEFAULT 0
                )
            ''')

            # Nueva Tabla: Planes de Ahorro por Objetivos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS planes_ahorro (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_plan TEXT NOT NULL,
                    monto_objetivo REAL NOT NULL,
                    monto_actual REAL DEFAULT 0,
                    fecha_limite TEXT,
                    color_hex TEXT
                )
            ''')

            # Tabla de Presupuestos (Smart Budget)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS presupuestos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    categoria TEXT UNIQUE NOT NULL,
                    monto_limite REAL NOT NULL CHECK(monto_limite >= 0)
                )
            ''')

            # Tabla de Transacciones Recurrentes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transacciones_recurrentes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    monto REAL NOT NULL,
                    dia_cobro INTEGER NOT NULL,
                    categoria TEXT,
                    activo INTEGER DEFAULT 1
                )
            ''')

            # Índices para consultas frecuentes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transacciones_fecha ON transacciones(fecha)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transacciones_tipo ON transacciones(tipo)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transacciones_categoria ON transacciones(categoria)")

            conn.commit()

    # --- Métodos CRUD ---
    def add_transaction(self, tipo: str, categoria: str, monto: float, fecha: str, descripcion: str, metodo: str) -> int:
        return self.add_transaction_atomic(tipo, categoria, monto, fecha, descripcion, metodo)

    def add_transaction_atomic(self, tipo: str, categoria: str, monto: float, fecha: str, descripcion: str, metodo: str) -> int:
        """Inserta una transacción y actualiza el estado del crédito de forma atómica.

        Lanza ValueError si la operación no es válida (ej. monto negativo o límite excedido).
        """
        if monto < 0:
            raise ValueError("El monto debe ser no negativo")

        conn = self.connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO transacciones (tipo, categoria, monto, fecha, descripcion, metodo_pago)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tipo, categoria, monto, fecha, descripcion, metodo))

            if metodo == "CreditoInterno" and tipo == "Gasto":
                cursor.execute("SELECT limite_total, saldo_utilizado FROM credito_config LIMIT 1")
                row = cursor.fetchone()
                if row is None:
                    raise sqlite3.Error("Configuración de crédito no disponible")
                limite, usado = row
                if usado + monto > limite:
                    raise ValueError("Límite de crédito excedido")
                cursor.execute("UPDATE credito_config SET saldo_utilizado = ?", (usado + monto,))
            elif tipo == "PagoCredito":
                cursor.execute("SELECT saldo_utilizado FROM credito_config LIMIT 1")
                row = cursor.fetchone()
                if row is None:
                    raise sqlite3.Error("Configuración de crédito no disponible")
                usado = row[0]
                nuevo = max(0, usado - monto)
                cursor.execute("UPDATE credito_config SET saldo_utilizado = ?", (nuevo,))

            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_transactions(self, limit: int = 50) -> List[tuple]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transacciones ORDER BY fecha DESC, id DESC LIMIT ?", (limit,))
            return cursor.fetchall()

    def delete_transaction(self, tx_id: int) -> None:
        """Elimina una transacción y revierte su impacto en el crédito si aplica."""
        conn = self.connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.cursor()

            # 1. Obtener detalles de la transacción antes de borrar
            cursor.execute("SELECT tipo, monto, metodo_pago FROM transacciones WHERE id = ?", (tx_id,))
            row = cursor.fetchone()
            if not row:
                return

            tipo, monto, metodo = row

            # 2. Revertir impacto en crédito
            if metodo == "CreditoInterno" and tipo == "Gasto":
                # Devolver al saldo disponible (restar de usado)
                cursor.execute("UPDATE credito_config SET saldo_utilizado = saldo_utilizado - ?", (monto,))
            elif tipo == "PagoCredito":
                # Volver a aumentar la deuda
                cursor.execute("UPDATE credito_config SET saldo_utilizado = saldo_utilizado + ?", (monto,))

            # 3. Borrar la transacción
            cursor.execute("DELETE FROM transacciones WHERE id = ?", (tx_id,))
            
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_recent_transactions(self, days: int = 90) -> List[tuple]:
        """Obtiene transacciones de los últimos 'days' días."""
        from datetime import datetime, timedelta
        
        # Calculate cutoff date
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transacciones WHERE fecha >= ? ORDER BY fecha ASC", (cutoff,))
            return cursor.fetchall()

    def get_summary(self) -> Tuple[float, float]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo='Ingreso'")
            ingresos = cursor.fetchone()[0] or 0.0
            cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo='Gasto'")
            gastos = cursor.fetchone()[0] or 0.0
            return ingresos, gastos

    def get_credit_info(self) -> Optional[Tuple[float, float]]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT limite_total, saldo_utilizado FROM credito_config LIMIT 1")
            return cursor.fetchone()

    def update_credit_limit(self, new_limit: float) -> None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE credito_config SET limite_total = ?", (new_limit,))
            conn.commit()

    def update_credit_usage(self, amount: float, add: bool = True) -> None:
        # Mantener para compatibilidad, pero preferir add_transaction_atomic
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT saldo_utilizado FROM credito_config LIMIT 1")
            row = cursor.fetchone()
            saldo_actual = row[0] if row is not None else 0
            if add:
                new_saldo = saldo_actual + amount
            else:
                new_saldo = max(0, saldo_actual - amount)
            cursor.execute("UPDATE credito_config SET saldo_utilizado = ?", (new_saldo,))
            conn.commit()

    def get_expenses_by_category(self) -> List[tuple]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT categoria, SUM(monto) FROM transacciones WHERE tipo='Gasto' GROUP BY categoria")
            return cursor.fetchall()

    def add_savings_goal(self, nombre: str, objetivo: float) -> None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO metas_ahorro (nombre, monto_objetivo) VALUES (?, ?)", (nombre, objetivo))
            conn.commit()

    def get_savings_goals(self) -> List[tuple]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM metas_ahorro")
            return cursor.fetchall()

    def update_savings_progress(self, id_meta: int, monto: float) -> None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE metas_ahorro SET monto_actual = monto_actual + ? WHERE id = ?", (monto, id_meta))
            conn.commit()

    def update_budget(self, categoria: str, monto: float) -> None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO presupuestos (categoria, monto_limite) VALUES (?, ?)
                ON CONFLICT(categoria) DO UPDATE SET monto_limite = excluded.monto_limite
            ''', (categoria, monto))
            conn.commit()

    def get_budget_comparison(self) -> List[tuple]:
        """Devuelve [(categoria, gasto_actual, limite), ...]"""
        # Calcular gasto del mes actual (simplificado: todo gasto histórico por ahora o filtrar por fecha string YYYY-MM)
        # Nota: Para ser precisos con "Mes Actual", necesitaríamos parsear la fecha.
        # Dado el formato de fecha 'YYYY-MM-DD', podemos filtrar con LIKE 'YYYY-MM%'
        from datetime import datetime
        current_month = datetime.now().strftime("%Y-%m")

        with self.connect() as conn:
            cursor = conn.cursor()
            
            # 1. Obtener todos los presupuestos
            cursor.execute("SELECT categoria, monto_limite FROM presupuestos")
            budgets = cursor.fetchall() # [(cat, limit), ...]
            
            results = []
            for cat, limit in budgets:
                # 2. Calcular gasto para esta categoría en el mes actual
                cursor.execute("""
                    SELECT SUM(monto) FROM transacciones 
                    WHERE tipo='Gasto' AND categoria=? AND fecha LIKE ?
                """, (cat, f"{current_month}%"))
                spent = cursor.fetchone()[0] or 0.0
                results.append((cat, spent, limit))
                
            return results

    # --- Planes de Ahorro (New System) ---
    def create_plan(self, nombre: str, objetivo: float, fecha: str, color: str) -> None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO planes_ahorro (nombre_plan, monto_objetivo, monto_actual, fecha_limite, color_hex)
                VALUES (?, ?, 0, ?, ?)
            ''', (nombre, objetivo, fecha, color))
            conn.commit()

    def get_plans(self) -> List[tuple]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM planes_ahorro ORDER BY id DESC")
            return cursor.fetchall()

    def deposit_to_plan(self, plan_id: int, amount: float) -> None:
        """Atomic deposit: Add Expense Transaction AND Update Plan Balance."""
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        conn = self.connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.cursor()

            # 1. Obtener nombre del plan para la descripción
            cursor.execute("SELECT nombre_plan FROM planes_ahorro WHERE id = ?", (plan_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Plan no encontrado")
            plan_name = row[0]

            # 2. Añadir Transacción (Gasto)
            cursor.execute('''
                INSERT INTO transacciones (tipo, categoria, monto, fecha, descripcion, metodo_pago)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ("Gasto", "Ahorro/Plan", amount, date_str, f"Aporte a {plan_name}", "Efectivo"))

            # 3. Actualizar Saldo del Plan
            cursor.execute("UPDATE planes_ahorro SET monto_actual = monto_actual + ? WHERE id = ?", (amount, plan_id))

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_plan(self, plan_id: int) -> None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM planes_ahorro WHERE id = ?", (plan_id,))
            conn.commit()

    # --- Recurring Transactions ---
    def add_recurring(self, nombre: str, monto: float, dia: int, categoria: str) -> None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transacciones_recurrentes (nombre, monto, dia_cobro, categoria)
                VALUES (?, ?, ?, ?)
            ''', (nombre, monto, dia, categoria))
            conn.commit()

    def get_recurring(self) -> List[tuple]:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transacciones_recurrentes WHERE activo=1 ORDER BY dia_cobro")
            return cursor.fetchall()

    def delete_recurring(self, rid: int) -> None:
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transacciones_recurrentes WHERE id=?", (rid,))
            conn.commit()
