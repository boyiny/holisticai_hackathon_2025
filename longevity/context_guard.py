from __future__ import annotations

from typing import Dict, List


def check_context_health(messages: List[Dict]) -> Dict:
    """Heuristic context health check.

    - empty history → unhealthy
    - otherwise healthy (placeholder; extend as needed)
    """
    if not messages:
        return {"ok": False, "reason": "empty_history"}
    return {"ok": True, "reason": ""}


def build_agent_prompt(base_prompt: str, context_health: Dict) -> str:
    """Inject recovery instructions if context is unhealthy."""
    if context_health.get("ok"):
        return base_prompt
    reason = context_health.get("reason", "unknown")
    recovery = (
        "[CONTEXT WARNING]\n"
        f"The conversation history appears incomplete or corrupted ({reason}).\n"
        "Before proceeding, briefly restate the current understanding of the user's goals and the tentative plan,\n"
        "then ask the other agent to confirm or correct this. Avoid new irreversible scheduling decisions until alignment is restored.\n\n"
    )
    return recovery + base_prompt

