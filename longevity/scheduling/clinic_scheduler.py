from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
import hashlib
import json
from pathlib import Path

from ..schemas import Appointment


@dataclass
class Slot:
    service_type: str
    start_iso: str
    end_iso: str
    staff_role: str
    location: str
    price: float
    booked: bool = False


def _deterministic_dates(seed: int, months: int = 6, per_month: int = 3) -> List[datetime]:
    # Simple deterministic schedule: fixed days per month based on seed
    base = datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0)
    dates: List[datetime] = []
    for m in range(months):
        for i in range(per_month):
            day = 3 + i * 7  # 3rd, 10th, 17th (roughly)
            dt = (base + timedelta(days=30 * m)).replace(day=min(day, 28))
            dates.append(dt)
    return dates


def generate_slots(seed: int | None = 42) -> List[Slot]:
    # Deterministic slots for services
    services = [
        ("baseline_bloodwork", "lab tech", 120.0),
        ("vo2_test", "coach", 150.0),
        ("scan", "nurse", 300.0),
        ("lifestyle_coaching", "coach", 80.0),
    ]
    dates = _deterministic_dates(seed or 42)
    slots: List[Slot] = []
    for idx, dt in enumerate(dates):
        svc, staff, price = services[idx % len(services)]
        end = dt + timedelta(hours=1)
        slots.append(
            Slot(
                service_type=svc,
                start_iso=dt.isoformat() + "Z",
                end_iso=end.isoformat() + "Z",
                staff_role=staff,
                location="Main Clinic",
                price=price,
            )
        )
    return slots


def find_available_slots(
    slots: List[Slot], service_type: str, user_availability: Optional[List[str]] = None, blackout_dates: Optional[List[str]] = None
) -> List[Slot]:
    # For now, ignore user_availability beyond simple placeholder
    blk = set(blackout_dates or [])
    return [s for s in slots if (not s.booked) and s.service_type == service_type and s.start_iso[:10] not in blk]


def book_slot(slots: List[Slot], service_type: str, user_id: str, persist_path: Optional[Path] = None) -> Optional[Appointment]:
    for s in slots:
        if not s.booked and s.service_type == service_type:
            s.booked = True
            bid = hashlib.sha1(f"{user_id}-{s.start_iso}-{s.service_type}".encode()).hexdigest()[:10]
            appt = Appointment(
                service_type=s.service_type,
                start_iso=s.start_iso,
                end_iso=s.end_iso,
                staff_role=s.staff_role,
                location=s.location,
                price=s.price,
                booking_id=bid,
            )
            if persist_path:
                _persist_booking(persist_path, appt)
            return appt
    return None


def _persist_booking(path: Path, appt: Appointment) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if path.exists():
        try:
            existing = json.loads(path.read_text())
        except Exception:
            existing = []
    existing.append(appt.__dict__)
    path.write_text(json.dumps(existing, indent=2))

