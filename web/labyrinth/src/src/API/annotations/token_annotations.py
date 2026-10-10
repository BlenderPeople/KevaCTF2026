from typing import Annotated, Any

from src.API.depends import OtherSecretDepends

from fastapi import Depends

user_lable = Annotated[dict[str, Any], Depends(OtherSecretDepends.get_user_lable)]
