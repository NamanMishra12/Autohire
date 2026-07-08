import base64
import os

from cryptography.fernet import Fernet

from app.utils.logger import logger


def _get_or_create_key() -> bytes:
    """
    Uses ENCRYPTION_KEY from env if set, otherwise generates
    a key and saves it to .encryption_key file.
    In production this must come from env/secrets manager.
    """
    key_file = ".encryption_key"

    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()

    key = Fernet.generate_key()

    with open(key_file, "wb") as f:
        f.write(key)

    logger.info("Generated new encryption key — store .encryption_key securely.")
    return key


_fernet = Fernet(_get_or_create_key())


def encrypt(data: str) -> str:
    return _fernet.encrypt(data.encode()).decode()


def decrypt(data: str) -> str:
    return _fernet.decrypt(data.encode()).decode()