"""Vista de Transacciones."""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from utils.constants import *


class TransactionsView(ctk.CTkFrame):
    def __init__(self, parent, db, tx_service):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.db = db
        self.tx_service = tx_service
        self.grid(row=0, column=1, sticky="nsew", padx=40, pady=30)
        self._setup_ui()

    def _setup_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 40))
        ctk.CTkLabel(header_frame, text="Transacciones", font=FONT_TITLE_MAIN, text_color=COLOR_TEXT_WHITE).pack(side="left")
        ctk.CTkButton(header_frame, text="Exportar", command=self.export_csv, 
                      fg_color=COLOR_ACCENT_BLUE, width=100).pack(side="right")
        ctk.CTkButton(header_frame, text="Eliminar", command=self.delete_selected,
                      fg_color=theme_color(COLOR_ACCENT_RED), width=100).pack(side="right", padx=5)

        form_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        form_frame.pack(fill="x", pady=10)

        self.var_tipo = ctk.StringVar(value=TX_TYPE_GASTO)
        self.var_cat = ctk.StringVar(value=CATEGORIAS[0])
        self.var_monto = ctk.StringVar()
        self.var_desc = ctk.StringVar()
        self.var_metodo = ctk.StringVar(value=METHOD_EFECTIVO)

        input_grid = ctk.CTkFrame(form_frame, fg_color="transparent")
        input_grid.pack(fill="x", padx=20, pady=20)

        # Configuración de Grid
        ctk.CTkLabel(input_grid, text="Tipo:", font=FONT_BODY).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkOptionMenu(input_grid, variable=self.var_tipo, values=[TX_TYPE_INGRESO, TX_TYPE_GASTO]).grid(row=0, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(input_grid, text="Categoría:", font=FONT_BODY).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkOptionMenu(input_grid, variable=self.var_cat, values=CATEGORIAS).grid(row=0, column=3, padx=10, pady=5)
        
        ctk.CTkLabel(input_grid, text="Monto ($):", font=FONT_BODY).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(input_grid, textvariable=self.var_monto).grid(row=1, column=1, padx=10, pady=5)
        
        ctk.CTkLabel(input_grid, text="Método:", font=FONT_BODY).grid(row=1, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkOptionMenu(input_grid, variable=self.var_metodo, values=[METHOD_EFECTIVO, METHOD_DEBITO, METHOD_CREDITO_INTERNO]).grid(row=1, column=3, padx=10, pady=5)
        
        ctk.CTkLabel(input_grid, text="Descripción:", font=FONT_BODY).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(input_grid, textvariable=self.var_desc, width=300).grid(row=2, column=1, columnspan=3, sticky="we", padx=10, pady=5)

        ctk.CTkButton(form_frame, text="Agregar Transacción", command=self.save_transaction, 
                      fg_color=COLOR_ACCENT_GREEN, text_color="#000000", hover_color="#27ae60", font=FONT_BODY, height=40).pack(pady=20, padx=20, fill="x")

        self.create_treeview()

    def create_treeview(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background=COLOR_CARD_BG, foreground="white", fieldbackground=COLOR_CARD_BG, rowheight=35, borderwidth=0)
        style.map('Treeview', background=[('selected', COLOR_ACCENT_BLUE)])
        style.configure("Treeview.Heading", background=COLOR_SIDEBAR, foreground="white", font=(FONT_FAMILY, 11, 'bold'), borderwidth=0)

        tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, pady=10)
        
        cols = ("ID", "Tipo", "Cat", "Monto", "Fecha", "Desc", "Método")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=10)
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        self.tree.column("Desc", width=250)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.refresh_table()

    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.db.get_transactions():
            self.tree.insert("", "end", values=row)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una transacción para eliminar")
            return
        item = selected[0]
        values = self.tree.item(item, "values")
        tx_id = values[0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar la transacción ID {tx_id}?"):
            self.db.delete_transaction(tx_id)
            self.refresh_table()
            messagebox.showinfo("Éxito", "Transacción eliminada")

    def save_transaction(self):
        try:
            monto_str = self.var_monto.get()
            if not monto_str: return
            monto = float(monto_str)
            
            self.tx_service.create_transaction(
                self.var_tipo.get(), self.var_cat.get(), monto,
                datetime.now().strftime("%Y-%m-%d"), self.var_desc.get(), self.var_metodo.get()
            )
            self.var_monto.set(""); self.var_desc.set("")
            self.refresh_table()
            messagebox.showinfo("Success", "Transacción guardada exitosamente")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def export_csv(self):
        from tkinter import filedialog
        from services.data_service import DataService
        
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filename:
            try:
                ds = DataService(self.db)
                ds.export_transactions_csv(filename)
                messagebox.showinfo("Success", "Datos exportados exitosamente")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
