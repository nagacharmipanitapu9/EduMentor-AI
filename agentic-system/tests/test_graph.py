"""
Basic smoke tests. Forces LLM_PROVIDER=mock so tests never depend on a
running Ollama server and are fully reproducible.
"""

import os
import sqlite3
import sys
from pathlib import Path

os.environ["LLM_PROVIDER"] = "mock"

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402

from src.graph import build_graph  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def seeded_db(tmp_path_factory):
    """Build a throwaway seeded DB so tests don't depend on setup.py having run."""
    import json

    db_path = tmp_path_factory.mktemp("data") / "advisor.db"
    os.environ["ADVISOR_DB_PATH"] = str(db_path)

    seed = json.loads((ROOT / "data" / "seed_data.json").read_text())
    conn = sqlite3.connect(db_path)
    conn.executescript((ROOT / "setup.py").read_text().split('SCHEMA = """')[1].split('"""')[0])
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
    conn.close()
    yield db_path


def test_graph_runs_end_to_end():
    app = build_graph()
    result = app.invoke({"student_id": "S001"})

    assert result["profile"]["name"] == "Charmi"
    assert result["gpa"] > 0
    assert "Operating Systems" in result["weak_subjects"]
    assert len(result["study_plan"]) == 4
    assert isinstance(result["recommended_resources"], list)
    assert len(result["career_suggestions"]) == 3


def test_unknown_student_raises():
    app = build_graph()
    with pytest.raises(Exception):
        app.invoke({"student_id": "NOT_REAL"})


def test_graph_runs_with_user_supplied_profile_and_grades():
    """The interactive CLI path: profile/grades typed by the user, not the DB."""
    app = build_graph()
    profile = {
        "student_id": "local-user",
        "name": "Alex",
        "program": "Computer Science",
        "year": 2,
        "interests": ["robotics", "design"],
    }
    grades = [
        {"subject": "Operating Systems", "score": 55, "term": "Current"},
        {"subject": "Mathematics", "score": 92, "term": "Current"},
    ]

    result = app.invoke(
        {"student_id": profile["student_id"], "profile": profile, "grades": grades}
    )

    assert result["profile"]["name"] == "Alex"
    assert result["gpa"] > 0
    assert "Operating Systems" in result["weak_subjects"]
    assert "Mathematics" in result["strong_subjects"]
    assert len(result["study_plan"]) == 4
    assert isinstance(result["recommended_resources"], list)
    assert len(result["career_suggestions"]) == 3


def test_user_supplied_empty_grades_does_not_hit_database():
    """Even an explicit empty grade list must be respected, not overridden by DB lookup."""
    app = build_graph()
    profile = {
        "student_id": "local-user-2",
        "name": "Sam",
        "program": "Design",
        "year": 1,
        "interests": [],
    }

    result = app.invoke(
        {"student_id": profile["student_id"], "profile": profile, "grades": []}
    )

    # Retry loop gives up after MAX_PROFILE_RETRIES and still finishes the run.
    assert result["data_sufficient"] is False
    assert result["grades"] == []
    assert len(result["study_plan"]) == 4
