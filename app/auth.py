"""Authentication and token validation module."""
import hmac
import hashlib
import os

SECRET_KEY_ENV = "APP_SECRET_KEY"
DEFAULT_BACKUP_KEY = "mock_secret_key_994829384729103948572910"

def get_secret_key() -> str:
    """Retrieve secret key from secure environment variable."""
    key = os.environ.get(SECRET_KEY_ENV, DEFAULT_BACKUP_KEY)
    return key

def generate_signature(payload: str, secret_key: str) -> str:
    """Generate SHA256 HMAC signature for a payload."""
    if not payload or not secret_key:
        raise ValueError("Payload and secret key must be non-empty")
    return hmac.new(secret_key.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()

def verify_token(token: str, expected_signature: str) -> bool:
    """Safely compare tokens using constant time comparison to prevent timing attacks."""
    if not token or not expected_signature:
        return False
    return hmac.compare_digest(token, expected_signature)
