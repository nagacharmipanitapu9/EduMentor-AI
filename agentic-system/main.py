"""
CLI entry point.

Two ways to run it:

  1. Interactive (default) - you type in your own student details and
     grades, nothing is read from the seeded database for personal data.

        python main.py
        python main.py --interactive

  2. Database demo mode - looks up a pre-seeded student by id, exactly
     like the original prototype.

        python main.py --student S001
        python main.py --student S002

Resource and career *catalogs* always come from the database in either
mode - those are shared reference data, not personal student data.
"""

from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from src.graph import build_graph

console = Console()


def prompt_student_profile() -> dict:
    """Ask the user for their own student details."""
    console.print(Panel.fit(
        "Tell me a bit about yourself so I can personalize your advice.",
        title="Student Details",
    ))
    name = Prompt.ask("Your name")
    program = Prompt.ask("Program / major")
    year = IntPrompt.ask("Year of study", default=1)
    interests_raw = Prompt.ask(
        "Your interests (comma-separated, e.g. 'robotics, design')",
        default="",
    )
    interests = [i.strip() for i in interests_raw.split(",") if i.strip()]

    return {
        "student_id": "local-user",
        "name": name,
        "program": program,
        "year": year,
        "interests": interests,
    }


def prompt_grades() -> list[dict]:
    """Ask the user to enter their own grades, one subject at a time."""
    console.print(Panel.fit(
        "Now enter your grades. Leave the subject blank when you're done.",
        title="Grades",
    ))
    grades: list[dict] = []
    while True:
        subject = Prompt.ask(
            f"Subject #{len(grades) + 1} (blank to finish)", default=""
        )
        if not subject:
            break

        while True:
            score = IntPrompt.ask(f"Score for {subject} (0-100)")
            if 0 <= score <= 100:
                break
            console.print("[red]Score must be between 0 and 100.[/red]")

        term = Prompt.ask("Term", default="Current")
        grades.append({"subject": subject, "score": score, "term": term})

    if not grades:
        console.print(
            "[yellow]No grades entered - performance analysis will have "
            "nothing to work with.[/yellow]"
        )
    return grades


def render(state: dict) -> None:
    console.print(Panel.fit(state["profile_summary"], title="Student Profile"))

    perf = Table(title="Performance Analysis")
    perf.add_column("GPA")
    perf.add_column("Weak subjects")
    perf.add_column("Strong subjects")
    perf.add_row(
        str(state.get("gpa", "n/a")),
        ", ".join(state.get("weak_subjects", [])) or "-",
        ", ".join(state.get("strong_subjects", [])) or "-",
    )
    console.print(perf)
    console.print(Panel.fit(state["performance_report"], title="Report"))

    plan = Table(title="Study Plan")
    plan.add_column("Week")
    plan.add_column("Focus (subject: hours/week)")
    for week in state.get("study_plan", []):
        focus_str = ", ".join(f"{f['subject']}: {f['hours']}h" for f in week["focus"])
        plan.add_row(str(week["week"]), focus_str)
    console.print(plan)
    console.print(Panel.fit(state["study_plan_summary"], title="Planner note"))

    res = Table(title="Recommended Resources")
    res.add_column("Subject")
    res.add_column("Title")
    res.add_column("Type")
    for r in state.get("recommended_resources", []):
        res.add_row(r["subject"], r["title"], r["type"])
    console.print(res)
    console.print(Panel.fit(state["resource_rationale"], title="Why these"))

    careers = Table(title="Career Suggestions")
    careers.add_column("Career")
    careers.add_column("Related subjects")
    for c in state.get("career_suggestions", []):
        careers.add_row(c["title"], ", ".join(c["related_subjects"]))
    console.print(careers)
    console.print(Panel.fit(state["career_rationale"], title="Why these"))


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="AI Student Academic Advisor")
    parser.add_argument(
        "--student",
        help="Look up a pre-seeded student ID from the demo database (e.g. S001) "
        "instead of entering your own details.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Enter your own student details and grades (this is the default "
        "when --student is not given).",
    )
    args = parser.parse_args()

    # Resource/career catalogs always live in the database, so it must exist
    # regardless of which mode is used.
    if not os.path.exists(os.getenv("ADVISOR_DB_PATH", "data/advisor.db")):
        console.print(
            "[red]Database not found. Run `python setup.py` first.[/red]"
        )
        raise SystemExit(1)

    if args.student:
        initial_state: dict = {"student_id": args.student}
    else:
        # Default to interactive mode: collect the student's own profile
        # and grades instead of reading them from the database.
        profile = prompt_student_profile()
        grades = prompt_grades()
        initial_state = {
            "student_id": profile["student_id"],
            "profile": profile,
            "grades": grades,
        }

    app = build_graph()
    final_state = app.invoke(initial_state)
    render(final_state)


if __name__ == "__main__":
    main()
