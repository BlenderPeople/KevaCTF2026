import datetime

from pydantic import BaseModel
from pydantic import Field


class BaseToken(BaseModel):
    token: str = Field(min_length=64, max_length=64)


class Token(BaseToken):
    user_id: int


class CrtToken(BaseToken):
    pass


class DBToken(Token):
    pass
