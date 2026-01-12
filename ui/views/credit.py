"""Vista de Crédito (Cashea)."""
import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox
from utils.constants import *

class CreditView(ctk.CTkFrame):
    def __init__(self, parent, db, tx_service):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.db = db
        self.tx_service = tx_service
        self.grid(row=0, column=1, sticky="nsew", padx=40, pady=30)
        self._setup_ui()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="Cashea", font=FONT_TITLE_MAIN, text_color=COLOR_TEXT_WHITE).pack(anchor="w", pady=(0, 40))
        
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)
        
        self._refresh_data() 

    def _refresh_data(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        lim, used = self.db.get_credit_info()
        disp = lim - used
        percent = used / lim if lim > 0 else 0

        # Tarjeta principal de Crédito
        credit_card = ctk.CTkFrame(self.content_frame, fg_color=COLOR_CARD_BG, border_color=COLOR_ACCENT_BLUE, border_width=1, corner_radius=20)
        credit_card.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(credit_card, text=f"Límite Total: ${lim:.2f}", font=FONT_SUBTITLE).pack(pady=(20, 10))
        
        prog = ctk.CTkProgressBar(credit_card, width=400, height=20, corner_radius=10)
        prog.set(percent)
        prog.configure(progress_color=COLOR_ACCENT_RED if percent > 0.9 else COLOR_ACCENT_GREEN)
        prog.pack(pady=10)
        
        ctk.CTkLabel(credit_card, text=f"Usado: ${used:.2f}  |  Disponible: ${disp:.2f}", font=FONT_SUBTITLE, text_color=COLOR_TEXT_WHITE).pack(pady=(10, 20))

        # Acciones
        actions_frame = ctk.CTkFrame(self.content_frame, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        actions_frame.pack(pady=10, padx=0, fill="x")
        
        self.new_limit_var = ctk.StringVar()
        ctk.CTkEntry(actions_frame, textvariable=self.new_limit_var, placeholder_text="Nuevo Límite").grid(row=0, column=0, padx=20, pady=20)
        ctk.CTkButton(actions_frame, text="Actualizar Límite", command=self.update_limit, fg_color=COLOR_ACCENT_BLUE).grid(row=0, column=1, padx=20)

        # Pagos
        pay_frame = ctk.CTkFrame(self.content_frame, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        pay_frame.pack(pady=10, padx=0, fill="x")
        
        self.pay_credit_var = ctk.StringVar()
        ctk.CTkEntry(pay_frame, textvariable=self.pay_credit_var, placeholder_text="Monto del Pago").pack(side="left", padx=20, pady=20)
        ctk.CTkButton(pay_frame, text="Realizar Pago", fg_color=COLOR_ACCENT_GREEN, text_color="#000000", command=self.pay_credit).pack(side="left", padx=20)

    def update_limit(self):
        try:
            val = float(self.new_limit_var.get())
            self.db.update_credit_limit(val)
            self._refresh_data()
        except ValueError: messagebox.showerror("Error", "Número Inválido")

    def pay_credit(self):
        try:
            val = float(self.pay_credit_var.get())
            self.tx_service.create_transaction("PagoCredito", "Financiero", val, datetime.now().strftime("%Y-%m-%d"), "Abono Crédito", "Transferencia")
            self._refresh_data()
            messagebox.showinfo("Éxito", "Pago procesado")
        except ValueError: messagebox.showerror("Error", "Monto Inválido")
