"""
Study Planner Agent
---------------------
Builds a week-by-week study schedule. Allocation of hours is a deterministic
rule (weakest subject gets the most hours) so the plan is explainable; the
LLM is only used to turn that schedule into a readable narrative blurb.
"""

from __future__ import annotations

from src.llm import get_llm
from src.state import AdvisorState

TOTAL_WEEKLY_HOURS = 10
PLAN_WEEKS = 4

PROMPT_TEMPLATE = """# Write a study plan summary
You are the Study Planner Agent. In 2-3 sentences, motivate the student to
follow this {weeks}-week plan built around their weakest subjects first.

Weak subjects (priority order): {weak}
Weekly hour budget: {hours}
"""


def _allocate_hours(weak_subjects: list[str]) -> dict[str, int]:
    """Weakest subject (first in list) gets the largest share of hours."""
    if not weak_subjects:
        return {}
    weights = list(range(len(weak_subjects), 0, -1))  # e.g. [3, 2, 1]
    total_weight = sum(weights)
    hours = {}
    for subject, weight in zip(weak_subjects, weights):
        hours[subject] = round(TOTAL_WEEKLY_HOURS * weight / total_weight)
    return hours


def run(state: AdvisorState) -> AdvisorState:
    weak = state.get("weak_subjects", [])
    hours_per_subject = _allocate_hours(weak)

    plan = []
    for week in range(1, PLAN_WEEKS + 1):
        plan.append(
            {
                "week": week,
                "focus": [
                    {"subject": s, "hours": h} for s, h in hours_per_subject.items()
                ]
                or [{"subject": "Review strong subjects", "hours": TOTAL_WEEKLY_HOURS}],
            }
        )

    llm = get_llm()
    summary = llm.invoke(
        PROMPT_TEMPLATE.format(
            weeks=PLAN_WEEKS,
            weak=", ".join(weak) or "none - keep sharpening your strong subjects",
            hours=TOTAL_WEEKLY_HOURS,
        )
    )

    return {
        **state,
        "study_plan": plan,
        "study_plan_summary": summary,
    }
