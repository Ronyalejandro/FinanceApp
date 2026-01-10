"""Utilidades de seguridad para la Aplicación de Finanzas."""
import os
import json
import hashlib
import hmac
from typing import Optional, Dict
from utils.constants import CONFIG_FILE

CONFIG_PATH = os.path.join(os.path.expanduser("~"), CONFIG_FILE)

def save_pin_hash(pin: str, question: str = None, answer: str = None) -> None:
    """Guarda el hash del PIN y opcionalmente los datos de recuperación."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100_000)
    
    # Cargar datos existentes si los hay para no sobrescribir perfil
    current_data = {}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                current_data = json.load(f)
        except:
            pass

    data = {
        "salt": salt.hex(),
        "hash": dk.hex(),
        # Mantener datos previos si no se pasan nuevos
        "security_question": question if question else current_data.get("security_question"),
        "recovery_hash": _hash_answer(answer, salt) if answer else current_data.get("recovery_hash"),
        "profile": current_data.get("profile", {})
    }
    
    _write_config(data)

def _hash_answer(answer: str, salt: bytes) -> str:
    """Genera hash para la respuesta de seguridad (normalizada)."""
    normalized = answer.lower().strip()
    dk = hashlib.pbkdf2_hmac("sha256", normalized.encode(), salt, 100_000)
    return dk.hex()

def verify_pin(pin: str) -> bool:
    """Verifica si el PIN proporcionado coincide con el hash almacenado."""
    data = _read_config()
    if not data: return False
    
    try:
        salt = bytes.fromhex(data["salt"])
        stored = bytes.fromhex(data["hash"])
        dk = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100_000)
        return hmac.compare_digest(dk, stored)
    except (KeyError, ValueError):
        return False

def verify_recovery_answer(answer: str) -> bool:
    """Verifica la respuesta de seguridad."""
    data = _read_config()
    if not data or "recovery_hash" not in data or "salt" not in data: return False

    try:
        salt = bytes.fromhex(data["salt"])
        stored = bytes.fromhex(data["recovery_hash"])
        normalized = answer.lower().strip()
        dk = hashlib.pbkdf2_hmac("sha256", normalized.encode(), salt, 100_000)
        return hmac.compare_digest(dk, stored)
    except (KeyError, ValueError):
        return False

def get_security_question() -> Optional[str]:
    data = _read_config()
    return data.get("security_question") if data else None

def save_user_profile(nombre: str, apellido: str, edad: int) -> None:
    data = _read_config()
    if not data: return # No debería pasar si se creó PIN primero
    
    data["profile"] = {
        "nombre": nombre,
        "apellido": apellido,
        "edad": edad
    }
    _write_config(data)

def get_user_profile() -> Dict:
    data = _read_config()
    return data.get("profile", {}) if data else {}

def is_first_time() -> bool:
    """Comprueba si el PIN ha sido configurado."""
    return not os.path.exists(CONFIG_PATH)

def _read_config() -> Optional[Dict]:
    if not os.path.exists(CONFIG_PATH): return None
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

def _write_config(data: Dict) -> None:
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f)
        try:
            os.chmod(CONFIG_PATH, 0o600)
        except OSError:
            pass
    except OSError:
        raise
