from typing import Annotated

from src.database import get_db

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

db_annotation = Annotated[AsyncSession, Depends(get_db)]
