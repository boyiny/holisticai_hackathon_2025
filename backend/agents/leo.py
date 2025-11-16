from __future__ import annotations

from typing import List
from ..models import LongevityContext, UserProfile, PlanAction, PlanDraft


def run_intake(context: LongevityContext) -> LongevityContext:
    """Simulate a simple intake to populate user_profile.
    Non-medical: focus on goals, constraints, lifestyle.
    """
    if context.user_profile is None:
        context.user_profile = UserProfile(
            user_id="demo-user",
            age=34,
            primary_goals=["better sleep", "more daytime energy"],
            constraints=["busy schedule", "no extreme diets"],
            lifestyle_summary="Sleeps late on weekdays, light movement, long desk hours.",
            sleep_pattern="irregular bed/wake times",
            activity_pattern="mostly walks on weekends",
            work_pattern="hybrid office",
        )
    return context


def draft_plan(context: LongevityContext) -> LongevityContext:
    """Draft a plan based on user_profile.
    Only habits & routines.
    """
    assert context.user_profile is not None, "user_profile is required"
    goals = context.user_profile.primary_goals
    focus = _guess_focus_area(goals)
    actions: List[PlanAction] = [
        PlanAction(description="Set consistent wind-down at 10:30pm", category="sleep", intensity="low"),
        PlanAction(description="15–20 min light walk after lunch", category="movement", intensity="low"),
        PlanAction(description="Balanced dinner, stop eating 2–3h before bed", category="nutrition", intensity="moderate"),
    ]
    context.plan_draft = PlanDraft(
        version=len(context.revision_history) + 1,
        focus_area=focus,
        primary_goals=goals,
        actions=actions,
        rationale="Simple, consistent routines improve energy and sleep regularity.",
    )
    return context


def review_plan(context: LongevityContext) -> LongevityContext:
    assert context.plan_draft is not None
    notes = [
        "Sleep window chosen for regularity.",
        "Post-meal walks aid digestion and glucose stability.",
        "Earlier dinners support circadian rhythm.",
    ]
    context.plan_review_notes.extend(notes)
    return context


def revise_plan(context: LongevityContext) -> LongevityContext:
    assert context.plan_draft is not None
    # Push current draft to history and create a new version with small adjustments
    context.revision_history.append(context.plan_draft)
    new_actions = list(context.plan_draft.actions)
    # Nudge intensity down if too aggressive
    new_actions = [
        PlanAction(
            description=a.description,
            category=a.category,
            intensity="low" if a.intensity == "high" else a.intensity,
            notes=a.notes or "adjusted for feasibility",
        )
        for a in new_actions
    ]
    context.plan_draft = PlanDraft(
        version=len(context.revision_history) + 1,
        focus_area=context.plan_draft.focus_area,
        primary_goals=context.plan_draft.primary_goals,
        actions=new_actions,
        rationale=context.plan_draft.rationale + " Revised for feasibility.",
    )
    return context


def generate_final_summary(context: LongevityContext) -> LongevityContext:
    assert context.final_plan is not None
    plan = context.final_plan
    lines = [
        "Longevity Lifestyle Plan (Educational)",
        f"Focus: {plan.focus_area}",
        "",
        "Actions:",
    ]
    for a in plan.actions:
        lines.append(f"- [{a.category}] {a.description} (intensity: {a.intensity})")
    if context.schedule:
        lines.append("")
        lines.append("Schedule:")
        for it in context.schedule.items:
            lines.append(f"- {it.datetime_iso} · {it.label} ({it.type})")
    lines.append("")
    lines.append("Disclaimer: This plan is a lifestyle-oriented, educational suggestion, not medical advice.")
    context.summary = "\n".join(lines)
    return context


def _guess_focus_area(goals: List[str]) -> str:
    text = ", ".join(goals).lower()
    if any(k in text for k in ["sleep", "circadian", "energy"]):
        return "Sleep & Recovery"
    if any(k in text for k in ["weight", "metabolic", "glucose", "energy"]):
        return "Metabolic Health"
    if any(k in text for k in ["strength", "movement", "endurance", "cardio"]):
        return "Strength & Movement"
    return "Cognitive Resilience"

