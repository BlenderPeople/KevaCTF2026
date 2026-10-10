import logging

from src.API.api_config import templates
from src.API import annotations as ann
from src.API.functions import SecretFunc
from src.configurations import main_config
from src import pydantic_models as pdm
from src.database import TokenManager
from src.database import UserManager


from fastapi import APIRouter
from fastapi import HTTPException
from fastapi import Request

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Pages"])

FILE_LIBRARY = [
    {
        "icon": "DOC",
        "name": "lab_map_v2.pdf",
        "content": (
            "LABYRINTH MAP // VERSION 2\n"
            "\n"
            "1. Центральный терминал соединён с тремя секторами: B-3, D-9, X-13.\n"
            "2. Аварийный путь из сектора B-3 ведёт к архивному шлюзу.\n"
            "3. Доступ в архив открывается только после повторной проверки токена.\n"
            "4. Помеченные зоны без подписи считаются нестабильными."
        ),
    },
    {
        "icon": "LOG",
        "name": "session_2024.log",
        "content": (
            "[21:11:07] INFO  session initialized\n"
            "[21:11:09] WARN  unknown login attempt detected\n"
            "[21:11:14] INFO  route /files opened successfully\n"
            "[21:11:18] WARN  hidden file marker found in archive index\n"
            "[21:11:24] INFO  operator disconnected"
        ),
    },
    {
        "icon": "CFG",
        "name": "terminal_config.ini",
        "content": (
            "[display]\n"
            "mode=terminal\n"
            "layout=fullscreen\n"
            "header=fixed\n"
            "footer=fixed\n"
            "\n"
            "[security]\n"
            "file_preview=token_required\n"
            "audit=true"
        ),
    },
    {
        "icon": "TXT",
        "name": "alice_notes.txt",
        "content": (
            "Alice memo:\n"
            "Не верь спокойному интерфейсу. Самые важные вещи спрятаны в тех местах,\n"
            "которые выглядят как шум. Если файл просит токен, значит он ещё не готов\n"
            "довериться тебе полностью."
        ),
    },
    {
        "icon": "DAT",
        "name": "user_database.dat",
        "content": (
            "users_total=17\n"
            "active_sessions=3\n"
            "suspended=2\n"
            "last_admin_login=unknown\n"
            "integrity=warning"
        ),
    },
    {
        "icon": "BIN",
        "name": "sector_keys.bin",
        "content": (
            "BINARY INDEX\n"
            "01000010 00101101 00110011\n"
            "01000100 00101101 00111001\n"
            "01011000 00101101 00110001 00110011\n"
            "\n"
            "Decoded labels: B-3, D-9, X-13"
        ),
    },
    {
        "icon": "ENC",
        "name": "encrypted_message.enc",
        "content": (
            "-----BEGIN ENCRYPTED BLOB-----\n"
            "4f1b7c9ea8120d17f98ea13c0dd8f773f1ab\n"
            "7c9b210e4a33fe9a7e2cbb89126d5b9130f0\n"
            "-----END ENCRYPTED BLOB-----\n"
            "\n"
            "Status: ciphertext only, manual decryption required."
        ),
    },
    {
        "icon": "CSV",
        "name": "access_log.csv",
        "content": (
            "time,route,status\n"
            "21:10:01,/login,200\n"
            "21:10:04,/profile,200\n"
            "21:10:11,/files,200\n"
            "21:10:19,/send-token,200\n"
            "21:10:27,/support,200"
        ),
    },
    {
        "icon": "SYS",
        "name": "system_override.sys",
        "content": (
            "override.enabled=false\n"
            "fallback.protocol=manual\n"
            "ui.profile=labyrinth\n"
            "notes=change requires elevated access"
        ),
    },
    {
        "icon": "BAK",
        "name": "backup_2023.bak",
        "content": (
            "Backup snapshot created: 2023-12-19T04:11:26Z\n"
            "Included modules: auth, profile, files, support\n"
            "Archive status: partial\n"
            "Checksum: 2a9c7f11dce3"
        ),
    },
    {
        "icon": "JSON",
        "name": "token_cache.json",
        "content": (
            '{\n'
            '  "cache_status": "stale",\n'
            '  "last_rotation": "2026-03-20T11:43:00Z",\n'
            '  "linked_sessions": 3,\n'
            '  "manual_confirmation": true\n'
            '}'
        ),
    },
    {
        "icon": "TOP",
        "name": "TopSecretFile",
        "content": None,
    },
]


def get_visible_files() -> list[dict[str, str | None]]:
    return list(FILE_LIBRARY)


@router.get("/", tags=["Pages"])
async def secret_page(
    request: Request,
    user_lable: ann.user_lable,
):
    try:
        return templates.TemplateResponse(
            request=request,
            name="secret.html",
            context=user_lable,
        )
    except Exception:
        logger.error("Error when sending the page /", exc_info=True)
        raise


@router.get("/files", tags=["Pages"])
async def files_page(
    request: Request,
    user_lable: ann.user_lable,
):
    try:
        context = dict(user_lable)
        context["files"] = get_visible_files()
        return templates.TemplateResponse(
            request=request,
            name="files.html",
            context=context,
        )
    except Exception:
        logger.error("Error when sending the page /files", exc_info=True)
        raise


@router.post("/files/content", tags=["Files"])
async def file_content(
    payload: pdm.FileAccessRequest,
    token_data: ann.check_user,
    db_session: ann.db_annotation,
):
    visible_files = {file_data["name"]: file_data for file_data in get_visible_files()}
    file_data = visible_files.get(payload.file_name)
    if file_data is None:
        raise HTTPException(status_code=404, detail="Файл не найден.")

    provided_token = payload.token.strip()
    if not provided_token:
        raise HTTPException(status_code=400, detail="Токен доступа обязателен.")

    token_manager = TokenManager(db_session)
    token_record = await token_manager.get_token_by_value(provided_token)
    if token_record is None:
        raise HTTPException(status_code=403, detail="Неверный токен доступа.")

    if payload.file_name == "TopSecretFile":
        user_manager = UserManager(db_session)
        token_owner = await user_manager.get_user(token_record.user_id)
        is_admin_token = token_record.user_id == main_config.admin_conf.user_id
        if token_owner is not None and token_owner.login == main_config.admin_conf.login:
            is_admin_token = True
        if not is_admin_token:
            raise HTTPException(status_code=403, detail="TopSecretFile доступен только по admin-токену.")
        return {
            "name": file_data["name"],
            "content": main_config.app_conf.flag,
        }

    current_user_token = await token_manager.get_token_by_user_id(token_data["sub"])
    if current_user_token is None:
        token_value = await SecretFunc.ensure_access_token(token_data["sub"], db_session)
        current_user_token = (
            await token_manager.get_token_by_user_id(token_data["sub"])
            if token_value
            else None
        )
    if current_user_token is None or token_record.token != current_user_token.token:
        raise HTTPException(status_code=403, detail="Используйте токен, назначенный вашему профилю.")

    return {"name": file_data["name"], "content": file_data["content"]}
