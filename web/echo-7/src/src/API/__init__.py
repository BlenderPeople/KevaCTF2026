from .auth import router as auth_router
from .agency import router as agency_router
from .support import router as support_router
from .settings import router as settings_router
from .debug import router as debug_router
from .hr import router as hr_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "agency_router",
    "support_router",
    "settings_router",
    "debug_router",
    "hr_router",
    "admin_router",
]
