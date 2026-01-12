"""Vista del Panel de Control de Finanzas."""
import customtkinter as ctk
from utils.constants import *
from ui.components.cards import create_info_card

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.db = db
        self.grid(row=0, column=1, sticky="nsew", padx=40, pady=30)
        self._setup_ui()

    def _setup_ui(self):
        ctk.CTkLabel(self, text="Panel de Control De Finanzas", font=FONT_TITLE_MAIN, text_color=COLOR_TEXT_WHITE).pack(anchor="w", pady=(0, 40))

        ingresos, gastos = self.db.get_summary()
        balance = ingresos - gastos
        cred_lim, cred_used = self.db.get_credit_info()
        cred_disp = cred_lim - cred_used

        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)

        create_info_card(cards_frame, "Ingresos Totales", f"${ingresos:.2f}", COLOR_ACCENT_GREEN, "↑").pack(side="left", expand=True, fill="both", padx=10)
        create_info_card(cards_frame, "Gastos Totales", f"${gastos:.2f}", COLOR_ACCENT_RED, "↓").pack(side="left", expand=True, fill="both", padx=10)
        create_info_card(cards_frame, "Balance Neto", f"${balance:.2f}", COLOR_ACCENT_BLUE, "—").pack(side="left", expand=True, fill="both", padx=10)
        create_info_card(cards_frame, "Crédito Disponible", f"${cred_disp:.2f}", COLOR_ACCENT_YELLOW, "::").pack(side="left", expand=True, fill="both", padx=10)

        self._create_chart()

    def _create_chart(self):
        chart_container = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        chart_container.pack(fill="both", expand=True, pady=30)

        ctk.CTkLabel(chart_container, text="Análisis de Gastos", font=FONT_TITLE_SECTION, text_color=COLOR_TEXT_WHITE).pack(anchor="w", padx=25, pady=25)

        chart_frame = ctk.CTkFrame(chart_container, fg_color="transparent")
        chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        data = self.db.get_expenses_by_category()
        if HAS_MATPLOTLIB and data:
            categories = [x[0] for x in data]
            amounts = [x[1] for x in data]
            fig = plt.Figure(figsize=(6, 4), dpi=100, facecolor=theme_color(COLOR_CARD_BG))
            ax = fig.add_subplot(111)
            colors = [
                theme_color(COLOR_ACCENT_GREEN), 
                theme_color(COLOR_ACCENT_RED), 
                theme_color(COLOR_ACCENT_BLUE), 
                theme_color(COLOR_ACCENT_YELLOW), 
                '#9b59b6', '#e67e22'
            ]
            wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                              startangle=90, textprops={'color':"white", 'size': 10},
                                              colors=colors, wedgeprops={'edgecolor': theme_color(COLOR_CARD_BG), 'linewidth': 3})
            ax.set_facecolor(theme_color(COLOR_CARD_BG))
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="left", fill="both", expand=True, padx=10, pady=10)
        else:
            ctk.CTkLabel(chart_frame, text="Sin datos para gráficos", text_color=COLOR_TEXT_GRAY).pack(expand=True)
