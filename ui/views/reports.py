"""Reports View."""
import customtkinter as ctk
from utils.constants import *
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class ReportsView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.db = db
        self.grid(row=0, column=1, sticky="nsew", padx=40, pady=30)
        self._setup_ui()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="Reportes Avanzados", font=FONT_TITLE_MAIN, text_color=COLOR_TEXT_WHITE).pack(anchor="w", pady=(0, 20))
        
        if not HAS_MATPLOTLIB:
            ctk.CTkLabel(self, text="Matplotlib no instalado. No se pueden mostrar gráficos.", text_color="red").pack()
            return

        # Main Scroll
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        
        # 1. Monthly Trend (Line Chart)
        self._create_trend_chart(scroll)
        
        # 2. Category Breakdown (Bar/Pie)
        self._create_category_chart(scroll)

    def _create_trend_chart(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD_BG, corner_radius=12)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Tendencia de Gastos (Últimos 90 días)", font=("Inter", 16, "bold"), text_color=theme_color(COLOR_TEXT_WHITE)).pack(anchor="w", padx=20, pady=15)
        
        # Data
        txs = self.db.get_recent_transactions(90)
        # Process dates
        from collections import defaultdict
        import datetime
        daily_expenses = defaultdict(float)
        
        for t in txs:
            # t: id, type, cat, amount, date, desc, method
            if t[1] == "Gasto":
                daily_expenses[t[4]] += t[3]
                
        dates = sorted(daily_expenses.keys())
        amounts = [daily_expenses[d] for d in dates]
        
        if not dates:
            ctk.CTkLabel(frame, text="No hay suficientes datos", text_color="gray").pack(pady=30)
            return

        # Plot
        fig = plt.Figure(figsize=(8, 4), dpi=100, facecolor=theme_color(COLOR_CARD_BG))
        ax = fig.add_subplot(111)
        
        ax.plot(dates, amounts, marker='o', color=theme_color(COLOR_ACCENT_BLUE), linestyle='-')
        ax.set_facecolor(theme_color(COLOR_CARD_BG))
        ax.tick_params(colors=theme_color(COLOR_TEXT_WHITE), labelrotation=45)
        for spine in ax.spines.values():
            spine.set_color('#444')
            
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)

    def _create_category_chart(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD_BG, corner_radius=12)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(frame, text="Gasto por Categoría", font=("Inter", 16, "bold"), text_color=theme_color(COLOR_TEXT_WHITE)).pack(anchor="w", padx=20, pady=15)
        
        data = self.db.get_expenses_by_category()
        if not data:
            ctk.CTkLabel(frame, text="Sin datos", text_color=theme_color(COLOR_TEXT_GRAY)).pack(pady=30)
            return
            
        cats = [x[0] for x in data]
        vals = [x[1] for x in data]
        
        fig = plt.Figure(figsize=(8, 4), dpi=100, facecolor=theme_color(COLOR_CARD_BG))
        ax = fig.add_subplot(111)
        
        # Horizontal Bar
        y_pos = range(len(cats))
        ax.barh(y_pos, vals, color=theme_color(COLOR_ACCENT_RED))
        ax.set_yticks(y_pos)
        ax.set_yticklabels(cats, color=theme_color(COLOR_TEXT_WHITE))
        ax.tick_params(axis='x', colors=theme_color(COLOR_TEXT_WHITE))
        ax.set_facecolor(theme_color(COLOR_CARD_BG))
        for spine in ax.spines.values():
            spine.set_color('#444')
            
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)
