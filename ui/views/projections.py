"""Projections View for calculating future net worth."""
import customtkinter as ctk
from utils.constants import *
from services.finance_math import FinanceMath

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class ProjectionsView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, corner_radius=0, fg_color="#0A0A0A") # Deep Black Background
        self.db = db
        self.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self._setup_ui()

    def _setup_ui(self):
        # 1. Base Data
        self.avg_savings = max(0, FinanceMath.calculate_average_savings(self.db, days=90))
        current_balance_ing, current_balance_gas = self.db.get_summary()
        self.current_principal = current_balance_ing - current_balance_gas
        
        # 60 Months (5 Years)
        self.months = 60 
        
        # 2. HEADER
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=(20, 10))
        
        ctk.CTkLabel(header_frame, text="SIMULADOR DE CRECIMIENTO", font=("Inter", 24, "bold"), text_color=COLOR_ACCENT_GREEN).pack(anchor="w")
        ctk.CTkLabel(header_frame, text="Proyección a 5 Años (60 Meses) - Comparativa de Ahorro", font=("Inter", 14), text_color=COLOR_TEXT_GRAY).pack(anchor="w")

        # 3. INTERACTIVE CONTROLS
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(fill="x", padx=40, pady=(10, 20))
        
        # Slider Section
        self.slider_label = ctk.CTkLabel(controls_frame, text="Ahorro Extra Mensual: $0", font=("Inter", 16, "bold"), text_color=COLOR_TEXT_WHITE)
        self.slider_label.pack(anchor="w", pady=(0, 5))
        
        self.slider = ctk.CTkSlider(controls_frame, from_=0, to=1000, number_of_steps=100, command=self._update_simulation)
        self.slider.pack(fill="x", pady=(0, 15))
        self.slider.set(0)
        
        # Dynamic Results
        results_frame = ctk.CTkFrame(controls_frame, fg_color=COLOR_CARD_BG, corner_radius=12)
        results_frame.pack(fill="x", pady=5)
        
        # Grid layout for results
        results_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Result 1: 24 Months Total
        self.lbl_result_24m = ctk.CTkLabel(results_frame, text="En 24 Meses: $0", font=("Inter", 18, "bold"), text_color=COLOR_ACCENT_GREEN)
        self.lbl_result_24m.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Result 2: Extra Gain
        self.lbl_gain_extra = ctk.CTkLabel(results_frame, text="Ganancia Extra: $0", font=("Inter", 18, "bold"), text_color="#2ECC71")
        self.lbl_gain_extra.grid(row=0, column=1, padx=20, pady=15, sticky="e")

        # 4. CHART
        chart_frame = ctk.CTkFrame(self, fg_color="transparent")
        chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.figure = None
        self.ax = None
        self.canvas = None
        
        if HAS_MATPLOTLIB:
            self.figure = plt.Figure(figsize=(8, 5), dpi=100, facecolor="#0A0A0A")
            self.ax = self.figure.add_subplot(111)
            self.ax.set_facecolor("#0A0A0A")
            
            # Initial styling
            for spine in self.ax.spines.values():
                spine.set_visible(False)
            self.ax.tick_params(axis='x', colors='white')
            self.ax.tick_params(axis='y', colors='white')
            self.ax.grid(True, axis='y', color='#333333', linestyle='--', alpha=0.5)

            self.canvas = FigureCanvasTkAgg(self.figure, master=chart_frame)
            self.canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Initial Draw
            self._update_simulation(0)
        else:
            ctk.CTkLabel(chart_frame, text="Matplotlib no instalado", text_color=COLOR_TEXT_RED).pack(expand=True)
            
        # 5. DISCLAIMER
        ctk.CTkLabel(self, text="Ahorro Base (Promedio 90 días): ${:.2f}".format(self.avg_savings), 
                     font=("Inter", 12), text_color=COLOR_TEXT_GRAY).pack(side="bottom", pady=(0, 20))

    def _update_simulation(self, value):
        extra_savings = float(value)
        self.slider_label.configure(text=f"Ahorro Extra Mensual: ${int(extra_savings)}")
        
        # Calculate Scenarios
        # 1. Base
        t_base, amounts_base = FinanceMath.calculate_compound_growth(self.current_principal, self.avg_savings, 0.08, self.months)
        # 2. Optimized
        t_opt, amounts_opt = FinanceMath.calculate_compound_growth(self.current_principal, self.avg_savings + extra_savings, 0.08, self.months)
        
        # Update Labels (at 24 months = index 24)
        idx_24 = min(24, len(amounts_opt)-1)
        val_24 = amounts_opt[idx_24]
        diff_24 = val_24 - amounts_base[idx_24]
        
        self.lbl_result_24m.configure(text=f"En 24 Meses: ${val_24:,.0f}")
        self.lbl_gain_extra.configure(text=f"Ganancia Extra: ${diff_24:,.0f}")
        
        # Update Chart
        if self.ax:
            self.ax.clear()
            self.ax.grid(True, axis='y', color='#333333', linestyle='--', alpha=0.5)
            
            # Plot Base (Cyan)
            self.ax.plot(t_base, amounts_base, color="#00F2FF", linewidth=2, label="Actual")
            
            # Plot Optimized (Green)
            self.ax.plot(t_opt, amounts_opt, color="#2ECC71", linewidth=2, label="Optimizado")
            
            # Fill Between
            self.ax.fill_between(t_base, amounts_base, amounts_opt, color="#2ECC71", alpha=0.3)
            self.ax.fill_between(t_base, [self.current_principal]*len(t_base), amounts_base, color="#00F2FF", alpha=0.1)
            
            self.canvas.draw()
