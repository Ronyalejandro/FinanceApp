"""Security utilities for the Finance App."""
import os
import json
import hashlib
import hmac
from utils.constants import CONFIG_FILE

CONFIG_PATH = os.path.join(os.path.expanduser("~"), CONFIG_FILE)

def save_pin_hash(pin: str) -> None:
    """Save the hash of the PIN to the configuration file."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100_000)
    data = {"salt": salt.hex(), "hash": dk.hex()}
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f)
        try:
            os.chmod(CONFIG_PATH, 0o600)
        except OSError:
            pass
    except OSError:
        raise

def verify_pin(pin: str) -> bool:
    """Verify if the provided PIN matches the stored hash."""
    if not os.path.exists(CONFIG_PATH):
        return False
    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
        salt = bytes.fromhex(data["salt"])
        stored = bytes.fromhex(data["hash"])
        dk = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100_000)
        return hmac.compare_digest(dk, stored)
    except (json.JSONDecodeError, KeyError, ValueError):
        return False

def is_first_time() -> bool:
    """Check if the PIN has been set."""
    return not os.path.exists(CONFIG_PATH)
