import logging
import pwdlib

logger = logging.getLogger(__name__)

password_hash = pwdlib.PasswordHash.recommended()


class HashPassword:
    @staticmethod
    def hash_password(password: str) -> str:
        try:
            return password_hash.hash(password)
        except Exception:
            logger.error("Password hashing error", exc_info=True)
            raise

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            return password_hash.verify(plain_password, hashed_password)
        except Exception:
            logger.error("Error checking passwords hashes", exc_info=True)
            raise
