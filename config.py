"""Configuración Centralizada."""
import os
import sys
from pathlib import Path

def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, compatible con PyInstaller y desarrollo. """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Rutas Base (Código y assets empaquetados)
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = Path(resource_path("assets"))

# Base de Datos (Externa al EXE, persistente en APPDATA)
if sys.platform == "win32":
    APP_DATA_DIR = Path(os.environ.get("APPDATA", os.path.expanduser("~"))) / "FinanceApp"
else:
    APP_DATA_DIR = Path(os.path.expanduser("~")) / ".financeapp"

# Asegurar que el directorio de datos existe
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_NAME = "finanzas_personales.db"
DB_PATH = APP_DATA_DIR / DB_NAME

# Configuración de Usuario
USER_CONFIG_FILE = ".financeapp_config.json"
USER_CONFIG_PATH = APP_DATA_DIR / USER_CONFIG_FILE # Movido también a APPDATA para persistencia

# Apariencia
DEFAULT_THEME = "Dark"
DEFAULT_COLOR_THEME = "dark-blue"

# Seguridad
PIN_ITERATIONS = 100_000
PIN_SALT_LENGTH = 16
MID_LENGTH = 4
