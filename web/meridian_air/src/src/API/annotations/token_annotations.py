from typing import Annotated

from src.API.depends import OtherAgencyDepends

from fastapi import Depends

user_lable = Annotated[dict[str, any], Depends(OtherAgencyDepends.get_user_lable)]
