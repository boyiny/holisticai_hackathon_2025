from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Runtime configuration for longevity conversation runs."""

    # Conversation
    turn_limit: int = 10
    model: str = "gpt-4o-mini"  # default to OpenAI reasonable-cost model

    # Inputs
    user_profile_path: Path = Path("user_info.json")
    company_resource_path: Path = Path("company_resource.txt")

    # Validation
    enable_valyu: bool = True
    valyu_url: str = "http://localhost:3000/validate"
    valyu_timeout_s: int = 12

    # Outputs
    output_dir: Path = Path("data")

    # Telemetry
    telemetry_enabled: bool = True

    # Misc
    seed: Optional[int] = 42

    def make_run_dir(self) -> Path:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        run_dir = self.output_dir / f"longevity_plan_{ts}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir


def load_config(
    turn_limit: Optional[int] = None,
    model: Optional[str] = None,
    valyu_url: Optional[str] = None,
    enable_valyu: Optional[bool] = None,
    user_profile: Optional[str | Path] = None,
    company_resource: Optional[str | Path] = None,
    output_dir: Optional[str | Path] = None,
    seed: Optional[int] = None,
) -> Config:
    """Create a Config object from args and environment.

    Loads .env if present to enable LangSmith or provider keys.
    """
    load_dotenv(override=False)

    cfg = Config()
    if turn_limit is not None:
        cfg.turn_limit = int(turn_limit)
    if model is not None:
        cfg.model = str(model)
    if valyu_url is not None:
        cfg.valyu_url = str(valyu_url)
    if enable_valyu is not None:
        cfg.enable_valyu = bool(enable_valyu)
    if user_profile is not None:
        cfg.user_profile_path = Path(user_profile)
    if company_resource is not None:
        cfg.company_resource_path = Path(company_resource)
    if output_dir is not None:
        cfg.output_dir = Path(output_dir)
    if seed is not None:
        cfg.seed = int(seed)

    # Ensure output dir exists
    cfg.output_dir.mkdir(parents=True, exist_ok=True)

    # If LangSmith vars exist, enable tracing; else leave as-is
    if not os.getenv("LANGSMITH_API_KEY"):
        os.environ.setdefault("LANGSMITH_TRACING", "false")

    return cfg
