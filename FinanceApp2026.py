import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os

# --- Configuración Global ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class DatabaseManager:
    """Gestor de la base de datos SQLite."""
    def __init__(self, db_name="finanzas_personales.db"):
        self.db_name = db_name
        self.init_db()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """Inicializa las tablas si no existen."""
        with self.connect() as conn:
            cursor = conn.cursor()
            
            # Tabla de Transacciones (Ingresos y Gastos)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transacciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT NOT NULL, -- 'Ingreso', 'Gasto', 'PagoCredito'
                    categoria TEXT,
                    monto REAL NOT NULL,
                    fecha TEXT NOT NULL,
                    descripcion TEXT,
                    metodo_pago TEXT -- 'Efectivo', 'Tarjeta', 'CreditoInterno'
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

            # Tabla de Metas de Ahorro
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metas_ahorro (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    monto_objetivo REAL NOT NULL,
                    monto_actual REAL DEFAULT 0
                )
            ''')
            conn.commit()

    # --- Métodos CRUD ---
    def add_transaction(self, tipo, categoria, monto, fecha, descripcion, metodo):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transacciones (tipo, categoria, monto, fecha, descripcion, metodo_pago)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (tipo, categoria, monto, fecha, descripcion, metodo))
            
            # Lógica de Crédito Interno
            if metodo == "CreditoInterno" and tipo == "Gasto":
                self.update_credit_usage(monto, add=True)
            elif tipo == "PagoCredito":
                self.update_credit_usage(monto, add=False)
                
            conn.commit()

    def get_transactions(self, limit=50):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transacciones ORDER BY fecha DESC, id DESC LIMIT ?", (limit,))
            return cursor.fetchall()

    def get_summary(self):
        """Calcula totales para el dashboard."""
        with self.connect() as conn:
            cursor = conn.cursor()
            # Ingresos
            cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo='Ingreso'")
            ingresos = cursor.fetchone()[0] or 0.0
            
            # Gastos (excluyendo pagos de crédito para no duplicar en el flujo de caja operativo)
            cursor.execute("SELECT SUM(monto) FROM transacciones WHERE tipo='Gasto'")
            gastos = cursor.fetchone()[0] or 0.0

            return ingresos, gastos

    def get_credit_info(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT limite_total, saldo_utilizado FROM credito_config LIMIT 1")
            return cursor.fetchone()

    def update_credit_limit(self, new_limit):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE credito_config SET limite_total = ?", (new_limit,))
            conn.commit()

    def update_credit_usage(self, amount, add=True):
        with self.connect() as conn:
            cursor = conn.cursor()
            current = self.get_credit_info()
            saldo_actual = current[1]
            if add:
                new_saldo = saldo_actual + amount
            else:
                new_saldo = max(0, saldo_actual - amount)
            cursor.execute("UPDATE credito_config SET saldo_utilizado = ?", (new_saldo,))
            conn.commit()

    def get_expenses_by_category(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT categoria, SUM(monto) FROM transacciones WHERE tipo='Gasto' GROUP BY categoria")
            return cursor.fetchall()
            
    def add_savings_goal(self, nombre, objetivo):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO metas_ahorro (nombre, monto_objetivo) VALUES (?, ?)", (nombre, objetivo))
            conn.commit()

    def get_savings_goals(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM metas_ahorro")
            return cursor.fetchall()
    
    def update_savings_progress(self, id_meta, monto):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE metas_ahorro SET monto_actual = monto_actual + ? WHERE id = ?", (monto, id_meta))
            conn.commit()


class LoginWindow(ctk.CTkToplevel):
    """Ventana de seguridad simple."""
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.title("Seguridad - Finanzas Personales")
        self.geometry("300x200")
        self.resizable(False, False)
        self.on_success = on_success
        
        # Centrar
        self.update_idletasks()
        width = 300
        height = 200
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        self.label = ctk.CTkLabel(self, text="Ingrese PIN de Acceso (1234)", font=("Roboto", 14))
        self.label.pack(pady=20)

        self.entry = ctk.CTkEntry(self, show="*")
        self.entry.pack(pady=10)

        self.btn = ctk.CTkButton(self, text="Entrar", command=self.check_password)
        self.btn.pack(pady=10)
        
        self.protocol("WM_DELETE_WINDOW", sys.exit)
        self.attributes("-topmost", True)

    def check_password(self):
        # En una app real, esto usaría hashing
        if self.entry.get() == "1234":
            self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Error", "PIN Incorrecto")


class FinanceApp(ctk.CTk):
    """Clase principal de la aplicación."""
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()

        # Configuración de ventana
        self.title("Finanzas Personales - Master System")
        self.geometry("1100x700")
        
        # Grid layout (1x2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Iniciar login
        self.withdraw() # Ocultar main hasta login
        LoginWindow(self, self.start_app)

    def start_app(self):
        self.deiconify()
        self.create_sidebar()
        self.show_dashboard()

    def create_sidebar(self):
        """Panel de navegación lateral."""
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        logo_label = ctk.CTkLabel(self.sidebar_frame, text="Finanzas\nPersonales", font=ctk.CTkFont(size=20, weight="bold"))
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Botones de navegación
        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=self.show_dashboard)
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_ingresos = ctk.CTkButton(self.sidebar_frame, text="Ingresos / Gastos", command=self.show_transactions)
        self.btn_ingresos.grid(row=2, column=0, padx=20, pady=10)

        self.btn_credito = ctk.CTkButton(self.sidebar_frame, text="Crédito Interno", command=self.show_credit)
        self.btn_credito.grid(row=3, column=0, padx=20, pady=10)

        self.btn_ahorros = ctk.CTkButton(self.sidebar_frame, text="Metas de Ahorro", command=self.show_savings)
        self.btn_ahorros.grid(row=4, column=0, padx=20, pady=10)
        
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Tema:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Dark", "Light", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def clear_main_frame(self):
        for widget in self.winfo_children():
            if widget != self.sidebar_frame and not isinstance(widget, tk.Toplevel):
                widget.destroy()

    # --- Vistas ---

    def show_dashboard(self):
        self.clear_main_frame()
        main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(main_frame, text="Resumen Financiero Mensual", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # Tarjetas de Resumen
        ingresos, gastos = self.db.get_summary()
        balance = ingresos - gastos
        cred_lim, cred_used = self.db.get_credit_info()
        cred_disp = cred_lim - cred_used

        cards_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)

        self.create_card(cards_frame, "Ingresos Totales", f"${ingresos:.2f}", "green").pack(side="left", expand=True, fill="both", padx=5)
        self.create_card(cards_frame, "Gastos Totales", f"${gastos:.2f}", "red").pack(side="left", expand=True, fill="both", padx=5)
        self.create_card(cards_frame, "Balance Disponible", f"${balance:.2f}", "#1f6aa5").pack(side="left", expand=True, fill="both", padx=5)
        self.create_card(cards_frame, "Crédito Disponible", f"${cred_disp:.2f}", "orange").pack(side="left", expand=True, fill="both", padx=5)

        # Gráficos
        chart_frame = ctk.CTkFrame(main_frame)
        chart_frame.pack(fill="both", expand=True, pady=20)

        # Gráfico de Gastos por Categoría
        data = self.db.get_expenses_by_category()
        if data:
            categories = [x[0] for x in data]
            amounts = [x[1] for x in data]

            fig = plt.Figure(figsize=(6, 4), dpi=100, facecolor="#2b2b2b")
            ax = fig.add_subplot(111)
            ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90, textprops={'color':"white"})
            ax.set_title("Distribución de Gastos", color="white")
            ax.set_facecolor("#2b2b2b")
            
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="left", fill="both", expand=True, padx=10, pady=10)
        else:
            ctk.CTkLabel(chart_frame, text="No hay datos suficientes para gráficos").pack(expand=True)

    def create_card(self, parent, title, value, color):
        frame = ctk.CTkFrame(parent)
        ctk.CTkLabel(frame, text=title, font=("Arial", 14)).pack(pady=(10, 5))
        ctk.CTkLabel(frame, text=value, font=("Arial", 20, "bold"), text_color=color).pack(pady=(0, 10))
        return frame

    def show_transactions(self):
        self.clear_main_frame()
        main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Gestión de Transacciones", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # Formulario
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", pady=10)

        # Variables
        self.var_tipo = ctk.StringVar(value="Gasto")
        self.var_cat = ctk.StringVar(value="Comida")
        self.var_monto = ctk.StringVar()
        self.var_desc = ctk.StringVar()
        self.var_metodo = ctk.StringVar(value="Efectivo")

        # Inputs
        input_grid = ctk.CTkFrame(form_frame, fg_color="transparent")
        input_grid.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(input_grid, text="Tipo:").grid(row=0, column=0, padx=5)
        ctk.CTkOptionMenu(input_grid, variable=self.var_tipo, values=["Ingreso", "Gasto"]).grid(row=0, column=1, padx=5)

        ctk.CTkLabel(input_grid, text="Categoría:").grid(row=0, column=2, padx=5)
        ctk.CTkOptionMenu(input_grid, variable=self.var_cat, values=["Comida", "Renta", "Transporte", "Servicios", "Entretenimiento", "Salud", "Sueldo", "Freelance", "Otros"]).grid(row=0, column=3, padx=5)

        ctk.CTkLabel(input_grid, text="Monto ($):").grid(row=1, column=0, padx=5, pady=10)
        ctk.CTkEntry(input_grid, textvariable=self.var_monto).grid(row=1, column=1, padx=5, pady=10)

        ctk.CTkLabel(input_grid, text="Método:").grid(row=1, column=2, padx=5)
        ctk.CTkOptionMenu(input_grid, variable=self.var_metodo, values=["Efectivo", "Debito", "CreditoInterno"]).grid(row=1, column=3, padx=5)

        ctk.CTkLabel(input_grid, text="Descripción:").grid(row=2, column=0, padx=5)
        ctk.CTkEntry(input_grid, textvariable=self.var_desc, width=300).grid(row=2, column=1, columnspan=3, sticky="w", padx=5)

        ctk.CTkButton(form_frame, text="Registrar Transacción", command=self.save_transaction, fg_color="green").pack(pady=10)

        # Tabla de Historial (Treeview con estilo Custom)
        self.create_treeview(main_frame)

    def create_treeview(self, parent):
        # Estilos para Treeview oscuro
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        rowheight=25)
        style.map('Treeview', background=[('selected', '#1f6aa5')])
        style.configure("Treeview.Heading", background="#333333", foreground="white", font=('Arial', 10, 'bold'))

        tree_frame = ctk.CTkFrame(parent)
        tree_frame.pack(fill="both", expand=True, pady=10)

        cols = ("ID", "Tipo", "Cat", "Monto", "Fecha", "Desc", "Metodo")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)
        
        for col in cols:
            self.tree.heading(col, text=col)
            if col == "Desc":
                self.tree.column(col, width=200)
            else:
                self.tree.column(col, width=80)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.db.get_transactions():
            self.tree.insert("", "end", values=row)

    def save_transaction(self):
        try:
            monto = float(self.var_monto.get())
            tipo = self.var_tipo.get()
            metodo = self.var_metodo.get()

            # Validación de crédito
            if tipo == "Gasto" and metodo == "CreditoInterno":
                lim, used = self.db.get_credit_info()
                if used + monto > lim:
                    messagebox.showerror("Error", f"Límite de crédito excedido. Disponible: ${lim - used:.2f}")
                    return

            self.db.add_transaction(
                tipo,
                self.var_cat.get(),
                monto,
                datetime.now().strftime("%Y-%m-%d"),
                self.var_desc.get(),
                metodo
            )
            self.var_monto.set("")
            self.var_desc.set("")
            self.refresh_table()
            messagebox.showinfo("Éxito", "Transacción guardada correctamente")
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser numérico")

    def show_credit(self):
        self.clear_main_frame()
        main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        ctk.CTkLabel(main_frame, text="Sistema de Crédito Interno", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 20))

        lim, used = self.db.get_credit_info()
        disp = lim - used
        percent = used / lim if lim > 0 else 0

        # Barra de progreso visual
        credit_card = ctk.CTkFrame(main_frame, fg_color="#3a3a3a", border_color="white", border_width=2)
        credit_card.pack(fill="x", pady=20, padx=50)

        ctk.CTkLabel(credit_card, text=f"Límite Total: ${lim:.2f}", font=("Arial", 16)).pack(pady=10)
        
        prog = ctk.CTkProgressBar(credit_card, width=400, height=20)
        prog.set(percent)
        if percent > 0.9: prog.configure(progress_color="red")
        else: prog.configure(progress_color="green")
        prog.pack(pady=10)

        ctk.CTkLabel(credit_card, text=f"Usado: ${used:.2f}  |  Disponible: ${disp:.2f}", font=("Arial", 14, "bold")).pack(pady=10)

        # Acciones
        actions_frame = ctk.CTkFrame(main_frame)
        actions_frame.pack(pady=20)

        # Ajustar Límite
        self.new_limit_var = ctk.StringVar()
        ctk.CTkEntry(actions_frame, textvariable=self.new_limit_var, placeholder_text="Nuevo Límite").grid(row=0, column=0, padx=10)
        ctk.CTkButton(actions_frame, text="Actualizar Límite", command=self.update_limit).grid(row=0, column=1, padx=10)

        # Pagar Crédito
        ctk.CTkLabel(main_frame, text="Para pagar el crédito, registre una transacción tipo 'Gasto' con método 'Efectivo/Banco' \npero seleccione una categoría especial o simplemente use el botón abajo que registrará un 'PagoCredito'.").pack(pady=10)
        
        self.pay_credit_var = ctk.StringVar()
        pay_frame = ctk.CTkFrame(main_frame)
        pay_frame.pack(pady=10)
        ctk.CTkEntry(pay_frame, textvariable=self.pay_credit_var, placeholder_text="Monto a Pagar").pack(side="left", padx=10)
        ctk.CTkButton(pay_frame, text="Realizar Pago a Crédito", fg_color="green", command=self.pay_credit).pack(side="left", padx=10)

    def update_limit(self):
        try:
            val = float(self.new_limit_var.get())
            self.db.update_credit_limit(val)
            self.show_credit() # Recargar
        except ValueError:
            messagebox.showerror("Error", "Número inválido")

    def pay_credit(self):
        try:
            val = float(self.pay_credit_var.get())
            self.db.add_transaction("PagoCredito", "Financiero", val, datetime.now().strftime("%Y-%m-%d"), "Abono a Crédito Interno", "Transferencia")
            self.show_credit()
            messagebox.showinfo("Pago", "Pago registrado y saldo liberado.")
        except ValueError:
            messagebox.showerror("Error", "Monto inválido")

    def show_savings(self):
        self.clear_main_frame()
        main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="Metas de Ahorro", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # Agregar Meta
        add_frame = ctk.CTkFrame(main_frame)
        add_frame.pack(fill="x", pady=10)
        
        self.goal_name = ctk.StringVar()
        self.goal_target = ctk.StringVar()
        
        ctk.CTkEntry(add_frame, textvariable=self.goal_name, placeholder_text="Nombre (ej. Auto Nuevo)").pack(side="left", padx=10, expand=True, fill="x")
        ctk.CTkEntry(add_frame, textvariable=self.goal_target, placeholder_text="Monto Objetivo").pack(side="left", padx=10)
        ctk.CTkButton(add_frame, text="Crear Meta", command=self.create_goal).pack(side="left", padx=10)

        # Lista de Metas
        goals_scroll = ctk.CTkScrollableFrame(main_frame, height=400)
        goals_scroll.pack(fill="both", expand=True)

        goals = self.db.get_savings_goals()
        for g in goals:
            gid, name, target, current = g
            pct = current / target if target > 0 else 0
            
            card = ctk.CTkFrame(goals_scroll)
            card.pack(fill="x", pady=5)
            
            ctk.CTkLabel(card, text=f"{name}", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=(5,0))
            ctk.CTkProgressBar(card).pack(fill="x", padx=10, pady=5) # Solo visual, requeriría configurar valor
            
            lbl_progress = ctk.CTkLabel(card, text=f"Progreso: ${current:.2f} / ${target:.2f} ({pct*100:.1f}%)")
            lbl_progress.pack(anchor="w", padx=10)
            
            btn_add = ctk.CTkButton(card, text="Abonar $50", height=25, width=100, command=lambda i=gid: self.add_savings(i, 50))
            btn_add.pack(anchor="e", padx=10, pady=5)

    def create_goal(self):
        try:
            target = float(self.goal_target.get())
            name = self.goal_name.get()
            if name:
                self.db.add_savings_goal(name, target)
                self.show_savings()
        except:
            messagebox.showerror("Error", "Datos inválidos")

    def add_savings(self, gid, amount):
        self.db.update_savings_progress(gid, amount)
        self.show_savings()

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()