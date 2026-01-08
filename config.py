"""Centralized Configuration."""
import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "db"
ASSETS_DIR = BASE_DIR / "assets"

# Database
DB_NAME = "finanzas_personales.db"
DB_PATH = DB_DIR / DB_NAME

# User Config
USER_CONFIG_FILE = ".financeapp_config.json"
USER_CONFIG_PATH = Path(os.path.expanduser("~")) / USER_CONFIG_FILE

# Appearance
DEFAULT_THEME = "Dark"
DEFAULT_COLOR_THEME = "dark-blue"

# Security
PIN_ITERATIONS = 100_000
PIN_SALT_LENGTH = 16
MID_LENGTH = 4
