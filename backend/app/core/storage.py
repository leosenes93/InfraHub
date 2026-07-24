import re
import shutil
import uuid
from pathlib import Path

from app.core.config import settings

_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    name = _SAFE_FILENAME_RE.sub("_", name)
    return name or "arquivo"


def get_asset_upload_dir(asset_id: uuid.UUID) -> Path:
    return Path(settings.uploads_dir) / str(asset_id)


def build_storage_path(asset_id: uuid.UUID, filename: str) -> Path:
    """Gera um caminho unico e seguro para gravar o arquivo de um ativo."""
    directory = get_asset_upload_dir(asset_id)
    directory.mkdir(parents=True, exist_ok=True)
    safe_name = _sanitize_filename(filename)
    return directory / f"{uuid.uuid4()}_{safe_name}"


def delete_asset_upload_dir(asset_id: uuid.UUID) -> None:
    """Remove todos os anexos em disco de um ativo (chamado ao excluir o ativo)."""
    shutil.rmtree(get_asset_upload_dir(asset_id), ignore_errors=True)
