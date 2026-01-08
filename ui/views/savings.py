"""Savings View."""
import customtkinter as ctk
from tkinter import messagebox
from utils.constants import *

class SavingsView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.db = db
        self.grid(row=0, column=1, sticky="nsew", padx=40, pady=30)
        self._setup_ui()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="Savings Goals", font=FONT_TITLE_MAIN, text_color=COLOR_TEXT_WHITE).pack(anchor="w", pady=(0, 40))

        # Add Goal Form
        add_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        add_frame.pack(fill="x", pady=10)
        
        self.goal_name = ctk.StringVar(); self.goal_target = ctk.StringVar()
        ctk.CTkEntry(add_frame, textvariable=self.goal_name, placeholder_text="Goal Name").pack(side="left", padx=20, expand=True, fill="x", pady=20)
        ctk.CTkEntry(add_frame, textvariable=self.goal_target, placeholder_text="Target Amount").pack(side="left", padx=20)
        ctk.CTkButton(add_frame, text="Create Goal", command=self.create_goal, fg_color=COLOR_ACCENT_BLUE).pack(side="left", padx=20)

        # Goals List
        self.goals_scroll = ctk.CTkScrollableFrame(self, height=400, fg_color="transparent")
        self.goals_scroll.pack(fill="both", expand=True, pady=10)
        
        self.refresh_goals()

    def refresh_goals(self):
        for widget in self.goals_scroll.winfo_children():
            widget.destroy()

        for g in self.db.get_savings_goals():
            gid, name, target, current = g
            pct = current / target if target > 0 else 0
            
            card = ctk.CTkFrame(self.goals_scroll, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
            card.pack(fill="x", pady=8)
            
            ctk.CTkLabel(card, text=name, font=FONT_SUBTITLE, text_color=COLOR_TEXT_WHITE).pack(anchor="w", padx=20, pady=(15, 5))
            
            prog = ctk.CTkProgressBar(card, height=12, corner_radius=6, progress_color=COLOR_ACCENT_GREEN)
            prog.set(pct)
            prog.pack(fill="x", padx=20, pady=10)
            
            ctk.CTkLabel(card, text=f"${current} / ${target}", font=FONT_BODY, text_color=COLOR_TEXT_GRAY).pack(anchor="w", padx=20, pady=(0, 15))
            
            ctk.CTkButton(card, text="Deposit $50", height=32, corner_radius=8, command=lambda i=gid: self.add_savings(i, 50),
                          fg_color=COLOR_ACCENT_BLUE, hover_color="#2980b9").pack(anchor="e", padx=20, pady=(0, 15))

    def create_goal(self):
        try:
            self.db.add_savings_goal(self.goal_name.get(), float(self.goal_target.get()))
            self.refresh_goals()
        except ValueError: messagebox.showerror("Error", "Invalid Amount")

    def add_savings(self, gid, amount):
        self.db.update_savings_progress(gid, amount)
        self.refresh_goals()
