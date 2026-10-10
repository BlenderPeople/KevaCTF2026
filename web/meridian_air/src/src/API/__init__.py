from .auth import router as auth_router
from .agency import router as agency_router
from .support import router as support_router
from .settings import router as settings_router

__all__ = [
    "auth_router",
    "agency_router",
    "support_router",
    "settings_router",
]
