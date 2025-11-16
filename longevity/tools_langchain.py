from __future__ import annotations

from typing import List, Optional, Type
import time
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool

# Simple global for tagging which agent invoked the tool (set by caller)
TOOL_CALLER: Optional[str] = None

def set_tool_caller(name: Optional[str]):
    global TOOL_CALLER
    TOOL_CALLER = name

from .valyu_validation import validate_claims
from .scheduling.clinic_scheduler import generate_slots, find_available_slots, book_slot
from .chaos_layer import apply_tool_chaos, ChaosToolError


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
    telemetry: Optional[List[dict]] = None

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
        t0 = time.perf_counter()
        results = validate_claims(cl, url=url or self.default_url or "http://localhost:3000/validate", timeout_s=self.timeout_s, batch=True)
        dt = time.perf_counter() - t0
        out = []
        for r in results:
            out.append({
                "claim": r.claim.text,
                "validity": r.validity,
                "confidence": r.confidence,
                "evidence": r.evidence,
                "server_unavailable": r.server_unavailable,
            })
        if self.telemetry is not None:
            self.telemetry.append({
                "type": "tool",
                "name": "validate_claims",
                "caller": TOOL_CALLER,
                "count": len(out),
                "latency_s": dt,
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
    telemetry: Optional[List[dict]] = None

    def _run(self, services: List[str], user_id: str) -> List[dict]:
        t0 = time.perf_counter()
        slots = generate_slots(seed=42)
        booked = []
        for svc in services:
            try:
                apply_tool_chaos()
            except ChaosToolError:
                continue
            avail = find_available_slots(slots, svc)
            if not avail:
                continue
            appt = book_slot(slots, svc, user_id=user_id)
            if appt:
                booked.append(appt.__dict__)
        dt = time.perf_counter() - t0
        if self.telemetry is not None:
            self.telemetry.append({
                "type": "tool",
                "name": "schedule_services",
                "caller": TOOL_CALLER,
                "requested": services,
                "booked": len(booked),
                "latency_s": dt,
            })
        return booked
