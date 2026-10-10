from typing import Optional

from pydantic import BaseModel
from pydantic import Field

pattern = r"^[^ \u0400-\u04FF\U0001F300-\U0001F9FF\u2600-\u26FF\u2700-\u27BF]+$"

class BaseUser(BaseModel):
    login: str = Field(min_length=5, max_length=30, pattern=pattern)


class PwdUser(BaseUser):
    hash_password: str


class RspUser(BaseUser):
    user_id: int


class DBUser(RspUser, PwdUser):
    pass


class UpdUser(PwdUser):
    login: Optional[str] = Field(
        default=None, min_length=5, max_length=30, pattern=pattern
    )
    hash_password: Optional[str] = None


class PageUpdUser(BaseUser):
    login: Optional[str] = Field(
        default=None, min_length=5, max_length=30, pattern=pattern
    )
    new_password: Optional[str] = Field(
        default=None, min_length=5, max_length=50, pattern=pattern
    )


class PageCrtUser(BaseUser):
    login: str = Field(
        min_length=5, max_length=30, pattern=pattern
    )
    password: str = Field(
        min_length=5, max_length=50, pattern=pattern
    )


class CrtUser(PwdUser):
    pass


class Send(BaseModel):
    login: str = Field(min_length=5, max_length=30, pattern=pattern)
    url: str = Field(min_length=1, max_length=255)
    token: str = Field(min_length=64, max_length=64)
