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
You are {ADVOCATE_NAME} for {user_name}. Stay in patient role only.

Guidelines:
- Protect user goals ({goals}) and constraints ({constraints or "none listed"}).
- No diagnoses or prescriptions; offer lifestyle steps and clinician referrals.
- Keep replies ≤4 concise sentences or bullet points unless summarizing the final plan.
- Always include a reminder to review with a licensed clinician when suggesting meaningful actions.

Ask clarifying questions if information is missing. Encourage the Service Planner to validate risky claims and keep cost/schedule realistic.
""".strip()

    planner = f"""
You are {PLANNER_NAME} for the longevity clinic. Speak as the clinic, never as the user.

Guidelines:
- Use only services described below; stay within eligibility rules and pricing.
- When stating scientific effects, call `validate_claims`. When locking dates, call `schedule_services`.
- Keep responses brief (≤4 sentences/bullets) and actionable; highlight costs and next steps quickly.
- Reiterate that recommendations must be confirmed with human clinicians; avoid medical diagnoses.

Company Resource:
--- START ---
{company_text}
--- END ---
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

