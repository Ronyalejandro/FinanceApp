"""Login Window implementation."""
import os
import sys
import customtkinter as ctk
from tkinter import messagebox
from utils.security import save_pin_hash, verify_pin, is_first_time
from utils.constants import *

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_success) -> None:
        super().__init__(parent)
        self.title("Seguridad - Finanzas Personales")
        self.geometry("300x250")
        self.resizable(False, False)
        self.on_success = on_success
        
        self.update_idletasks()
        width = 300
        height = 250
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        self.configure(fg_color="#1e1e1e")
        self.first_time = is_first_time()
        
        if self.first_time:
            self.label = ctk.CTkLabel(self, text="Crear PIN de Acceso", font=("Roboto", 18, "bold"), text_color="#ffffff")
        else:
            self.label = ctk.CTkLabel(self, text="Ingrese PIN de Acceso", font=("Roboto", 18, "bold"), text_color="#ffffff")
        self.label.pack(pady=(30, 20))

        self.entry = ctk.CTkEntry(self, show="*", width=180, height=40, corner_radius=10, 
                                  border_color="#333333", fg_color="#252525", justify="center", font=("Roboto", 18))
        self.entry.pack(pady=10)
        
        self.entry.focus_set()

        btn_text = "Crear" if self.first_time else "Entrar"
        btn_cmd = self.create_pin if self.first_time else self.check_password
        
        self.btn = ctk.CTkButton(self, text=btn_text, command=btn_cmd, width=180, height=40, 
                                 corner_radius=10, fg_color=COLOR_ACCENT_BLUE, hover_color="#2980b9", font=("Roboto", 14, "bold"))
        self.btn.pack(pady=20)
        
        # Vincular tecla Enter
        self.entry.bind("<Return>", lambda event: btn_cmd())
        
        self.protocol("WM_DELETE_WINDOW", sys.exit)
        self.attributes("-topmost", True)

    def check_password(self) -> None:
        try:
            if verify_pin(self.entry.get()):
                self.on_success()
                self.destroy()
            else:
                messagebox.showerror("Error", "PIN Incorrecto")
                self.entry.delete(0, "end")
        except Exception:
            messagebox.showerror("Error", "Error al verificar PIN")

    def create_pin(self) -> None:
        pin = self.entry.get()
        if not pin or len(pin) < 4:
            messagebox.showerror("Error", "El PIN debe tener al menos 4 caracteres")
            return
        try:
            save_pin_hash(pin)
            messagebox.showinfo("Listo", "PIN creado. Iniciando aplicación.")
            self.on_success()
            self.destroy()
        except OSError:
            messagebox.showerror("Error", "No se pudo guardar el PIN")
