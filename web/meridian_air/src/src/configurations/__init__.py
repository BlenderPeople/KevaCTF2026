from . import config as cf
from .env_config import EnvConfig as EC

env = EC.read()

main_config = cf.Config(
    db=cf.DBConfig(base=cf.Base, db_url=env("DB_URL")),
    flag=env("FLAG"),
    jwt_conf=cf.JWTConfig(
        jwt_key=env("JWT_KEY"),
        algorithm=env("ALGORITHM"),
        expire=env.int("ACCESS_TOKEN_EXPIRE_MINUTES"),
    )
)
