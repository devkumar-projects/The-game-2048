from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from game.storage import application_data_directory  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Delete all locally saved players, scores and games."
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="delete without asking for confirmation",
    )
    args = parser.parse_args()

    data_directory = application_data_directory()
    if not data_directory.exists():
        print("No saved data was found.")
        return 0

    if not args.yes:
        answer = input(
            f"Delete all 2048 data in '{data_directory}'? [y/N] "
        ).strip().lower()
        if answer not in {"y", "yes"}:
            print("Cancelled.")
            return 0

    shutil.rmtree(data_directory)
    print("All local 2048 data has been deleted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
