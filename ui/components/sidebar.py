"""Componente de barra lateral (Sidebar) para la navegación."""
import customtkinter as ctk
from utils.constants import *

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, command_callback):
        super().__init__(parent, width=200, corner_radius=0, fg_color=COLOR_SIDEBAR, border_width=1, border_color=COLOR_SIDEBAR_BORDER)
        self.command_callback = command_callback
        self.buttons = {}
        self.indicators = {}
        self.active_view = "dashboard" # Vista activa por defecto

        self.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.grid_rowconfigure(6, weight=1)

        self._create_widgets()
        self._select_button("dashboard")

    def _create_widgets(self):
        logo_label = ctk.CTkLabel(self, text="FINANCE", font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"), text_color=theme_color(COLOR_TEXT_WHITE))
        logo_label.grid(row=0, column=0, padx=20, pady=(40, 30))

        self._create_nav_button("FinanceApp", "dashboard", 1)
        self._create_nav_button("Transacciones", "transactions", 2)
        self._create_nav_button("Mis Suscripciones", "recurring", 3)
        self._create_nav_button("Cashea", "credit", 4)
        self._create_nav_button("Objetivos", "savings", 5)
        self._create_nav_button("Reportes", "reports", 6)
        self._create_nav_button("Proyecciones", "projections", 7)
        self._create_nav_button("Configuración", "settings", 8)
        
        self.appearance_mode_label = ctk.CTkLabel(self, text="Tema:", anchor="w")
        self.appearance_mode_label.grid(row=9, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self, values=["Oscuro", "Claro", "Sistema"],
                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=10, column=0, padx=20, pady=(10, 20))

    def _create_nav_button(self, text, view_name, row):
        # Franja indicadora (oculta por defecto)
        indicator = ctk.CTkFrame(self, width=4, height=40, corner_radius=0, fg_color="transparent")
        indicator.grid(row=row, column=0, sticky="w", padx=0, pady=2)
        self.indicators[view_name] = indicator

        # Botón
        btn = ctk.CTkButton(self, text=text, 
                            command=lambda v=view_name: self._handle_click(v), 
                            height=45, corner_radius=0,
                            fg_color="transparent", hover_color=theme_color(COLOR_BTN_HOVER), anchor="w")
        # Pad a la izquierda para dejar espacio visual para el indicador o simplemente superponer
        btn.grid(row=row, column=0, padx=(10, 0), pady=2, sticky="ew") 
        self.buttons[view_name] = btn
        return btn

    def _handle_click(self, view_name):
        self._select_button(view_name)
        self.command_callback(view_name)

    def _select_button(self, view_name):
        # Restablecer anterior
        if self.active_view in self.buttons:
            self.buttons[self.active_view].configure(text_color="#aaaaaa", fg_color="transparent")
            self.indicators[self.active_view].configure(fg_color="transparent")

        self.active_view = view_name
        
        # Activar nuevo
        if view_name in self.buttons:
            # Texto iluminado (Cian) + Indicador
            self.buttons[view_name].configure(text_color=theme_color(COLOR_ACCENT_GREEN), fg_color=theme_color(COLOR_BTN_ACTIVE)) # Fondo ligeramente más claro
            self.indicators[view_name].configure(fg_color=COLOR_ACCENT_GREEN)

    def change_appearance_mode_event(self, new_appearance_mode: str) -> None:
        if new_appearance_mode == "Oscuro":
            ctk.set_appearance_mode("Dark")
        elif new_appearance_mode == "Claro":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("System")
