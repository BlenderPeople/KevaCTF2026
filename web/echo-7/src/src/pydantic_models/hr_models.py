import datetime

from pydantic import BaseModel
from pydantic import Field


class BaseHR(BaseModel):
    full_name: str = Field(min_length=1, max_length=1000)
    age: int = Field(ge=1, le=150)
    position: str = Field(min_length=1, max_length=1000)
    organization: str = Field(min_length=1, max_length=1000)
    departament: str = Field(min_length=1, max_length=1000)
    create_date: datetime.date


class CrtHR(BaseHR):
    user_id: int


class PageCrtHR(BaseHR):
    pass


class DBHR(CrtHR):
    hr_id: int


class RspHR(DBHR):
    pass
