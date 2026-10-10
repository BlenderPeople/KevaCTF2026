from typing import Annotated

from fastapi import Form

from src import pydantic_models as pdm

field = Annotated[str, Form(min_length=8, max_length=30, pattern=pdm.pattern)]
