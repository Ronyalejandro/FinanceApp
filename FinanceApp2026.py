import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import json
import hashlib
import hmac
from datetime import datetime
try:
    import matplotlib.pyplot as plt  # type: ignore
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # type: ignore
    HAS_MATPLOTLIB = True
except Exception:
    # matplotlib no está disponible en el entorno; la aplicación
    # seguirá funcionando pero sin la visualización de gráficos.
    plt = None
    FigureCanvasTkAgg = None
    HAS_MATPLOTLIB = False
import sys
import os
from services.transaction_service import TransactionService

# Path para almacenar hash de PIN fuera del repositorio
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".financeapp_config.json")

def _save_pin_hash(pin: str) -> None:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100_000)
    data = {"salt": salt.hex(), "hash": dk.hex()}
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f)
        try:
            os.chmod(CONFIG_PATH, 0o600)
        except OSError:
            # Ignorar en sistemas Windows que no admiten chmod igual
            pass
    except OSError:
        # No exponemos detalles al usuario aquí; el creador puede ver logs
        raise

def _verify_pin(pin: str) -> bool:
    if not os.path.exists(CONFIG_PATH):
        return False
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    salt = bytes.fromhex(data["salt"])
    stored = bytes.fromhex(data["hash"])
    dk = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100_000)
    return hmac.compare_digest(dk, stored)

# --- Configuración Global ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Importar DatabaseManager desde el módulo refactorizado
from db.database import DatabaseManager

class LoginWindow(ctk.CTkToplevel):
    """Ventana de seguridad para autenticación mediante PIN.

    El PIN se guarda como hash PBKDF2 en el archivo de configuración
    del usuario (`~/.financeapp_config.json`). Si no existe, la ventana
    solicita crear el PIN inicial.
    """
    def __init__(self, parent, on_success) -> None:
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

        # Si no existe configuración, pedimos crear PIN inicial
        self.first_time = not os.path.exists(CONFIG_PATH)
        if self.first_time:
            self.label = ctk.CTkLabel(self, text="Crear PIN de Acceso", font=("Roboto", 14))
        else:
            self.label = ctk.CTkLabel(self, text="Ingrese PIN de Acceso", font=("Roboto", 14))
        self.label.pack(pady=20)

        self.entry = ctk.CTkEntry(self, show="*")
        self.entry.pack(pady=10)

        btn_text = "Crear" if self.first_time else "Entrar"
        btn_cmd = self.create_pin if self.first_time else self.check_password
        self.btn = ctk.CTkButton(self, text=btn_text, command=btn_cmd)
        self.btn.pack(pady=10)
        
        self.protocol("WM_DELETE_WINDOW", sys.exit)
        self.attributes("-topmost", True)

    def check_password(self) -> None:
        """Verifica el PIN ingresado contra el hash almacenado.

        Muestra mensajes genéricos al usuario en caso de error.
        """
        try:
            if _verify_pin(self.entry.get()):
                self.on_success()
                self.destroy()
            else:
                messagebox.showerror("Error", "PIN Incorrecto")
        except (OSError, ValueError, json.JSONDecodeError):
            messagebox.showerror("Error", "Error al verificar PIN")

    def create_pin(self) -> None:
        """Crea y almacena el hash del PIN ingresado (mínimo 4 caracteres)."""
        pin = self.entry.get()
        if not pin or len(pin) < 4:
            messagebox.showerror("Error", "El PIN debe tener al menos 4 caracteres")
            return
        try:
            _save_pin_hash(pin)
            messagebox.showinfo("Listo", "PIN creado. Iniciando aplicación.")
            self.on_success()
            self.destroy()
        except OSError:
            messagebox.showerror("Error", "No se pudo guardar el PIN")


class FinanceApp(ctk.CTk):
    """Clase principal de la aplicación y controlador de la UI.

    Contiene la inicialización de la ventana principal, la navegación
    y los handlers que delegan en `TransactionService` para la lógica
    financiera.
    """
    def __init__(self) -> None:
        super().__init__()
        self.db = DatabaseManager()
        # Servicio que encapsula validaciones y delega operaciones atómicas en DB
        self.tx_service = TransactionService(self.db)

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
        """Muestra la ventana principal tras autenticación."""
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

    def change_appearance_mode_event(self, new_appearance_mode: str) -> None:
        """Cambia el modo de apariencia del tema (Dark/Light/System)."""
        ctk.set_appearance_mode(new_appearance_mode)

    def clear_main_frame(self) -> None:
        """Limpia widgets del área principal sin tocar la barra lateral ni toplevels."""
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

        # Gráfico de Gastos por Categoría (si matplotlib está disponible)
        data = self.db.get_expenses_by_category()
        if HAS_MATPLOTLIB and data:
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
        elif data:
            ctk.CTkLabel(chart_frame, text="Gráficos deshabilitados (matplotlib no disponible)").pack(expand=True)
        else:
            ctk.CTkLabel(chart_frame, text="No hay datos suficientes para gráficos").pack(expand=True)

    def create_card(self, parent, title: str, value: str, color: str) -> ctk.CTkFrame:
        """Crea una tarjeta visual resumen usada en el dashboard.

        Retorna el frame creado para su colocado en el layout.
        """
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

    def create_treeview(self, parent) -> None:
        """Crea y configura el `Treeview` para mostrar el historial de transacciones."""
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
        """Refresca el contenido de la tabla de transacciones desde la BD."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.db.get_transactions():
            self.tree.insert("", "end", values=row)

    def save_transaction(self) -> None:
        """Handler que toma datos del formulario y crea la transacción.

        Las validaciones de negocio (límite de crédito) se realizan en el
        `TransactionService` y se reportan mediante `ValueError`.
        """
        try:
            monto = float(self.var_monto.get())
            tipo = self.var_tipo.get()
            metodo = self.var_metodo.get()
            # Delegar la creación al servicio (operación atómica en BD)
            self.tx_service.create_transaction(
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
        except ValueError as e:
            # Puede ser monto inválido o límite de crédito excedido
            messagebox.showerror("Error", str(e))
        except sqlite3.Error:
            messagebox.showerror("Error", "Error al guardar la transacción")

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
        """Registra un pago de crédito utilizando el servicio transaccional."""
        try:
            val = float(self.pay_credit_var.get())
            # Usar servicio para operar de forma atómica
            self.tx_service.create_transaction("PagoCredito", "Financiero", val, datetime.now().strftime("%Y-%m-%d"), "Abono a Crédito Interno", "Transferencia")
            self.show_credit()
            messagebox.showinfo("Pago", "Pago registrado y saldo liberado.")
        except ValueError:
            messagebox.showerror("Error", "Monto inválido")
        except sqlite3.Error:
            messagebox.showerror("Error", "Error al procesar el pago")

    def show_savings(self):
        """Muestra y permite gestionar las metas de ahorro del usuario."""
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
            prog = ctk.CTkProgressBar(card)
            prog.set(pct)
            prog.pack(fill="x", padx=10, pady=5)
            
            lbl_progress = ctk.CTkLabel(card, text=f"Progreso: ${current:.2f} / ${target:.2f} ({pct*100:.1f}%)")
            lbl_progress.pack(anchor="w", padx=10)
            
            btn_add = ctk.CTkButton(card, text="Abonar $50", height=25, width=100, command=lambda i=gid: self.add_savings(i, 50))
            btn_add.pack(anchor="e", padx=10, pady=5)

    def create_goal(self):
        """Crea una nueva meta de ahorro validando entrada del usuario."""
        try:
            target = float(self.goal_target.get())
            name = self.goal_name.get()
            if not name:
                messagebox.showerror("Error", "El nombre de la meta es obligatorio")
                return
            self.db.add_savings_goal(name, target)
            self.show_savings()
        except ValueError:
            messagebox.showerror("Error", "Monto inválido")
        except sqlite3.Error:
            messagebox.showerror("Error", "Error al guardar la meta")

    def add_savings(self, gid, amount):
        """Abona una cantidad fija a la meta identificada por `gid`."""
        self.db.update_savings_progress(gid, amount)
        self.show_savings()

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()