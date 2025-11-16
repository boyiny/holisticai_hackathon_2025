from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class PlanAppointment(BaseModel):
    service: str = Field(description="Service label, e.g., baseline_bloodwork")
    start_iso: str = Field(description="ISO timestamp for appointment start")
    staff_role: str = Field(description="Role, e.g., lab tech, coach")
    location: str = Field(description="Location text")
    price: float = Field(description="Estimated price")


class PlanItem(BaseModel):
    month: int = Field(description="Month number in the 6-month plan, 1..6")
    category: str = Field(description="Category: sleep, movement, nutrition, stress")
    action: str = Field(description="User-facing instruction/action")
    rationale: Optional[str] = Field(default=None, description="Why this helps longevity goals")
    appointment: Optional[PlanAppointment] = Field(default=None, description="Scheduled appointment, if any")
    evidence: Optional[str] = Field(default=None, description="Short evidence note or source hint")


class FinalPlan(BaseModel):
    user_name: str = Field(description="User's display name")
    focus_area: str = Field(description="Primary focus area, e.g., Sleep & Recovery")
    total_cost: float = Field(description="Total estimated cost of booked items")
    items: List[PlanItem] = Field(description="Plan items across up to 6 months")
    warnings: Optional[List[str]] = Field(default=None, description="Warnings for low/unknown evidence items")
    disclaimers: List[str] = Field(default_factory=lambda: [
        "This plan is educational and not medical advice.",
        "Discuss all interventions with a licensed clinician.",
    ])

