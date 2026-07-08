import hashlib
import hmac
import secrets
from app.core.config import settings
from app.interfaces.services import ApiKeyGeneratorInterface


class ApiKeyGenerator(ApiKeyGeneratorInterface):

    def __init__(self, prefix: str = None, num_bytes: int = None):
        self.prefix = prefix if prefix is not None else settings.api_key_prefix
        self.num_bytes = num_bytes if num_bytes is not None else settings.api_key_bytes

    def generate(self) -> str:
        return f"{self.prefix}{secrets.token_urlsafe(self.num_bytes)}"

    def hash(self, raw_key: str) -> str:
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def verify(self, raw_key: str, key_hash: str) -> bool:
        return hmac.compare_digest(self.hash(raw_key), key_hash)
