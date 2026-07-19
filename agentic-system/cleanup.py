#!/usr/bin/env python3
"""
Cleanup script for the AI Student Academic Advisor prototype.

Removes everything setup.py generates so the repo goes back to a clean
checkout:

    python cleanup.py            # remove generated DB + Python caches
    python cleanup.py --all      # also remove .env

Does NOT remove anything under data/seed_data.json or source files.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / "data" / "advisor.db"
ENV_FILE = ROOT / ".env"


def step(msg: str) -> None:
    print(f"\n\033[1m==> {msg}\033[0m")


def remove_database() -> None:
    step("Removing generated database")
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Removed {DB_PATH}")
    else:
        print("No database file found, nothing to do.")


def remove_python_caches() -> None:
    step("Removing __pycache__ / pytest caches")
    removed = 0
    for pattern in ("**/__pycache__", "**/.pytest_cache"):
        for path in ROOT.glob(pattern):
            shutil.rmtree(path, ignore_errors=True)
            removed += 1
    print(f"Removed {removed} cache director{'y' if removed == 1 else 'ies'}.")


def remove_env(remove_all: bool) -> None:
    if not remove_all:
        return
    step("Removing .env")
    if ENV_FILE.exists():
        ENV_FILE.unlink()
        print(f"Removed {ENV_FILE}")
    else:
        print("No .env file found, nothing to do.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean up generated project artifacts")
    parser.add_argument(
        "--all", action="store_true", help="also remove .env (forces setup.py to recreate it)"
    )
    args = parser.parse_args()

    remove_database()
    remove_python_caches()
    remove_env(args.all)

    step("Cleanup complete")
    print("Run `python setup.py` again to recreate the database (and .env if removed).")


if __name__ == "__main__":
    main()
