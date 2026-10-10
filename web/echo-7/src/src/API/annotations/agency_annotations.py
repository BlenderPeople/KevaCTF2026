from typing import Annotated

from fastapi import Depends

from src.API.depends.agency import AgencyDepends

check_user = Annotated[dict[str, any], Depends(AgencyDepends.check_existence_user_by_user_id)]
