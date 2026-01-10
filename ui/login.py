"""Login Window implementation with Onboarding and Recovery."""
import sys
import customtkinter as ctk
from tkinter import messagebox
from utils.security import (save_pin_hash, verify_pin, is_first_time, 
                            verify_recovery_answer, get_security_question, save_user_profile)
from utils.constants import *

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_success) -> None:
        super().__init__(parent)
        self.title("Seguridad - FinanceApp")
        self.geometry("400x500") # Taller for profile form
        self.resizable(False, False)
        self.on_success = on_success
        
        self.update_idletasks()
        self._center_window(400, 500)

        self.configure(fg_color=COLOR_BACKGROUND)
        
        # State Data
        self.temp_pin = None
        
        # States: "LOGIN", "SETUP_PIN", "SETUP_SECURITY", "SETUP_PROFILE", "RECOVERY"
        self.login_state = "SETUP_PIN" if is_first_time() else "LOGIN"
        
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.render_current_state()
        
        self.protocol("WM_DELETE_WINDOW", sys.exit)
        self.attributes("-topmost", True)

    def _center_window(self, width, height):
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def render_current_state(self):
        self.clear_frame()
        
        if self.login_state == "LOGIN":
            self._render_login()
        elif self.login_state == "SETUP_PIN":
            self._render_setup_pin()
        elif self.login_state == "SETUP_SECURITY":
            self._render_setup_security()
        elif self.login_state == "SETUP_PROFILE":
            self._render_setup_profile()
        elif self.login_state == "RECOVERY":
            self._render_recovery()

    # --- Render Methods ---
    def _render_login(self):
        ctk.CTkLabel(self.main_frame, text="BIENVENIDO", font=("Inter", 24, "bold"), text_color=COLOR_TEXT_WHITE).pack(pady=(40, 10))
        ctk.CTkLabel(self.main_frame, text="Ingrese su PIN", font=("Inter", 14), text_color=COLOR_TEXT_GRAY).pack(pady=(0, 20))
        
        self.entry_pin = ctk.CTkEntry(self.main_frame, show="*", width=200, justify="center", font=("Inter", 20))
        self.entry_pin.pack(pady=10)
        self.entry_pin.focus_set()
        
        ctk.CTkButton(self.main_frame, text="Entrar", command=self._handle_login, fg_color=COLOR_ACCENT_BLUE).pack(pady=20, fill="x")
        ctk.CTkButton(self.main_frame, text="Olvidé mi PIN", command=lambda: self._utils_set_state("RECOVERY"), 
                      fg_color="transparent", text_color=COLOR_ACCENT_RED, hover_color="#222").pack()

        self.entry_pin.bind("<Return>", lambda e: self._handle_login())

    def _render_setup_pin(self):
        ctk.CTkLabel(self.main_frame, text="CONFIGURACIÓN INICIAL", font=("Inter", 20, "bold"), text_color=COLOR_ACCENT_GREEN).pack(pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text="1. Crea tu PIN de 4 dígitos", font=("Inter", 14), text_color=COLOR_TEXT_WHITE).pack(pady=(0, 20))
        
        self.entry_pin = ctk.CTkEntry(self.main_frame, show="*", width=200, justify="center", font=("Inter", 20))
        self.entry_pin.pack(pady=10)
        self.entry_pin.focus()
        
        ctk.CTkButton(self.main_frame, text="Siguiente", command=self._handle_setup_pin, fg_color=COLOR_ACCENT_GREEN, text_color="#000000").pack(pady=20, fill="x")

    def _render_setup_security(self):
        ctk.CTkLabel(self.main_frame, text="SEGURIDAD", font=("Inter", 20, "bold"), text_color=COLOR_ACCENT_GREEN).pack(pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text="2. Pregunta de Seguridad\n(Para recuperar tu cuenta)", font=("Inter", 14), text_color=COLOR_TEXT_WHITE).pack(pady=(0, 20))
        
        self.entry_question = ctk.CTkEntry(self.main_frame, placeholder_text="Ej: ¿Nombre de mi primera mascota?", width=300)
        self.entry_question.pack(pady=10)
        
        self.entry_answer = ctk.CTkEntry(self.main_frame, placeholder_text="Respuesta", width=300)
        self.entry_answer.pack(pady=10)
        
        ctk.CTkButton(self.main_frame, text="Guardar y Continuar", command=self._handle_setup_security, fg_color=COLOR_ACCENT_GREEN, text_color="#000000").pack(pady=20, fill="x")

    def _render_setup_profile(self):
        ctk.CTkLabel(self.main_frame, text="PERFIL", font=("Inter", 20, "bold"), text_color=COLOR_ACCENT_GREEN).pack(pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text="3. Completa tu Perfil", font=("Inter", 14), text_color=COLOR_TEXT_WHITE).pack(pady=(0, 20))
        
        self.entry_name = ctk.CTkEntry(self.main_frame, placeholder_text="Nombre", width=300)
        self.entry_name.pack(pady=5)
        
        self.entry_lastname = ctk.CTkEntry(self.main_frame, placeholder_text="Apellido", width=300)
        self.entry_lastname.pack(pady=5)
        
        self.entry_age = ctk.CTkEntry(self.main_frame, placeholder_text="Edad", width=300)
        self.entry_age.pack(pady=5)
        
        ctk.CTkButton(self.main_frame, text="Finalizar", command=self._handle_setup_profile, fg_color=COLOR_ACCENT_GREEN, text_color="#000000").pack(pady=30, fill="x")

    def _render_recovery(self):
        question = get_security_question()
        if not question:
            messagebox.showerror("Error", "No hay pregunta de seguridad configurada. Resetee la app.", parent=self)
            self._utils_set_state("LOGIN")
            return

        ctk.CTkLabel(self.main_frame, text="RECUPERACIÓN", font=("Inter", 20, "bold"), text_color=COLOR_ACCENT_RED).pack(pady=(20, 10))
        ctk.CTkLabel(self.main_frame, text=f"Pregunta: {question}", font=("Inter", 14, "italic"), text_color=COLOR_TEXT_WHITE).pack(pady=(0, 20))
        
        self.entry_recovery_answer = ctk.CTkEntry(self.main_frame, placeholder_text="Tu respuesta", width=300)
        self.entry_recovery_answer.pack(pady=10)
        
        ctk.CTkButton(self.main_frame, text="Verificar y Resetear PIN", command=self._handle_recovery, fg_color=COLOR_ACCENT_RED).pack(pady=20, fill="x")
        ctk.CTkButton(self.main_frame, text="Cancelar", command=lambda: self._utils_set_state("LOGIN"), fg_color="transparent").pack()

    # --- Handlers ---
    def _utils_set_state(self, new_state):
        self.login_state = new_state
        self.render_current_state()

    def _handle_login(self):
        if verify_pin(self.entry_pin.get()):
            self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Error", "PIN Incorrecto", parent=self)
            self.entry_pin.delete(0, "end")

    def _handle_setup_pin(self):
        pin = self.entry_pin.get()
        if len(pin) < 4:
            messagebox.showerror("Error", "El PIN debe tener 4+ caracteres", parent=self)
            return
        self.temp_pin = pin
        self._utils_set_state("SETUP_SECURITY")

    def _handle_setup_security(self):
        q = self.entry_question.get()
        a = self.entry_answer.get()
        if not q or not a:
            messagebox.showerror("Error", "Campos obligatorios", parent=self)
            return
        
        # Save PIN and Security info
        try:
            save_pin_hash(self.temp_pin, q, a)
            self._utils_set_state("SETUP_PROFILE")
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando datos: {e}", parent=self)

    def _handle_setup_profile(self):
        nombre = self.entry_name.get()
        apellido = self.entry_lastname.get()
        edad = self.entry_age.get()
        
        if not nombre or not apellido or not edad:
            messagebox.showerror("Error", "Todos los campos son obligatorios", parent=self)
            return
        if not edad.isdigit():
            messagebox.showerror("Error", "La edad debe ser un número", parent=self)
            return
            
        save_user_profile(nombre, apellido, int(edad))
        messagebox.showinfo("Bienvenido", "¡Perfil configurado exitosamente!", parent=self)
        self.on_success()
        self.destroy()

    def _handle_recovery(self):
        ans = self.entry_recovery_answer.get()
        if verify_recovery_answer(ans):
            messagebox.showinfo("Correcto", "Respuesta correcta. Por favor defina su nuevo PIN.", parent=self)
            # Clear config logic? Or just overwrite.
            # Ideally we want to keep profile but reset PIN.
            # For simplicity, we can go to SETUP_PIN state, but need to ensure it doesn't wipe profile unless intended.
            # save_pin_hash preserves profile if passing new pin. 
            self._utils_set_state("SETUP_PIN")
            # Note: SETUP_PIN flow will ask for Security Q again. 
            # Improvement: Add a specialized "RESET_PIN" state that only asks for PIN and keeps old security Q/A.
            # For now, full re-setup (PIN + Security) is safer/easier. Profile will be preserved by logic in security.py 
            # BUT wait, logic in security.py for save_pin_hash uses "current_data.get('profile')".
            # So if we run full setup again, we need to make sure we don't overwrite profile with empty if we don't reach step 3.
            # Actually, Step 3 (Profile) writes to 'profile' key. 
            # If user goes SETUP_PIN -> SETUP_SECURITY -> SETUP_PROFILE, they might overwrite profile.
            # Let's just guide them through full Setup again, it allows updating profile too which is fine.
        else:
            messagebox.showerror("Error", "Respuesta incorrecta", parent=self)
