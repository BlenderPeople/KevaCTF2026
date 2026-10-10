import os
import logging
from dotenv import dotenv_values

from src.configurations import main_config as mc

logger = logging.getLogger(__name__)


class JinjaFilters:
    @staticmethod
    def _load_env_file(env_name: str) -> dict:
        logger.info(f"Environment reading request {env_name=}: _load_env_file")
        if env_name != ".env.admin":
            return {}
        try:
            env_path = os.path.join(os.getcwd(), env_name)

            if os.path.exists(env_path):
                return dotenv_values(env_path)

            return {}
        except Exception:
            logger.error(f"environment reading error {env_name=}", exc_info=True)
            raise

    @staticmethod
    def ae(value: str = "", token: str = "", env_name: str = "") -> str:
        try:
            logger.info(
                f"Launching the _ae filter token={token is not None} env_name={env_name is not None}"
            )

            if not isinstance(token, str):
                logger.info(
                    f"Invalid token format: expected str, got {type(token).__name__}"
                )
                return f"Error: invalid token format (expected str, got {type(token).__name__})"

            if not isinstance(env_name, str):
                logger.info(
                    f"Invalid env_name format: expected str, got {type(env_name).__name__}"
                )
                return f"Error: invalid env_name format (expected str, got {type(env_name).__name__})"

            if not token:
                logger.info("Token not provided for _ae filter")
                return "Error: token required"

            if token != mc.jinja_conf.secret_token:
                logger.info("Invalid token provided for _ae filter")
                return "Error: invalid token"

            if not env_name:
                logger.info("env_name not provided for _ae filter")
                return "Error: env_name required"

            env_data = JinjaFilters._load_env_file(env_name)

            if not env_data:
                logger.info(f"env file '{env_name}' not found")
                return f"Error: env '{env_name}' not found"

            result_lines = [f"{k}={v}" for k, v in sorted(env_data.items())]
            return "\n".join(result_lines)
        except Exception:
            logger.error(
                f"Error during operation of the _ae filter token={token} env_name={env_name}",
                exc_info=True,
            )
            return "Error: internal server error"
