from __future__ import annotations

from ..models import PlanAction


def lookup_evidence_for_action(action: PlanAction) -> str:
    desc = action.description.lower()
    if "sleep" in desc or "bed" in desc:
        return "Strong evidence: consistent sleep schedules support energy and mood."
    if "walk" in desc:
        return "Moderate evidence: post-meal walks aid glycemic control and digestion."
    if "dinner" in desc or "eating" in desc:
        return "Moderate evidence: earlier dinners may support circadian rhythm."
    return "General principle: gradual, sustainable routines improve long-term adherence."

