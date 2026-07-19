"""
Thin SQLite data-access layer (stdlib sqlite3 - no external DB needed).

The database is created and seeded by setup.py. Agents only ever read
through the functions here, so the storage engine can be swapped later
(e.g. for Postgres) without touching agent code.
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager

DB_PATH = os.getenv("ADVISOR_DB_PATH", "data/advisor.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_student(student_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
        if row is None:
            return None
        student = dict(row)
        student["interests"] = json.loads(student["interests"])
        return student


def get_grades(student_id: str) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT subject, score, term FROM grades WHERE student_id = ?",
            (student_id,),
        ).fetchall()
        return [dict(r) for r in rows]


def get_resources_for_subjects(subjects: list[str]) -> list[dict]:
    if not subjects:
        return []
    with get_conn() as conn:
        placeholders = ",".join("?" for _ in subjects)
        rows = conn.execute(
            f"SELECT * FROM resources WHERE subject IN ({placeholders})",
            subjects,
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_careers() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM careers").fetchall()
        careers = []
        for r in rows:
            c = dict(r)
            c["related_subjects"] = json.loads(c["related_subjects"])
            c["skills"] = json.loads(c["skills"])
            careers.append(c)
        return careers
