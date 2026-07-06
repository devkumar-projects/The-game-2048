from __future__ import annotations

import platform
import sqlite3
import sys


def main() -> int:
    print(f"Python: {sys.version.split()[0]}")
    print(f"Platform: {platform.platform()}")
    print(f"SQLite: {sqlite3.sqlite_version}")

    if sys.version_info < (3, 10):
        print("ERROR: Python 3.10 or newer is required.")
        return 1

    try:
        import tkinter  # noqa: F401
    except ImportError as exc:
        print(f"ERROR: Tkinter is not available: {exc}")
        print("Read the installation section in README.md.")
        return 1

    print("Tkinter: available")
    print("Environment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
