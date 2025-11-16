from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Literal, Dict, Any


@dataclass
class Claim:
    text: str
    turn_index: int
    speaker: Literal["Health Advocate", "Service Planner"]
    context_before: Optional[str] = None
    context_after: Optional[str] = None


@dataclass
class ClaimValidation:
    claim: Claim
    validity: Literal["true", "false", "unknown"]
    confidence: float
    evidence: Optional[str] = None
    server_unavailable: bool = False
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class Appointment:
    service_type: str
    start_iso: str
    end_iso: str
    staff_role: str
    location: str
    price: float
    booking_id: str


@dataclass
class PlanItem:
    month: int
    service: str
    rationale: str
    appointment: Optional[Appointment] = None
    evidence_flag: Optional[Literal["ok", "low", "unknown"]] = None


@dataclass
class PlanSummary:
    user_name: str
    total_cost: float
    items: List[PlanItem]
    warnings: List[str]
    disclaimers: List[str]

