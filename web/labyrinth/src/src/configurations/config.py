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
class AdminConfig:
    user_id: int
    login: str
    password: str


@dataclass
class AppConfig:
    flag: str
    send_token_url: str


@dataclass
class Config:
    db: DBConfig
    jwt_conf: JWTConfig
    admin_conf: AdminConfig
    app_conf: AppConfig
