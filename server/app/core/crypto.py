import base64
import hashlib
from cryptography.fernet import Fernet
from app.core.config import settings

def _derive_key(secret: str) -> bytes:
    # Derive a 32-byte key from SECRET_KEY using SHA256 and base64-url encode for Fernet
    h = hashlib.sha256(secret.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(h)

def get_fernet():
    key = _derive_key(settings.SECRET_KEY or 'replace-me-with-secure-random')
    return Fernet(key)

def encrypt(plaintext: str) -> str:
    f = get_fernet()
    return f.encrypt(plaintext.encode('utf-8')).decode('utf-8')

def decrypt(token: str) -> str:
    f = get_fernet()
    return f.decrypt(token.encode('utf-8')).decode('utf-8')
