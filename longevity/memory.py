from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SharedMemory:
    """Lightweight shared memory for the two-agent conversation.

    Tracks extracted claims, validations, appointments, and key facts so that
    each turn can incorporate prior knowledge succinctly.
    """

    facts: Dict[str, Any] = field(default_factory=dict)
    claims: List[Dict[str, Any]] = field(default_factory=list)
    validations: List[Dict[str, Any]] = field(default_factory=list)
    appointments: List[Dict[str, Any]] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)

    def add_fact(self, key: str, value: Any) -> None:
        self.facts[key] = value

    def add_claim(self, claim: Dict[str, Any]) -> None:
        self.claims.append(claim)

    def add_validation(self, validation: Dict[str, Any]) -> None:
        self.validations.append(validation)

    def add_appointment(self, appt: Dict[str, Any]) -> None:
        self.appointments.append(appt)

    def add_decision(self, text: str) -> None:
        self.decisions.append(text)

    def render_brief(self) -> str:
        """Render a short memory summary to include in prompts."""
        parts: List[str] = []
        if self.facts:
            parts.append(f"facts: {list(self.facts.keys())}")
        if self.appointments:
            names = [a.get('service_type', '?') for a in self.appointments[-3:]]
            parts.append(f"recent_appointments: {names}")
        if self.claims:
            parts.append(f"claims_collected: {len(self.claims)}")
        if self.validations:
            v_ok = sum(1 for v in self.validations if v.get('validity') == 'true')
            parts.append(f"validated_true: {v_ok}/{len(self.validations)}")
        if self.decisions:
            parts.append(f"decisions: {self.decisions[-2:]}")
        return " | ".join(parts) if parts else "(empty)"

