"""
Career Guidance Agent
------------------------
Scores each career in the catalog by how much it overlaps with the
student's strong subjects and stated interests, then asks the LLM for a
short rationale for the top matches.
"""

from __future__ import annotations

from src import db
from src.llm import get_llm
from src.state import AdvisorState

TOP_N = 3

PROMPT_TEMPLATE = """# Explain career matches
You are the Career Guidance Agent. In 2-3 sentences, explain why these
careers suit a student with strong subjects [{strong}] and interests
[{interests}].

Top matches: {careers}
"""


def _score_career(career: dict, strong_subjects: set[str], interests: list[str]) -> int:
    subject_overlap = len(set(career["related_subjects"]) & strong_subjects)
    interest_overlap = sum(
        1
        for interest in interests
        for skill in career["skills"]
        if interest.lower() in skill.lower() or skill.lower() in interest.lower()
    )
    return subject_overlap * 2 + interest_overlap


def run(state: AdvisorState) -> AdvisorState:
    profile = state["profile"]
    strong = set(state.get("strong_subjects", []))
    interests = profile.get("interests", [])

    careers = db.get_all_careers()
    ranked = sorted(
        careers, key=lambda c: _score_career(c, strong, interests), reverse=True
    )
    top = ranked[:TOP_N]

    llm = get_llm()
    rationale = llm.invoke(
        PROMPT_TEMPLATE.format(
            strong=", ".join(strong) or "none yet",
            interests=", ".join(interests) or "none stated",
            careers="; ".join(c["title"] for c in top),
        )
    )

    return {
        **state,
        "career_suggestions": top,
        "career_rationale": rationale,
    }
