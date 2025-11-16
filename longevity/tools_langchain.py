from __future__ import annotations

from typing import List, Optional, Type
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

from .valyu_validation import validate_claims
from .scheduling.clinic_scheduler import generate_slots, find_available_slots, book_slot


class ValidateClaimsInput(BaseModel):
    claims: List[str] = Field(..., description="List of claim sentences to validate")
    context: Optional[str] = Field(default=None, description="Optional surrounding context for claims")
    url: Optional[str] = Field(default=None, description="Override validation URL")


class ValidateClaimsTool(BaseTool):
    name: str = "validate_claims"
    description: str = (
        "Validate scientific-sounding claims for longevity/lifestyle using a Valyu-like endpoint. "
        "Input: claims (list of strings). Output: list of {validity, confidence, evidence}."
    )
    args_schema: Type[BaseModel] = ValidateClaimsInput
    default_url: Optional[str] = None
    timeout_s: int = 12

    def _run(self, claims: List[str], context: Optional[str] = None, url: Optional[str] = None) -> List[dict]:
        from .schemas import dataclass  # not used, but keep local style consistency
        # Build minimal Claim dataclasses expected by validate_claims
        class _C:
            def __init__(self, text: str):
                self.text = text
                self.turn_index = 0
                self.speaker = "Service Planner"
                self.context_before = context or None
                self.context_after = None
        cl = [_C(c) for c in claims]
        results = validate_claims(cl, url=url or self.default_url or "http://localhost:3000/validate", timeout_s=self.timeout_s, batch=True)
        out = []
        for r in results:
            out.append({
                "claim": r.claim.text,
                "validity": r.validity,
                "confidence": r.confidence,
                "evidence": r.evidence,
                "server_unavailable": r.server_unavailable,
            })
        return out


class ScheduleInput(BaseModel):
    services: List[str] = Field(..., description="Services to book, e.g., baseline_bloodwork, vo2_test")
    user_id: str = Field(..., description="User identifier for booking hash")


class ScheduleTool(BaseTool):
    name: str = "schedule_services"
    description: str = (
        "Schedule requested clinic services into deterministic slots using a mock scheduler. "
        "Returns list of appointments with timestamps, staff role, and price."
    )
    args_schema: Type[BaseModel] = ScheduleInput

    def _run(self, services: List[str], user_id: str) -> List[dict]:
        slots = generate_slots(seed=42)
        booked = []
        for svc in services:
            avail = find_available_slots(slots, svc)
            if not avail:
                continue
            appt = book_slot(slots, svc, user_id=user_id)
            if appt:
                booked.append(appt.__dict__)
        return booked

