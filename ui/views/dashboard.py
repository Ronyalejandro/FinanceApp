"""Dashboard View."""
import customtkinter as ctk
from utils.constants import *
from ui.components.cards import create_info_card

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from utils.security import get_user_profile

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.db = db
        self.grid(row=0, column=1, sticky="nsew", padx=40, pady=30)
        self._setup_ui()

    def _setup_ui(self):
        # 1. Custom Title with Personalization
        profile = get_user_profile()
        nombre = profile.get("nombre", "Usuario")
        apellido = profile.get("apellido", "")
        
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(anchor="w", pady=(0, 30))
        
        # "Hola, " (White)
        ctk.CTkLabel(header_frame, text="Hola, ", font=(FONT_FAMILY, 28, "bold"), text_color=theme_color(COLOR_TEXT_WHITE)).pack(side="left")
        # "{Nombre}" (Neon Cyan)
        ctk.CTkLabel(header_frame, text=f"{nombre} {apellido}", font=(FONT_FAMILY, 28, "bold"), text_color=COLOR_ACCENT_GREEN).pack(side="left")

        ingresos, gastos = self.db.get_summary()
        balance = ingresos - gastos
        cred_lim, cred_used = self.db.get_credit_info()
        cred_disp = cred_lim - cred_used

        # 2. Cards with precise 15px spacing
        # Using grid for precision. 
        # Configure columns to have equal weight usually, but for fixed spacing we can use padx.
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)
        cards_frame.grid_columnconfigure((0,1,2,3), weight=1) 
        
        # Cards (Neon Colors)
        # Ingresos: Cyan (#00F2FF)
        c1 = create_info_card(cards_frame, "Total Income", f"${ingresos:.2f}", COLOR_ACCENT_GREEN, "💰")
        c1.grid(row=0, column=0, sticky="ew", padx=(0, 15))

        # Gastos: Magenta (#FF006E)
        c2 = create_info_card(cards_frame, "Total Expenses", f"${gastos:.2f}", COLOR_ACCENT_RED, "💸")
        c2.grid(row=0, column=1, sticky="ew", padx=(0, 15))

        # Balance: Blue (#2f81f7) 
        c3 = create_info_card(cards_frame, "Net Balance", f"${balance:.2f}", COLOR_ACCENT_BLUE, "⚖️")
        c3.grid(row=0, column=2, sticky="ew", padx=(0, 15))

        # Credito: Orange/Gold (#FFB800)
        c4 = create_info_card(cards_frame, "Available Credit", f"${cred_disp:.2f}", COLOR_ACCENT_YELLOW, "💳")
        c4.grid(row=0, column=3, sticky="ew", padx=(0, 0)) # Last one no right padding

        self._create_budgets_section()
        self._create_chart()

    def _create_budgets_section(self):
        # Container
        budget_container = ctk.CTkFrame(self, fg_color="transparent")
        budget_container.pack(fill="x", pady=20)
        
        # Header for the section
        header = ctk.CTkFrame(budget_container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header, text="Estado de Presupuestos (Mensual)", font=FONT_TITLE_SECTION, text_color=theme_color(COLOR_TEXT_WHITE)).pack(side="left")
        ctk.CTkButton(header, text="Configurar", command=self._open_budget_config, 
                      fg_color=COLOR_SIDEBAR, hover_color="#222", width=100).pack(side="right")
        
        # Scrollable Area for Bars
        self.budget_scroll = ctk.CTkScrollableFrame(budget_container, height=200, fg_color=theme_color(COLOR_CARD_BG), corner_radius=12)
        self.budget_scroll.pack(fill="x")
        
        self.refresh_budgets()

    def refresh_budgets(self):
        # Clear existing
        for w in self.budget_scroll.winfo_children():
            w.destroy()
            
        budgets = self.db.get_budget_comparison() # [(cat, spent, limit), ...]
        
        if not budgets:
            ctk.CTkLabel(self.budget_scroll, text="No hay presupuestos definidos.", text_color=COLOR_TEXT_GRAY).pack(pady=20)
            return

        for cat, spent, limit in budgets:
            self._create_budget_row(cat, spent, limit)

    def _create_budget_row(self, category, spent, limit):
        row = ctk.CTkFrame(self.budget_scroll, fg_color="transparent")
        row.pack(fill="x", pady=5, padx=10)
        
        # Logic for Color
        ratio = spent / limit if limit > 0 else 0
        percent = ratio * 100
        
        if ratio < 0.8:
            color = COLOR_ACCENT_GREEN # Cyan
        elif ratio < 1.0:
            color = COLOR_ACCENT_YELLOW # Orange
        else:
            color = COLOR_ACCENT_RED # Magenta
            
        # Labels
        header_row = ctk.CTkFrame(row, fg_color="transparent")
        header_row.pack(fill="x")
        ctk.CTkLabel(header_row, text=category, font=("Inter", 14, "bold"), text_color=theme_color(COLOR_TEXT_WHITE)).pack(side="left")
        ctk.CTkLabel(header_row, text=f"${spent:.2f} / ${limit:.2f} ({int(percent)}%)", 
                     font=("Inter", 12), text_color=color).pack(side="right")
        
        # Progress Bar
        bar = ctk.CTkProgressBar(row, height=12, corner_radius=6, fg_color=theme_color(COLOR_BTN_ACTIVE), progress_color=color)
        bar.pack(fill="x", pady=(5, 0))
        bar.set(min(ratio, 1.0)) # Cap visual at 100%

    def _open_budget_config(self):
        toplevel = ctk.CTkToplevel(self)
        toplevel.title("Configurar Presupuestos")
        toplevel.geometry("400x600")
        toplevel.attributes("-topmost", True)
        
        ctk.CTkLabel(toplevel, text="Definir Límites Mensuales", font=("Inter", 20, "bold")).pack(pady=20)
        
        scroll = ctk.CTkScrollableFrame(toplevel)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        entries = {}
        
        # Load existing limits to pre-fill
        current_budgets = {cat: limit for cat, _, limit in self.db.get_budget_comparison()}
        
        for cat in CATEGORIAS:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=cat, width=150, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(row, width=100)
            entry.pack(side="right")
            
            if cat in current_budgets:
                entry.insert(0, str(int(current_budgets[cat])))
                
            entries[cat] = entry
            
        def save():
            for cat, entry in entries.items():
                val = entry.get()
                if val:
                    try:
                        limit = float(val)
                        self.db.update_budget(cat, limit)
                    except ValueError:
                        pass # Ignore invalid inputs
            self.refresh_budgets()
            toplevel.destroy()
            
        ctk.CTkButton(toplevel, text="Guardar Cambios", command=save, fg_color=COLOR_ACCENT_GREEN, text_color="#000000").pack(pady=20, fill="x", padx=20)

    def _create_chart(self):
        # Chart Container - "Floating" look, so maybe no border or subtle border?
        # User said: "Quitar los bordes del gráfico para que parezca flotar sobre la interfaz."
        # If I remove the container border, it will look like it's floating on the main BG.
        # But 'chart_container' background is COLOR_CARD_BG (#161B22) which is same as Sidebar, but lighter than BG (#0D1117).
        # So it will look like a card.
        # I'll keep the card container style for consistency but make it look clean.
        chart_container = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=12, border_width=1, border_color=COLOR_CARD_BORDER)
        chart_container.pack(fill="both", expand=True, pady=30)

        ctk.CTkLabel(chart_container, text="Análisis de Gastos", font=FONT_TITLE_SECTION, text_color=COLOR_TEXT_WHITE).pack(anchor="w", padx=25, pady=25)

        chart_frame = ctk.CTkFrame(chart_container, fg_color="transparent")
        chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        data = self.db.get_expenses_by_category()
        if HAS_MATPLOTLIB and data:
            categories = [x[0] for x in data]
            amounts = [x[1] for x in data]
            
            # Doughnut Chart
            # Matplotlib does not support tuples for colors, so we must pick one. 
            # We'll default to Dark theme colors for consistency within the chart for now.
            chart_bg = theme_color(COLOR_CARD_BG) 
            
            fig = plt.Figure(figsize=(6, 4), dpi=100, facecolor=theme_color(COLOR_CARD_BG))
            ax = fig.add_subplot(111)
            
            # Neon Palette: Cyan, Magenta, Blue, Orange, Purple, etc.
            # Assuming Accents are also tuples now, pick [1]
            colors = [theme_color(COLOR_ACCENT_GREEN), theme_color(COLOR_ACCENT_RED), theme_color(COLOR_ACCENT_BLUE), theme_color(COLOR_ACCENT_YELLOW), '#D2a8ff', '#58a6ff']
            
            # Wedgeprops for doughnut (width < 1 creates hole)
            wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                              startangle=90, textprops={'color':"white", 'size': 10},
                                              colors=colors, wedgeprops={'edgecolor': chart_bg, 'linewidth': 2, 'width': 0.5})
            
            # Remove spines/border
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            
            # Transparent face
            fig.patch.set_facecolor(theme_color(COLOR_CARD_BG))
            ax.set_facecolor(chart_bg)
            
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="left", fill="both", expand=True, padx=10, pady=10)
        else:
            ctk.CTkLabel(chart_frame, text="Sin datos para gráficos", text_color=COLOR_TEXT_GRAY).pack(expand=True)
