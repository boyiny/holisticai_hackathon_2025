from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelRouter:
    """Simple frugal routing between small and big model.

    choose_model(task_type, turn_index, speaker) -> model_name
    """

    small_model: str
    big_model: str

    def choose_model(self, task_type: str, turn_index: int, speaker: str) -> str:
        # Prefer small model for acknowledgements and light turns
        tt = (task_type or "").lower()
        sp = (speaker or "").lower()
        if tt in {"chitchat", "ack", "confirmation"}:
            return self.small_model
        # Heuristic: planner every 3rd turn uses big model for synthesis
        if sp == "planner" and (turn_index % 3 == 0):
            return self.big_model
        if tt in {"plan_synthesis", "complex_reasoning"}:
            return self.big_model
        return self.small_model

