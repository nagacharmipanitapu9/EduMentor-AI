#!/usr/bin/env python3
"""
Project bootstrap script for the AI Student Academic Advisor prototype.

Run once before first use:

    python setup.py

What it does:
    1. Installs Python dependencies from requirements.txt.
    2. Creates a .env file from .env.example if one doesn't exist.
    3. Creates and seeds data/advisor.db (SQLite) from data/seed_data.json.
    4. Checks whether a local Ollama server is reachable and prints a hint
       if not (the app still runs via the mock LLM either way).

This is a setup helper for this prototype, not a packaging/distribution
setup.py - use pyproject.toml if this ever needs to ship as an installable
package.
"""

from __future__ import annotations

import json
import shutil
import sqlite3
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "advisor.db"
SEED_PATH = DATA_DIR / "seed_data.json"
ENV_EXAMPLE = ROOT / ".env.example"
ENV_FILE = ROOT / ".env"

SCHEMA = """
CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    interests TEXT NOT NULL  -- JSON-encoded list
);

CREATE TABLE grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL REFERENCES students(student_id),
    subject TEXT NOT NULL,
    score INTEGER NOT NULL,
    term TEXT NOT NULL
);

CREATE TABLE resources (
    resource_id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    url TEXT NOT NULL
);

CREATE TABLE careers (
    career_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    related_subjects TEXT NOT NULL,  -- JSON-encoded list
    skills TEXT NOT NULL             -- JSON-encoded list
);
"""


def step(msg: str) -> None:
    print(f"\n\033[1m==> {msg}\033[0m")


def install_dependencies() -> None:
    step("Installing Python dependencies")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt"), "--quiet"],
        check=True,
    )
    print("Dependencies installed.")


def write_env_file() -> None:
    step("Setting up .env")
    if ENV_FILE.exists():
        print(".env already exists, leaving it untouched.")
        return
    shutil.copy(ENV_EXAMPLE, ENV_FILE)
    print(f"Created {ENV_FILE} from .env.example. Edit it to change the LLM provider/model.")


def seed_database() -> None:
    step("Creating and seeding the database")
    DATA_DIR.mkdir(exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    seed = json.loads(SEED_PATH.read_text())

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        for s in seed["students"]:
            conn.execute(
                "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
                (s["student_id"], s["name"], s["program"], s["year"], json.dumps(s["interests"])),
            )
        for g in seed["grades"]:
            conn.execute(
                "INSERT INTO grades (student_id, subject, score, term) VALUES (?, ?, ?, ?)",
                (g["student_id"], g["subject"], g["score"], g["term"]),
            )
        for r in seed["resources"]:
            conn.execute(
                "INSERT INTO resources VALUES (?, ?, ?, ?, ?, ?)",
                (r["resource_id"], r["subject"], r["title"], r["type"], r["difficulty"], r["url"]),
            )
        for c in seed["careers"]:
            conn.execute(
                "INSERT INTO careers VALUES (?, ?, ?, ?)",
                (c["career_id"], c["title"], json.dumps(c["related_subjects"]), json.dumps(c["skills"])),
            )
        conn.commit()
    finally:
        conn.close()

    print(f"Seeded {DB_PATH} with {len(seed['students'])} students, "
          f"{len(seed['grades'])} grade records, {len(seed['resources'])} resources, "
          f"{len(seed['careers'])} careers.")


def check_ollama() -> None:
    step("Checking for a local Ollama server (optional)")
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        print("Ollama is reachable - real open-source LLM responses will be used.")
    except (urllib.error.URLError, ConnectionError, OSError):
        print(
            "Ollama not reachable at localhost:11434. That's fine - the "
            "prototype will use a deterministic mock LLM instead.\n"
            "To use a real open-source model: install Ollama "
            "(https://ollama.com), run `ollama pull llama3.1`, then `ollama serve`."
        )


def main() -> None:
    install_dependencies()
    write_env_file()
    seed_database()
    check_ollama()
    step("Setup complete")
    print("Try it:\n    python main.py --student S001\n    python main.py --student S002")


if __name__ == "__main__":
    main()
