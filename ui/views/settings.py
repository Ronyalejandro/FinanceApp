"""Settings View."""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from utils.constants import *
from services.data_service import DataService

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.db = db
        self.ds = DataService(db)
        self.grid(row=0, column=1, sticky="nsew", padx=40, pady=30)
        self._setup_ui()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="Settings", font=FONT_TITLE_MAIN, text_color=COLOR_TEXT_WHITE).pack(anchor="w", pady=(0, 40))

        # Data Management Section
        data_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        data_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(data_frame, text="Data Management", font=FONT_SUBTITLE, text_color=COLOR_TEXT_WHITE).pack(anchor="w", padx=20, pady=20)
        
        # Backup
        backup_frame = ctk.CTkFrame(data_frame, fg_color="transparent")
        backup_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(backup_frame, text="Create Database Backup", font=FONT_BODY, text_color=COLOR_TEXT_GRAY).pack(side="left")
        ctk.CTkButton(backup_frame, text="Backup Now", command=self.create_backup, 
                      fg_color=COLOR_ACCENT_BLUE, height=32).pack(side="right")

    def create_backup(self):
        target_dir = filedialog.askdirectory(title="Select Backup Directory")
        if target_dir:
            try:
                path = self.ds.backup_database(target_dir)
                messagebox.showinfo("Success", f"Backup created at:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Backup failed: {e}")
