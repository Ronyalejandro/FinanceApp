"""Implementación de la Vista de Objetivos: Plan por Objetivos."""
import customtkinter as ctk
from tkinter import messagebox
from utils.constants import *
from datetime import datetime
import math
import random

class GoalsView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.db = db
        # Alinear con el espaciado de RecurringView
        self.grid(row=0, column=1, sticky="nsew", padx=40, pady=30)

        self._avg_savings = self._calculate_avg_savings()
        self._setup_ui()

    def _calculate_avg_savings(self):
        """Estima la capacidad de ahorro mensual basada en los últimos 90 días.
        Heurística: (Ingresos Totales - Gastos Totales) / 3
        """
        ing, gast = self.db.get_summary()
        balance = ing - gast
        if balance > 0:
            return balance / 3 # Estimación aproximada
        return 0

    def _setup_ui(self):
        # Encabezado (Usando pack para coincidir con RecurringView)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(header, text="Objetivos de Ahorro", font=FONT_TITLE_MAIN, text_color=COLOR_TEXT_WHITE).pack(side="left")
        
        # Formulario para agregar nuevo (En línea, EXACTAMENTE como RecurringView)
        add_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        add_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(add_frame, text="Nuevo Objetivo", font=FONT_SUBTITLE, text_color=theme_color(COLOR_TEXT_WHITE)).pack(anchor="w", padx=20, pady=(15, 10))

        form_grid = ctk.CTkFrame(add_frame, fg_color="transparent")
        form_grid.pack(fill="x", padx=20, pady=(0, 15))

        self.name_var = ctk.StringVar()
        self.target_var = ctk.StringVar()

        # Etiquetas y campos con el mismo espaciado que RecurringView
        ctk.CTkLabel(form_grid, text="Nombre:", text_color=theme_color(COLOR_TEXT_WHITE)).pack(side="left", padx=(0, 5))
        ctk.CTkEntry(form_grid, textvariable=self.name_var, placeholder_text="Ej. Viaje a Japón", width=180).pack(side="left", padx=(0, 15))
        
        ctk.CTkLabel(form_grid, text="Monto Meta:", text_color=theme_color(COLOR_TEXT_WHITE)).pack(side="left", padx=(0, 5))
        ctk.CTkEntry(form_grid, textvariable=self.target_var, placeholder_text="Ej. 2000", width=100).pack(side="left", padx=(0, 15))

        ctk.CTkButton(form_grid, text="Añadir", command=self._handle_add_goal, fg_color=theme_color(COLOR_ACCENT_BLUE), width=100).pack(side="left")

        # Cuadrícula desplazable para tarjetas (Usando pack)
        self.cards_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.cards_scroll.pack(fill="both", expand=True, pady=10)
        # Necesitamos columnas para las tarjetas dentro del marco desplazable
        self.cards_scroll.grid_columnconfigure((0, 1, 2), weight=1)

        self.refresh_plans()

    def _handle_add_goal(self):
        try:
            name = self.name_var.get()
            target_str = self.target_var.get()
            if not name or not target_str:
                raise ValueError("Campos obligatorios")
            
            t = float(target_str)
            if t <= 0:
                raise ValueError("Monto debe ser > 0")
            
            # Asignar automáticamente un color neón aleatorio
            neon_colors = ["#00FFFF", "#FF00FF", "#00FF00", "#FFFF00", "#FF0099", "#9D00FF"]
            color = random.choice(neon_colors)
            
            self.db.create_plan(name, t, "2026-12-31", color) # Fecha provisional
            
            # Reiniciar formulario
            self.name_var.set("")
            self.target_var.set("")
            self.refresh_plans()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)

    def refresh_plans(self):
        for w in self.cards_scroll.winfo_children():
            w.destroy()

        plans = self.db.get_plans()
        
        # Diseño: 3 columnas
        col = 0
        row = 0
        
        for plan in plans:
            # Plan: id, nombre, meta, actual, fecha, color
            pid, name, target, current, date_limit, color = plan
            self._create_plan_card(pid, name, target, current, date_limit, color, row, col)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _create_plan_card(self, pid, name, target, current, date_limit, color, r, c):
        # Marco de la Tarjeta
        card = ctk.CTkFrame(self.cards_scroll, fg_color="#161B22", corner_radius=15, 
                            border_width=2, border_color=color)
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
        
        # Acciones: Botón Eliminar (Arriba a la derecha, estilo RecurringView)
        delete_btn = ctk.CTkButton(card, text="🗑", width=30, height=30, fg_color="transparent", 
                                   text_color=theme_color(COLOR_ACCENT_RED), hover_color=theme_color(COLOR_BTN_HOVER),
                                   font=("Arial", 16),
                                   command=lambda i=pid: self._confirm_delete(i, name))
        delete_btn.place(relx=0.98, rely=0.02, anchor="ne")
        
        # Cabecera de Tarjeta: Icono + Título
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        icon = ctk.CTkLabel(header_frame, text="⬤", font=("Arial", 16), text_color=color)
        icon.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(header_frame, text=name, font=FONT_SUBTITLE, text_color=COLOR_TEXT_WHITE).pack(side="left")
        
        # Barra de Progreso
        pct = current / target if target > 0 else 0
        if pct > 1: pct = 1
        
        prog_bar = ctk.CTkProgressBar(card, height=10, corner_radius=5, progress_color=color)
        prog_bar.set(pct)
        prog_bar.pack(fill="x", padx=15, pady=10)
        
        # Estadísticas
        stats_frame = ctk.CTkFrame(card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=5)
        
        missing = target - current
        time_msg = "¡Completado!" if missing <= 0 else self._calculate_time_remaining(missing)
        
        ctk.CTkLabel(stats_frame, text=f"{int(pct*100)}%", font=("Inter", 12, "bold"), text_color=color).pack(side="left")
        ctk.CTkLabel(stats_frame, text=f"Faltan ${missing:,.0f}", font=("Inter", 12), text_color=COLOR_TEXT_GRAY).pack(side="right")
        
        # Parte Inferior: Tiempo + Acción
        bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        ctk.CTkLabel(bottom_frame, text=time_msg, font=("Inter", 10, "italic"), text_color="#666").pack(anchor="w", pady=(0, 10))
        
        if missing > 0:
            btn = ctk.CTkButton(bottom_frame, text="Aportar", height=28, fg_color="transparent", 
                                border_width=1, border_color=color, text_color=color, hover_color="#222",
                                command=lambda i=pid: self._show_deposit_dialog(i, name, color))
            btn.pack(fill="x")
        else:
            ctk.CTkButton(bottom_frame, text="¡Meta Lograda!", height=28, fg_color=color, text_color="#000", state="disabled").pack(fill="x")

    def _calculate_time_remaining(self, missing_amount):
        if self._avg_savings <= 0:
            return "Indefinido (Sin ahorro mensual)"
        months = math.ceil(missing_amount / self._avg_savings)
        return f"~{months} meses restantes"

    def _show_deposit_dialog(self, pid, name, color):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Aportar a {name}")
        dialog.geometry("300x200")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text=f"Aportar a: {name}", font=("Inter", 14)).pack(pady=20)
        
        amt_var = ctk.StringVar()
        ctk.CTkEntry(dialog, textvariable=amt_var, placeholder_text="Monto a depositar").pack(pady=10)
        
        def confirm():
            try:
                val = float(amt_var.get())
                if val <= 0: raise ValueError
                self.db.deposit_to_plan(pid, val)
                messagebox.showinfo("Éxito", f"Aportado ${val} a {name}", parent=dialog)
                dialog.destroy()
                self.refresh_plans()
            except ValueError as e:
                messagebox.showerror("Error", f"Error: {e}", parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", f"Fallo BD: {e}", parent=dialog)

        ctk.CTkButton(dialog, text="Confirmar", fg_color=color, text_color="#000", command=confirm).pack(pady=20)

    def _confirm_delete(self, pid, name):
        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que deseas eliminar el plan '{name}'?\nEsta acción no se puede deshacer.", parent=self):
            try:
                self.db.delete_plan(pid)
                self.refresh_plans()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}", parent=self)

