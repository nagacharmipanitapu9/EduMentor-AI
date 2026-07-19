"""
Performance Analysis Agent
----------------------------
Turns raw grade records into a GPA, a ranked list of weak/strong subjects,
and a narrative report. Also flags whether there was enough data to work
with - if not, the graph loops back to the Student Profile Agent (see
graph.py) instead of guessing.

Weak/strong subject detection is a plain deterministic rule (score < 70),
not an LLM call - that keeps the number that decides "which subjects need
help" auditable and reproducible instead of an opaque model guess.

Grades can come from two places, same as the profile:
  1. `state["grades"]` - typed in directly by the user. This is checked
     first; if the key is present at all (even as an empty list) it is
     trusted and the database is not queried.
  2. The seeded database, looked up by student_id - the original demo path.
"""

from __future__ import annotations

from src import db
from src.llm import get_llm
from src.state import AdvisorState

WEAK_THRESHOLD = 70

PROMPT_TEMPLATE = """# Write a performance report
You are the Performance Analysis Agent. Write a short, encouraging but
honest performance report for the student below.

Student: {name}
GPA (0-100 scale): {gpa:.1f}
Weak subjects (score < {threshold}): {weak}
Strong subjects: {strong}
"""


def run(state: AdvisorState) -> AdvisorState:
    student = state["profile"]

    # User-supplied grades take priority. `state.get("grades")` returns
    # `None` only when the key was never set at all (e.g. the DB-driven
    # `--student <id>` path), which is the signal to fall back to the DB.
    # A user who explicitly submitted an empty list is still respected -
    # that correctly triggers the "not enough data" retry path below.
    grades = state.get("grades")
    if grades is None:
        grades = db.get_grades(student.get("student_id", ""))

    if not grades:
        # Not enough data yet - signal the graph to route back and try
        # augmenting the profile rather than analyzing nothing.
        return {
            **state,
            "grades": [],
            "data_sufficient": False,
            "profile_retry_count": state.get("profile_retry_count", 0) + 1,
        }

    scores = [g["score"] for g in grades]
    gpa = sum(scores) / len(scores)
    weak = sorted(
        [g["subject"] for g in grades if g["score"] < WEAK_THRESHOLD],
        key=lambda s: next(g["score"] for g in grades if g["subject"] == s),
    )
    strong = [g["subject"] for g in grades if g["score"] >= WEAK_THRESHOLD]

    llm = get_llm()
    report = llm.invoke(
        PROMPT_TEMPLATE.format(
            name=student["name"],
            gpa=gpa,
            threshold=WEAK_THRESHOLD,
            weak=", ".join(weak) or "none",
            strong=", ".join(strong) or "none",
        )
    )

    return {
        **state,
        "grades": grades,
        "gpa": round(gpa, 1),
        "weak_subjects": weak,
        "strong_subjects": strong,
        "performance_report": report,
        "data_sufficient": True,
    }
