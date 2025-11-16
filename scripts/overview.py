from __future__ import annotations

from pathlib import Path


WORKFLOW = """
States:
 Start -> Intake -> PlanDraft -> PlanReview -> Audit -> Revision -> FinalPlan -> Scheduling -> FinalSummary
""".strip()


def main() -> None:
    print("=== ElevenLabs-style Overview ===")
    print("\n[Agent Tab]")
    print(" - Health Advocate (patient-facing)")
    print(" - Service Planner (clinic-facing)")
    print("\n[Workflow Tab]\n" + WORKFLOW)
    print("\n[Tools Tab]")
    print(" - Valyu validator (HTTP)")
    print(" - Clinic scheduler (mock)")
    print(" - File outputs + summarizer")
    print("\n[Analysis Tab]")
    _list_recent_runs()
    print("\n[Tests Tab]")
    print(" - pytest groups: consistency, chaos, load, role_confusion, scientific_safety")


def _list_recent_runs() -> None:
    data = Path("data")
    if not data.exists():
        print(" No runs yet.")
        return
    runs = sorted(p for p in data.iterdir() if p.is_dir() and p.name.startswith("longevity_plan_"))[-5:]
    if not runs:
        print(" No runs yet.")
        return
    print(" Recent runs:")
    for r in runs:
        print(f" - {r}")


if __name__ == "__main__":
    main()

