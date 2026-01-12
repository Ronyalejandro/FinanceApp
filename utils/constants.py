# Constantes y Enumeraciones para la Aplicación de Finanzas.

import customtkinter

# Configuración de Archivos
DB_NAME = "finanzas_personales.db"
CONFIG_FILE = ".financeapp_config.json"

# Colores (Tema Adaptativo Light/Dark)
# Formato: (Color Claro, Color Oscuro)

COLOR_BACKGROUND = ("#F6F8FA", "#0D1117") 
COLOR_SIDEBAR = ("#FFFFFF", "#161B22")
COLOR_SIDEBAR_BORDER = ("#E1E4E8", "#30363d") 
COLOR_CARD_BG = ("#FFFFFF", "#161B22")
COLOR_CARD_BORDER = ("#D1D5DA", "#30363d")

# Textos
COLOR_TEXT_WHITE = ("#24292E", "#ffffff") # Texto principal (Negro en claro, Blanco en oscuro)
COLOR_TEXT_GRAY = ("#586069", "#8b949e")

# Acentos
COLOR_ACCENT_GREEN = ("#007F87", "#00F2FF")   # Cian/Teal
COLOR_ACCENT_RED = ("#A00045", "#FF006E")     # Magenta
COLOR_ACCENT_BLUE = ("#0366d6", "#2f81f7")    # Azul
COLOR_ACCENT_YELLOW = ("#946200", "#FFB800")  # Naranja/Oro

# Botones/Interactivo
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

# Helper para obtener el color apropiado basado en el modo de apariencia actual
import customtkinter as ctk

def theme_color(color_tuple):
    """Devuelve el color apropiado de una tupla basado en el modo de apariencia actual.
    Si se proporciona una cadena simple, se devuelve sin cambios.
    """
    # Si ya es una cadena (ej. color legado), devolver tal cual
    if isinstance(color_tuple, str):
        return color_tuple
    # Se espera una tupla (claro, oscuro)
    if not isinstance(color_tuple, tuple) or len(color_tuple) != 2:
        return color_tuple
    # Determinar el modo
    dark = ctk.get_appearance_mode() == "Dark"
    return color_tuple[1] if dark else color_tuple[0]
