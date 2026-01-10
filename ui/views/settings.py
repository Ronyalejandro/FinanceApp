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
        ctk.CTkLabel(self, text="Configuración", font=FONT_TITLE_MAIN, text_color=COLOR_TEXT_WHITE).pack(anchor="w", pady=(0, 40))

        # Data Management Section
        data_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        data_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(data_frame, text="Gestión de Datos", font=FONT_SUBTITLE, text_color=COLOR_TEXT_WHITE).pack(anchor="w", padx=20, pady=20)
        
        # Backup
        backup_frame = ctk.CTkFrame(data_frame, fg_color="transparent")
        backup_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(backup_frame, text="Crear Respaldo de Base de Datos", font=FONT_BODY, text_color=COLOR_TEXT_GRAY).pack(side="left")
        ctk.CTkButton(backup_frame, text="Respaldar DB", command=self.create_backup, 
                      fg_color=COLOR_ACCENT_BLUE, height=32).pack(side="right", padx=(10, 0))
        
        # Export CSV
        export_frame = ctk.CTkFrame(data_frame, fg_color="transparent")
        export_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(export_frame, text="Exportar Transacciones a Excel/CSV", font=FONT_BODY, text_color=COLOR_TEXT_GRAY).pack(side="left")
        ctk.CTkButton(export_frame, text="Exportar CSV", command=self.export_csv,
                      fg_color=COLOR_ACCENT_GREEN, text_color="black", height=32).pack(side="right", padx=(10, 0))

    def export_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filename:
            try:
                self.ds.export_transactions_csv(filename)
                messagebox.showinfo("Éxito", "Datos exportados correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando: {e}")

    def create_backup(self):
        target_dir = filedialog.askdirectory(title="Seleccionar Directorio de Respaldo")
        if target_dir:
            try:
                path = self.ds.backup_database(target_dir)
                messagebox.showinfo("Success", f"Respaldo creado en:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", f"Fallo en el respaldo: {e}")
