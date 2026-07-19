"""
Student Profile Agent
----------------------
Loads the student's static profile (program, year, interests) and asks the
LLM for a short natural-language summary that later agents' prompts can
reuse for context.

The profile can come from two places:
  1. `state["profile"]` - supplied directly by the user (e.g. via the CLI's
     interactive prompt), when they typed in their own details rather than
     looking themselves up in the seeded database.
  2. The database, looked up by `state["student_id"]` - the original demo
     path, kept for backwards compatibility with `--student <id>`.

If a profile is already present in state, it is used as-is and the database
is never touched for this step.
"""

from __future__ import annotations

from src import db
from src.llm import get_llm
from src.state import AdvisorState

PROMPT_TEMPLATE = """# Summarize a student profile
You are the Student Profile Agent in an academic advising system.
Write a 2-sentence summary of this student for internal use by other
advising agents. Be concrete, mention their program, year, and interests.

Student: {name}
Program: {program}, Year {year}
Interests: {interests}
"""


def run(state: AdvisorState) -> AdvisorState:
    student = state.get("profile")
    if student is None:
        # Fall back to the seeded database (original --student <id> path).
        student_id = state.get("student_id")
        if not student_id:
            raise ValueError(
                "No student profile was supplied and no student_id was given "
                "to look one up in the database."
            )
        student = db.get_student(student_id)
        if student is None:
            raise ValueError(f"Unknown student_id: {student_id!r}")

    llm = get_llm()
    prompt = PROMPT_TEMPLATE.format(
        name=student["name"],
        program=student["program"],
        year=student["year"],
        interests=", ".join(student["interests"]),
    )
    summary = llm.invoke(prompt)

    return {
        **state,
        "profile": student,
        "profile_summary": summary,
        "profile_retry_count": state.get("profile_retry_count", 0),
    }
