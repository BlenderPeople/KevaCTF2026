import hashlib
import logging

logger = logging.getLogger(__name__)


class HashPassword:
    @staticmethod
    def hash_password(password: str) -> str:
        try:
            return hashlib.sha256(password.encode()).hexdigest()
        except Exception:
            logger.error("Password hashing error", exc_info=True)
            raise

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return HashPassword.hash_password(plain_password) == hashed_password
        except Exception:
            logger.error("Error checking passwords hashes", exc_info=True)
            raise
