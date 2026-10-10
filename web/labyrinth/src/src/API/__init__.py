from .auth import router as auth_router
from .secret import router as secret_router
from .support import router as support_router
from .settings import router as settings_router
from .message import router as message_router
from .profile import router as profile_router

__all__ = [
    "auth_router",
    "secret_router",
    "support_router",
    "settings_router",
    "message_router",
    "profile_router",
]
