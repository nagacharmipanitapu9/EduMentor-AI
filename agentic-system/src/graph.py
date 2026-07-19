"""
Wires the five agents into a LangGraph StateGraph.

    START
      |
      v
  student_profile
      |
      v
  performance_analysis --(no grade data, < 2 retries)--> back to student_profile
      |
      (data sufficient)
      v
  study_planner
      |
      v
  resource_recommendation
      |
      v
  career_guidance
      |
      v
     END

The retry loop is a deliberate small demo of LangGraph's conditional
edges/cycles: if performance analysis finds no grade records, control
routes back to re-run the profile step (capped at 2 attempts) instead of
silently producing an empty plan.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from src.agents import (
    career_guidance_agent,
    performance_analysis_agent,
    resource_recommendation_agent,
    student_profile_agent,
    study_planner_agent,
)
from src.state import AdvisorState

MAX_PROFILE_RETRIES = 2


def _route_after_performance(state: AdvisorState) -> str:
    if state.get("data_sufficient", True):
        return "study_planner"
    if state.get("profile_retry_count", 0) < MAX_PROFILE_RETRIES:
        return "student_profile"
    # Give up looping and continue with an empty performance picture rather
    # than hang forever.
    return "study_planner"


def build_graph():
    graph = StateGraph(AdvisorState)

    graph.add_node("student_profile", student_profile_agent.run)
    graph.add_node("performance_analysis", performance_analysis_agent.run)
    graph.add_node("study_planner", study_planner_agent.run)
    graph.add_node("resource_recommendation", resource_recommendation_agent.run)
    graph.add_node("career_guidance", career_guidance_agent.run)

    graph.add_edge(START, "student_profile")
    graph.add_edge("student_profile", "performance_analysis")
    graph.add_conditional_edges(
        "performance_analysis",
        _route_after_performance,
        {"student_profile": "student_profile", "study_planner": "study_planner"},
    )
    graph.add_edge("study_planner", "resource_recommendation")
    graph.add_edge("resource_recommendation", "career_guidance")
    graph.add_edge("career_guidance", END)

    return graph.compile()
