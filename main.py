"""Main Application Entry Point."""
import os
import sys
import customtkinter as ctk

# Ensure 'utils' and other modules can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.constants import *
from db.database import DatabaseManager
from services.transaction_service import TransactionService

from ui.login import LoginWindow
from ui.components.sidebar import Sidebar
from ui.views.dashboard import DashboardView
from ui.views.transactions import TransactionsView
from ui.views.credit import CreditView
from ui.views.savings import SavingsView
from ui.views.settings import SettingsView

# Global Config
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class FinanceApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        
        # --- Configuración de Fondo ---
        self.configure(fg_color=COLOR_BACKGROUND)
        self.title("FINANCE")
        self.geometry("1400x800")
        
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
            SavingsView(self, self.db)
        elif view_name == "settings":
            SettingsView(self, self.db)

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()
