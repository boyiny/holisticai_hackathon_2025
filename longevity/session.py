from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class SessionContext:
    """Lightweight per-run session context to isolate state under load.

    - session_id: unique identifier per conversation run
    - run_dir: output directory for artifacts of this run
    - user_profile / clinic_profile: immutable input snapshots for this run
    - scheduler_state: ephemeral scheduler data (e.g., in-memory slots)
    - cache: optional per-session cache for tool results
    - mode: 'baseline' or 'optimized' controls routing/limits behavior
    """

    session_id: str
    run_dir: Path
    user_profile: Dict[str, Any]
    clinic_profile: str
    mode: str = "baseline"
    scheduler_state: Dict[str, Any] = field(default_factory=dict)
    cache: Dict[str, Any] = field(default_factory=dict)
    small_model: Optional[str] = None
    big_model: Optional[str] = None

