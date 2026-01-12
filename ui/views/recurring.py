"""Vista de Transacciones Recurrentes."""
import customtkinter as ctk
from tkinter import messagebox
from utils.constants import *

class RecurringView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.db = db
        self.grid(row=0, column=1, sticky="nsew", padx=40, pady=30)
        self._setup_ui()

    def _setup_ui(self):
        # Encabezado
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 30))
        ctk.CTkLabel(header, text="Suscripciones y Pagos Fijos", font=FONT_TITLE_MAIN, text_color=COLOR_TEXT_WHITE).pack(side="left")
        
        # Formulario para agregar nueva
        add_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        add_frame.pack(fill="x", pady=10)
        
        # Cabecera para sección de agregar
        ctk.CTkLabel(add_frame, text="Nueva Suscripción", font=FONT_SUBTITLE, text_color=theme_color(COLOR_TEXT_WHITE)).pack(anchor="w", padx=20, pady=(15, 10))

        # Cuadrícula de formulario con etiquetas explícitas
        form_grid = ctk.CTkFrame(add_frame, fg_color="transparent")
        form_grid.pack(fill="x", padx=20, pady=(0, 15))

        self.name_var = ctk.StringVar()
        self.amount_var = ctk.StringVar()
        self.day_var = ctk.StringVar()
        self.cat_var = ctk.StringVar(value="Suscripción")

        # Nombre de la suscripción
        ctk.CTkLabel(form_grid, text="Nombre:", text_color=theme_color(COLOR_TEXT_WHITE)).pack(side="left", padx=(0, 5))
        ctk.CTkEntry(form_grid, textvariable=self.name_var, placeholder_text="Ej. Netflix", width=150).pack(side="left", padx=(0, 10))
        # Monto a pagar
        ctk.CTkLabel(form_grid, text="Monto:", text_color=theme_color(COLOR_TEXT_WHITE)).pack(side="left", padx=(0, 5))
        ctk.CTkEntry(form_grid, textvariable=self.amount_var, placeholder_text="Ej. 12.99", width=80).pack(side="left", padx=(0, 10))
        # Día del mes
        ctk.CTkLabel(form_grid, text="Día:", text_color=theme_color(COLOR_TEXT_WHITE)).pack(side="left", padx=(0, 5))
        ctk.CTkEntry(form_grid, textvariable=self.day_var, placeholder_text="1-31", width=60).pack(side="left", padx=(0, 10))
        # Categoría
        ctk.CTkLabel(form_grid, text="Categoría:", text_color=theme_color(COLOR_TEXT_WHITE)).pack(side="left", padx=(0, 5))
        ctk.CTkComboBox(form_grid, values=CATEGORIAS, variable=self.cat_var, width=120).pack(side="left", padx=(0, 10))

        # Botón para añadir la suscripción
        ctk.CTkButton(form_grid, text="Añadir", command=self.add_recurring, fg_color=theme_color(COLOR_ACCENT_BLUE), width=100).pack(side="left")
        
        # Lista
        self.list_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_scroll.pack(fill="both", expand=True)
        
        self.refresh_list()
        
    def refresh_list(self):
        for w in self.list_scroll.winfo_children():
            w.destroy()
            
        recurrings = self.db.get_recurring()
        
        if not recurrings:
            ctk.CTkLabel(self.list_scroll, text="No hay suscripciones activas.", text_color=COLOR_TEXT_GRAY).pack(pady=40)
            return

        for r in recurrings:
            rid, name, amount, day, cat, active = r
            self._create_row(rid, name, amount, day, cat)
            
    def _create_row(self, rid, name, amount, day, cat):
        row = ctk.CTkFrame(self.list_scroll, fg_color=COLOR_CARD_BG, corner_radius=10)
        row.pack(fill="x", pady=5)
        
        inner = ctk.CTkFrame(row, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=10)
        
        # Información
        ctk.CTkLabel(inner, text=name, font=("Inter", 14, "bold"), text_color="white", width=150, anchor="w").pack(side="left")
        ctk.CTkLabel(inner, text=f"${amount:.2f}", font=("Inter", 14), text_color=COLOR_ACCENT_RED, width=100, anchor="w").pack(side="left")
        ctk.CTkLabel(inner, text=f"Día {day}", font=("Inter", 12), text_color=COLOR_TEXT_GRAY, width=80).pack(side="left")
        ctk.CTkLabel(inner, text=cat, font=("Inter", 12), text_color=COLOR_TEXT_GRAY, width=120).pack(side="left")
        
        # Acciones
        # Botón de eliminar suscripción con colores adaptativos
        ctk.CTkButton(inner, text="🗑", width=30, height=30, fg_color="transparent", text_color=theme_color(COLOR_ACCENT_RED), hover_color=theme_color(COLOR_BTN_HOVER),
                       command=lambda: self.delete_recurring(rid)).pack(side="right")
                      
    def add_recurring(self):
        try:
            name = self.name_var.get()
            amt = float(self.amount_var.get())
            day = int(self.day_var.get())
            if not name or amt <= 0 or not (1 <= day <= 31): raise ValueError
            
            self.db.add_recurring(name, amt, day, self.cat_var.get())
            self.name_var.set("")
            self.amount_var.set("")
            self.day_var.set("")
            self.refresh_list()
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos (Monto > 0, Día 1-31)")
            
    def delete_recurring(self, rid):
        if messagebox.askyesno("Confirmar", "¿Eliminar suscripción?"):
            self.db.delete_recurring(rid)
            self.refresh_list()
