"""Goals View Implementation: Plan by Objectives."""
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
        # Grid layout for the main view
        self.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Scrollable part

        self._avg_savings = self._calculate_avg_savings()
        self._setup_ui()

    def _calculate_avg_savings(self):
        """Estimate monthly savings capacity based on last 90 days."""
        # This is a simple estimation: (Total Income - Total Expenses) / 3 months
        # A more robust one would query monthly aggregates.
        # For now, let's look at global summary or short term history.
        # Let's use get_summary() which is global, potentially too broad if app used for years.
        # Better: let's assume a default or calculate from last month if possible.
        # To keep it fast, we'll try to get expenses by category and infer.
        # Actually, let's use a simple heuristic for now: 20% of income if no data, 
        # or just (Income - Expense) if positive.
        
        # We'll fetch global for now as a baseline.
        ing, gast = self.db.get_summary()
        balance = ing - gast
        # Assuming app usage time is tricky. Let's just say Balance / 12 for conservative estimate if long term?
        # Or better: let's just use current Balance as "Available to allocate" but that doesn't help with "Time to complete".
        # "Time to complete" implies FUTURE flux.
        # Let's use a fixed placeholder logic if no historical monthly data is easy:
        # If Balance > 0, assume we can save 10% of Balance per month? No that's weird.
        # Let's stick to: (Total Income - Total Expense) / 3 (assuming 3 months usage)
        # Improvement: Add get_monthly_average to DB later.
        if balance > 0:
            return balance / 3 # Rough estimate
        return 0

    def _setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        ctk.CTkLabel(header, text="Objetivos", font=FONT_TITLE_MAIN, text_color=COLOR_TEXT_WHITE).pack(side="left")
        
        ctk.CTkButton(header, text="+ Nuevo Objetivo", command=self._show_add_dialog, 
                      fg_color=COLOR_ACCENT_BLUE, width=120).pack(side="right")

        # Scrollable Grid for Cards
        self.cards_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.cards_scroll.grid(row=1, column=0, sticky="nsew")
        self.cards_scroll.grid_columnconfigure((0, 1, 2), weight=1) # 3 columns responsive

        self.refresh_plans()

    def refresh_plans(self):
        for w in self.cards_scroll.winfo_children():
            w.destroy()

        plans = self.db.get_plans()
        
        # Layout: 3 columns
        col = 0
        row = 0
        
        for plan in plans:
            # Plan: id, name, target, current, date, color
            pid, name, target, current, date_limit, color = plan
            self._create_plan_card(pid, name, target, current, date_limit, color, row, col)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1

    def _create_plan_card(self, pid, name, target, current, date_limit, color, r, c):
        # Card Frame
        card = ctk.CTkFrame(self.cards_scroll, fg_color="#161B22", corner_radius=15, 
                            border_width=2, border_color=color)
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
        
        # Card Header: Icon + Title
        # Using a simple circle label as 'icon' with plan color
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        icon = ctk.CTkLabel(header_frame, text="⬤", font=("Arial", 16), text_color=color)
        icon.pack(side="left", padx=(0, 10))
        
        ctk.CTkLabel(header_frame, text=name, font=FONT_SUBTITLE, text_color=COLOR_TEXT_WHITE).pack(side="left")
        
        # Progress Bar
        pct = current / target if target > 0 else 0
        if pct > 1: pct = 1
        
        prog_bar = ctk.CTkProgressBar(card, height=10, corner_radius=5, progress_color=color)
        prog_bar.set(pct)
        prog_bar.pack(fill="x", padx=15, pady=10)
        
        # Stats
        stats_frame = ctk.CTkFrame(card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=5)
        
        missing = target - current
        time_msg = "Completado!" if missing <= 0 else self._calculate_time_remaining(missing)
        
        ctk.CTkLabel(stats_frame, text=f"{int(pct*100)}%", font=("Inter", 12, "bold"), text_color=color).pack(side="left")
        ctk.CTkLabel(stats_frame, text=f"Faltan ${missing:,.0f}", font=("Inter", 12), text_color=COLOR_TEXT_GRAY).pack(side="right")
        
        # Bottom: Time + Action
        bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        ctk.CTkLabel(bottom_frame, text=time_msg, font=("Inter", 10, "italic"), text_color="#666").pack(anchor="w", pady=(0, 10))
        
        if missing > 0:
            btn = ctk.CTkButton(bottom_frame, text="Aportar", height=28, fg_color="transparent", 
                                border_width=1, border_color=color, text_color=color, hover_color="#222",
                                command=lambda i=pid: self._show_deposit_dialog(i, name, color))
            btn.pack(fill="x")
        else:
            ctk.CTkButton(bottom_frame, text="¡Completado!", height=28, fg_color=color, text_color="#000", state="disabled").pack(fill="x")
        
        # Trash/Delete Button (Small, Transparent)
        delete_btn = ctk.CTkButton(card, text="🗑", width=30, height=30, fg_color="transparent", 
                                   hover_color="#330000", text_color="#FF4444", font=("Arial", 16),
                                   command=lambda i=pid: self._confirm_delete(i, name))
        delete_btn.place(relx=0.9, rely=0.02, anchor="ne") # Top right corner for cleaner "trash" look, or bottom?
        # User asked for: "debajo de cada objetivo creado en forma de papelera pequena"
        # Since I'm using pack for other elements, placing it at the bottom might be tricky with pack/grid mix.
        # Let's pack it at the very bottom of the card.
        delete_btn.pack(side="bottom", pady=(0, 10))


    def _calculate_time_remaining(self, missing_amount):
        if self._avg_savings <= 0:
            return "Indefinido (Sin ahorro mensual)"
        months = math.ceil(missing_amount / self._avg_savings)
        return f"~{months} meses restantes"

    def _show_add_dialog(self):
        # Quick modal to add plan. Ideally explicit class, but inline for speed here.
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Plan")
        dialog.geometry("400x400")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="Nuevo Objetivo", font=FONT_SUBTITLE).pack(pady=20)
        
        name_var = ctk.StringVar()
        target_var = ctk.StringVar()
        
        # Auto-assign random neon color
        neon_colors = ["#00FFFF", "#FF00FF", "#00FF00", "#FFFF00", "#FF0099", "#9D00FF"]
        color_var = ctk.StringVar(value=random.choice(neon_colors))
        
        ctk.CTkEntry(dialog, textvariable=name_var, placeholder_text="¿Cuál será nuestro objetivo?").pack(pady=10, padx=20, fill="x")
        ctk.CTkEntry(dialog, textvariable=target_var, placeholder_text="Monto del objetivo").pack(pady=10, padx=20, fill="x")
        # Color input removed per request
        
        def save():
            try:
                t = float(target_var.get())
                if t <= 0: raise ValueError
                self.db.create_plan(name_var.get(), t, "2026-12-31", color_var.get()) # Date placeholder
                dialog.destroy()
                self.refresh_plans()
            except ValueError:
                messagebox.showerror("Error", "Datos inválidos", parent=dialog)
                
        ctk.CTkButton(dialog, text="Crear Objetivo", command=save, fg_color=COLOR_ACCENT_GREEN, text_color="#000000").pack(pady=20)

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
                # Optional: Show a quick info box or just toast
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}", parent=self)
