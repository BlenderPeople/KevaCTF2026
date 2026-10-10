from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from dataclasses import dataclass


class Base(AsyncAttrs, DeclarativeBase):
    pass


@dataclass
class JWTConfig:
    jwt_key: str
    algorithm: str
    expire: int


@dataclass
class DBConfig:
    base: Base
    db_url: str


@dataclass
class JinjaConfig:
    secret_token: str


@dataclass
class Config:
    db: DBConfig
    jwt_conf: JWTConfig
    jinja_conf: JinjaConfig
