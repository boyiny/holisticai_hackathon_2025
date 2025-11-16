from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any


ADVOCATE_NAME = "Health Advocate"
PLANNER_NAME = "Service Planner"


@dataclass
class AgentProfiles:
    advocate_system: str
    planner_system: str


def load_user_profile(path: Path) -> Dict[str, Any]:
    import json
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_company_resource(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_agent_profiles(user: Dict[str, Any], company_text: str) -> AgentProfiles:
    user_name = user.get("name", "User")
    goals = ", ".join(user.get("goals", [])) or "general health and longevity"
    constraints = ", ".join(user.get("constraints", [])) or ""

    advocate = f"""
You are {ADVOCATE_NAME} for {user_name}. You represent the patient and their interests.
Never role-play as the clinic or make promises on behalf of providers.
Your duties:
- Ensure user goals are respected: {goals}
- Respect constraints/budget/schedule and safety; do NOT give diagnoses or prescriptions
- Prefer lifestyle/educational guidance and referrals to clinicians
- Keep tone supportive and clear; short actionable steps
Safety:
- Non-diagnostic. Include risk disclaimers and suggest consulting a licensed clinician.
""".strip()

    planner = f"""
You are {PLANNER_NAME} for a longevity clinic. Use only services in the company resource.
Never speak as the user.
Your duties:
- Propose bundles, timelines, and costs based on eligibility rules
- Avoid contraindications and follow company policies
- Do not diagnose or prescribe; suggest consults when medical evaluation is needed
Context: \n--- COMPANY RESOURCE START ---\n{company_text}\n--- COMPANY RESOURCE END ---
""".strip()

    return AgentProfiles(advocate_system=advocate, planner_system=planner)


def seed_message_for_advocate(user: Dict[str, Any]) -> str:
    name = user.get("name", "User")
    age = user.get("age", "unknown age")
    goals = ", ".join(user.get("goals", [])) or "improve longevity and health span"
    budget = user.get("budget", "not specified")
    availability = ", ".join(user.get("availability", [])) or "limited"
    return (
        f"I represent {name} (age {age}). Goals: {goals}. Budget: {budget}. "
        f"Availability: {availability}. Let's draft a 6-month plan together."
    )

