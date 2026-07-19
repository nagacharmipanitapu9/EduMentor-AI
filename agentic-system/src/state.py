"""Shared state that flows between every node in the LangGraph pipeline."""

from __future__ import annotations

from typing import Any, TypedDict


class AdvisorState(TypedDict, total=False):
    # --- input ---
    student_id: str

    # --- Student Profile Agent ---
    profile: dict[str, Any]
    profile_summary: str

    # --- Performance Analysis Agent ---
    grades: list[dict[str, Any]]
    gpa: float
    weak_subjects: list[str]
    strong_subjects: list[str]
    performance_report: str
    data_sufficient: bool
    profile_retry_count: int

    # --- Study Planner Agent ---
    study_plan: list[dict[str, Any]]
    study_plan_summary: str

    # --- Resource Recommendation Agent ---
    recommended_resources: list[dict[str, Any]]
    resource_rationale: str

    # --- Career Guidance Agent ---
    career_suggestions: list[dict[str, Any]]
    career_rationale: str
