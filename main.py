"""Punto de Entrada de la Aplicación."""
import os
import sys
import customtkinter as ctk

# Asegurar que se encuentren 'utils' y otros módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tkinter import messagebox
import traceback
from utils.constants import *
from config import resource_path, DB_PATH
from db.database import DatabaseManager
from services.transaction_service import TransactionService

def global_exception_handler(exctype, value, tb):
    """Manejo de errores global para mostrar un messagebox en producción."""
    error_msg = "".join(traceback.format_exception(exctype, value, tb))
    print(error_msg) # Mantener en consola para depuración local
    messagebox.showerror("Error Crítico de Aplicación", 
                         f"Ha ocurrido un error inesperado:\n\n{value}\n\nConsulte el log para más detalles.")
    # sys.exit(1) # Opcional: Cerrar la app tras un error crítico

sys.excepthook = global_exception_handler

from ui.login import LoginWindow
from ui.components.sidebar import Sidebar
from ui.views.dashboard import DashboardView
from ui.views.transactions import TransactionsView
from ui.views.credit import CreditView
from ui.views.goals import GoalsView
from ui.views.settings import SettingsView
from ui.views.projections import ProjectionsView
from ui.views.recurring import RecurringView
from ui.views.reports import ReportsView

# Configuración Global
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class FinanceApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        
        # --- Configuración de Fondo ---
        self.configure(fg_color=COLOR_BACKGROUND)
        self.title("FinanceApp")
        self.geometry("1400x800")
        
        # --- Configuración de Icono ---
        try:
            icon_path = resource_path("app_logo.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")
        
        self.db = DatabaseManager()
        self.tx_service = TransactionService(self.db)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.withdraw()
        LoginWindow(self, self.start_app)

    def start_app(self):
        self.deiconify()
        self.create_sidebar()
        self.show_view("dashboard")

    def create_sidebar(self):
        self.sidebar = Sidebar(self, self.show_view)

    def show_view(self, view_name):
        # Limpiar vista actual (excepto sidebar)
        for widget in self.winfo_children():
            if not isinstance(widget, Sidebar) and not isinstance(widget, ctk.CTkToplevel):
                widget.destroy()

        # Cargar nueva vista
        if view_name == "dashboard":
            DashboardView(self, self.db)
        elif view_name == "transactions":
            TransactionsView(self, self.db, self.tx_service)
        elif view_name == "credit":
            CreditView(self, self.db, self.tx_service)
        elif view_name == "savings":
            GoalsView(self, self.db)
        elif view_name == "settings":
            SettingsView(self, self.db)
        elif view_name == "projections":
            ProjectionsView(self, self.db)
        elif view_name == "recurring":
            RecurringView(self, self.db)
        elif view_name == "reports":
            ReportsView(self, self.db)

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
