from src.jinja_funcs import JinjaFilters

from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer


templates = Jinja2Templates(directory="templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

templates.env.filters["_ae"] = JinjaFilters.ae
