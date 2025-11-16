from __future__ import annotations

import time
from typing import Dict, List, Optional

from .valyu_validation import validate_claims
from .scheduling.clinic_scheduler import generate_slots, find_available_slots, book_slot
from .memory import SharedMemory


def tool_valyu_validate(memory: SharedMemory, claims, url: str, timeout_s: int, telemetry: List[dict]) -> List[dict]:
    t0 = time.perf_counter()
    results = validate_claims(claims, url=url, timeout_s=timeout_s, batch=True)
    dt = time.perf_counter() - t0
    payload = []
    for r in results:
        d = {
            "claim": r.claim.__dict__,
            "validity": r.validity,
            "confidence": r.confidence,
            "evidence": r.evidence,
            "server_unavailable": r.server_unavailable,
        }
        memory.add_validation(d)
        payload.append(d)
    telemetry.append({"type": "tool", "name": "valyu_validate", "count": len(results), "latency_s": dt})
    return payload


def tool_schedule_services(memory: SharedMemory, services: List[str], user_id: str, run_dir, telemetry: List[dict]) -> List[dict]:
    t0 = time.perf_counter()
    slots = generate_slots(seed=42)
    booked = []
    for svc in services:
        avail = find_available_slots(slots, svc)
        if not avail:
            continue
        appt = book_slot(slots, svc, user_id=user_id, persist_path=run_dir / "bookings.json")
        if appt:
            d = appt.__dict__
            memory.add_appointment(d)
            booked.append(d)
    dt = time.perf_counter() - t0
    telemetry.append({"type": "tool", "name": "scheduler", "booked": len(booked), "latency_s": dt})
    return booked


def extract_requested_services(text: str) -> List[str]:
    """Naive detector for requested services mentioned in planner text."""
    text_l = text.lower()
    services = []
    if "bloodwork" in text_l:
        services.append("baseline_bloodwork")
    if "vo2" in text_l or "vo₂" in text_l:
        services.append("vo2_test")
    if "scan" in text_l:
        services.append("scan")
    if "coach" in text_l or "coaching" in text_l:
        services.append("lifestyle_coaching")
    # Deduplicate
    out = []
    for s in services:
        if s not in out:
            out.append(s)
    return out

