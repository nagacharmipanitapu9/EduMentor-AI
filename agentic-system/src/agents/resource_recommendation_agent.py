"""
Resource Recommendation Agent
--------------------------------
Looks up open resources in the catalog matching the student's weak
subjects and asks the LLM for a one-line rationale tying them together.
"""

from __future__ import annotations

from src import db
from src.llm import get_llm
from src.state import AdvisorState

PROMPT_TEMPLATE = """# Explain resource picks
You are the Resource Recommendation Agent. In 1-2 sentences, explain why
these resources are a good fit for a student weak in: {weak}

Resources: {titles}
"""


def run(state: AdvisorState) -> AdvisorState:
    weak = state.get("weak_subjects", [])
    resources = db.get_resources_for_subjects(weak)

    llm = get_llm()
    rationale = llm.invoke(
        PROMPT_TEMPLATE.format(
            weak=", ".join(weak) or "none",
            titles="; ".join(r["title"] for r in resources) or "none available yet",
        )
    )

    return {
        **state,
        "recommended_resources": resources,
        "resource_rationale": rationale,
    }
