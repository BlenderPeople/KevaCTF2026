from pydantic import BaseModel
from pydantic import Field


class FileAccessRequest(BaseModel):
    file_name: str = Field(min_length=1, max_length=120)
    token: str = Field(min_length=1, max_length=2048)
