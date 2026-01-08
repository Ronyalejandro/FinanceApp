"""Constants and Enums for the Finance App."""

# Configuración de Archivos
DB_NAME = "finanzas_personales.db"
CONFIG_FILE = ".financeapp_config.json"

# Colores (Tema Dark Premium)
COLOR_BACKGROUND = "#0a0a0a"
COLOR_SIDEBAR = "#0a0a0a"
COLOR_SIDEBAR_BORDER = "#1a1a1a"
COLOR_CARD_BG = "#0a0a0a"
COLOR_CARD_BORDER = "#1a1a1a"
COLOR_TEXT_WHITE = "#ffffff"
COLOR_TEXT_GRAY = "#aaaaaa"

# Acentos
COLOR_ACCENT_GREEN = "#2eff7b"  # Ingresos / Positivo
COLOR_ACCENT_RED = "#ff3131"    # Gastos / Negativo
COLOR_ACCENT_BLUE = "#3498db"   # Balance / Neutro
COLOR_ACCENT_YELLOW = "#f1c40f" # Crédito / Precaución

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
TX_TYPE_PAGO_CREDITO = "PagoCredito"

# Métodos de Pago
METHOD_EFECTIVO = "Efectivo"
METHOD_DEBITO = "Debito"
METHOD_CREDITO_INTERNO = "CreditoInterno"

# Categorías por defecto
CATEGORIAS = [
    "Comida", "Renta", "Transporte", "Servicios", 
    "Entretenimiento", "Salud", "Sueldo", "Freelance", "Otros"
]
