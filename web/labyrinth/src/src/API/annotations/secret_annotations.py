from typing import Annotated, Any

from fastapi import Depends

from src.API.depends.secret import SecretDepends

check_user = Annotated[dict[str, Any], Depends(SecretDepends.check_existence_user_by_user_id)]
