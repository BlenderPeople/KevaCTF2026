import datetime

from src.configurations import main_config as mc

from sqlalchemy import Date
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class HRAgency(mc.db.base):
    __tablename__ = "HRAgency"

    hr_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("User.user_id"))

    full_name: Mapped[str] = mapped_column(String(1000), unique=False, nullable=False)
    age: Mapped[int] = mapped_column(unique=False, nullable=False)
    position: Mapped[str] = mapped_column(String(1000), unique=False, nullable=False)
    organization: Mapped[str] = mapped_column(
        String(1000), unique=False, nullable=False
    )
    departament: Mapped[str] = mapped_column(String(1000), unique=False, nullable=False)
    create_date: Mapped[datetime.date] = mapped_column(Date, default=func.now())

    def __repr__(self):
        return self.__dict__
