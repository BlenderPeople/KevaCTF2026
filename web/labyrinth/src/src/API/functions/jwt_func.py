import datetime
import logging
from typing import Any

from src.configurations import main_config as mc

from fastapi import HTTPException
import jwt

logger = logging.getLogger(__name__)


class JWTConfig:
    @staticmethod
    def generate_jwt_token(
        data: dict,
        expires_delta: datetime.timedelta = datetime.timedelta(
            minutes=mc.jwt_conf.expire
        ),
    ) -> str:
        try:
            to_encode = data.copy()
            now = datetime.datetime.now(datetime.timezone.utc)
            expire = now + expires_delta
            to_encode.update({"exp": expire, "iat": now})
            return jwt.encode(
                to_encode, key=mc.jwt_conf.jwt_key, algorithm=mc.jwt_conf.algorithm
            )
        except Exception:
            logger.error("Error when generating the jwt token", exc_info=True)
            raise
    
    @staticmethod
    def decode_jwt_token(token: str) -> dict[str, Any]:
        try:
            decoded_token = jwt.decode(
                token,
                key=mc.jwt_conf.jwt_key,
                algorithms=[mc.jwt_conf.algorithm],
                options={
                    "require": ["sub", "exp", "iat", "username", "status"],
                    "verify_sub": False,
                },
            )
            return decoded_token

        except jwt.exceptions.ExpiredSignatureError:
            logger.info("Token has expired: exp claim is in the past")
            raise HTTPException(
                status_code=401,
                detail="Token has expired. Please log in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except jwt.exceptions.ImmatureSignatureError:
            logger.info("Token is not yet valid: iat claim is in the future")
            raise HTTPException(
                status_code=401,
                detail="Token is not yet valid. Please try again later.",
            )

        except jwt.exceptions.InvalidAlgorithmError:
            logger.info("Token uses an unrecognized or unsupported algorithm")
            raise HTTPException(
                status_code=401,
                detail="Token algorithm is not supported.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except jwt.exceptions.InvalidIssuedAtError:
            logger.info("Token has invalid 'iat' claim: value is not numeric")
            raise HTTPException(
                status_code=401,
                detail="Token has an invalid issuance time format.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except jwt.exceptions.InvalidSignatureError:
            logger.info("Token signature verification failed: signature mismatch")
            raise HTTPException(
                status_code=401,
                detail="Invalid token signature.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except jwt.exceptions.MissingRequiredClaimError as e:
            logger.info(
                "Token is missing required claim: %s",
                str(e) if e else "unknown",
            )
            raise HTTPException(
                status_code=401,
                detail="Token is missing required field: 'sub', 'exp', 'iat', or 'status'.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except jwt.exceptions.DecodeError:
            logger.info("Token decoding failed: malformed JWT structure")
            raise HTTPException(status_code=400, detail="Invalid token format.")

        except jwt.exceptions.InvalidTokenError:
            logger.info(
                "Token validation failed: generic invalid token error", exc_info=True
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid or malformed access token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except Exception:
            logger.error("Unexpected error during JWT token decoding", exc_info=True)
            raise
