import datetime

from src.configurations import main_config as mc

from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Token(mc.db.base):
    __tablename__ = "Token"
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("User.user_id"), primary_key=True)
    token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    def __repr__(self):
        return f"Token(user_id={self.user_id})"
