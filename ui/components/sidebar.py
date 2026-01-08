"""Sidebar component for navigation."""
import customtkinter as ctk
from utils.constants import *

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, command_callback):
        super().__init__(parent, width=200, corner_radius=0, fg_color=COLOR_SIDEBAR, border_width=1, border_color=COLOR_SIDEBAR_BORDER)
        self.command_callback = command_callback
        
        self.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.grid_rowconfigure(6, weight=1)

        self._create_widgets()

    def _create_widgets(self):
        logo_label = ctk.CTkLabel(self, text="FINANZAS", font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"), text_color=COLOR_TEXT_WHITE)
        logo_label.grid(row=0, column=0, padx=20, pady=(40, 30))

        self.btn_dashboard = self._create_nav_button("Dashboard", "dashboard", 1)
        self.btn_ingresos = self._create_nav_button("Transactions", "transactions", 2)
        self.btn_credito = self._create_nav_button("Credit Line", "credit", 3)
        self.btn_ahorros = self._create_nav_button("Savings Goals", "savings", 4)
        self.btn_settings = self._create_nav_button("Settings", "settings", 5)
        
        self.appearance_mode_label = ctk.CTkLabel(self, text="Tema:", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self, values=["Dark", "Light", "System"],
                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

    def _create_nav_button(self, text, view_name, row):
        btn = ctk.CTkButton(self, text=text, 
                            command=lambda: self.command_callback(view_name), 
                            height=45, corner_radius=0,
                            fg_color="transparent", hover_color="#222222", anchor="w")
        btn.grid(row=row, column=0, padx=0, pady=2, sticky="ew")
        return btn

    def change_appearance_mode_event(self, new_appearance_mode: str) -> None:
        ctk.set_appearance_mode(new_appearance_mode)
