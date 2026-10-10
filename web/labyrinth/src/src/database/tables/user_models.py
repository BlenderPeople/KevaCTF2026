from src.configurations import main_config as mc

from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class User(mc.db.base):
    __tablename__ = "User"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    hash_password: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"User(user_id={self.user_id}, login={self.login!r})"
