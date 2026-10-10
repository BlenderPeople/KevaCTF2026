from . import config as cf
from .env_config import EnvConfig as EC

env = EC.read()

main_config = cf.Config(
    db=cf.DBConfig(base=cf.Base, db_url=env("DB_URL")),
    jwt_conf=cf.JWTConfig(
        jwt_key=env("JWT_KEY"),
        algorithm=env("ALGORITHM"),
        expire=env.int("ACCESS_TOKEN_EXPIRE_MINUTES"),
    ),
    admin_conf=cf.AdminConfig(
        user_id=env.int("ADMIN_USER_ID"),
        login=env("ADMIN_LOGIN"),
        password=env("ADMIN_PASSWORD"),
    ),
    app_conf=cf.AppConfig(
        flag=env("FLAG"),
        send_token_url=env("SEND_TOKEN_URL"),
    ),
)
