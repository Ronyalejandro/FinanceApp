#Constantes y Enumeraciones para la Aplicación de Finanzas.

import customtkinter

# Configuración de Archivos
DB_NAME = "finanzas_personales.db"
CONFIG_FILE = ".financeapp_config.json"

# Colores (Tema Adaptativo Light/Dark)
# Formato: (Color Light, Color Dark)

COLOR_BACKGROUND = ("#F6F8FA", "#0D1117") 
COLOR_SIDEBAR = ("#FFFFFF", "#161B22")
COLOR_SIDEBAR_BORDER = ("#E1E4E8", "#30363d") 
COLOR_CARD_BG = ("#FFFFFF", "#161B22")
COLOR_CARD_BORDER = ("#D1D5DA", "#30363d")

# Textos
COLOR_TEXT_WHITE = ("#24292E", "#ffffff") # Main text (Black in light, White in dark)
COLOR_TEXT_GRAY = ("#586069", "#8b949e")

# Accents
COLOR_ACCENT_GREEN = ("#007F87", "#00F2FF")   # Cyan/Teal
COLOR_ACCENT_RED = ("#A00045", "#FF006E")     # Magenta
COLOR_ACCENT_BLUE = ("#0366d6", "#2f81f7")    # Blue
COLOR_ACCENT_YELLOW = ("#946200", "#FFB800")  # Orange/Gold

# Button/Interactive
COLOR_BTN_HOVER = ("#F3F4F6", "#222222")
COLOR_BTN_ACTIVE = ("#E1E4E8", "#1F2937")

# Fuentes
FONT_FAMILY = "Inter"
FONT_TITLE_MAIN = (FONT_FAMILY, 36, "bold")
FONT_TITLE_SECTION = (FONT_FAMILY, 32, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 18, "bold")
FONT_BODY = (FONT_FAMILY, 14)
FONT_VALUE_BIG = (FONT_FAMILY, 28, "bold")

# Tipos de Transacción
TX_TYPE_INGRESO = "Ingreso"
TX_TYPE_GASTO = "Gasto"
TX_TYPE_PAGO_CREDITO = "PagoCashea"

# Métodos de Pago
METHOD_EFECTIVO = "Efectivo"
METHOD_DEBITO = "Debito"
METHOD_CREDITO_INTERNO = "CreditoCashea"

# Categorías por defecto
CATEGORIAS = [
    "Comida", "Renta", "Transporte", "Servicios", 
    "Entretenimiento", "Salud", "Sueldo", "Freelance", "Ropa" 
]

# Helper to get appropriate color based on current appearance mode
import customtkinter as ctk

def theme_color(color_tuple):
    """Return the appropriate color from a tuple based on the current appearance mode.
    If a plain string is provided, it is returned unchanged.
    """
    # If it's already a string (e.g., legacy color), return as is
    if isinstance(color_tuple, str):
        return color_tuple
    # Expect a tuple (light, dark)
    if not isinstance(color_tuple, tuple) or len(color_tuple) != 2:
        return color_tuple
    # Determine mode
    dark = ctk.get_appearance_mode() == "Dark"
    return color_tuple[1] if dark else color_tuple[0]
