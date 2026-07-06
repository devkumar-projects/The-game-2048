from __future__ import annotations

from pathlib import Path
import os
import sys


APP_NAME = "The Game 2048"
DATABASE_FILENAME = "scores.db"


def application_data_directory() -> Path:
    """Return the writable per-user application-data directory."""
    home = Path.home()

    if sys.platform == "darwin":
        directory = home / "Library" / "Application Support" / APP_NAME
    elif os.name == "nt":
        base = Path(os.environ.get("APPDATA", home))
        directory = base / APP_NAME
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
        directory = base / APP_NAME

    directory.mkdir(parents=True, exist_ok=True)
    return directory


def persistent_database_path(project_root: Path) -> Path:
    """Return the persistent SQLite path without storing data in the repository."""
    del project_root
    return application_data_directory() / DATABASE_FILENAME
