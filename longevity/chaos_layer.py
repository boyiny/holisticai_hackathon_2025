from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass, asdict
from typing import Any


class ChaosNetworkError(Exception):
    """Simulated network failure (timeouts, dropped connections, etc.)."""


class ChaosToolError(Exception):
    """Simulated tool-level failure (HTTP 500, malformed response, etc.)."""


@dataclass
class ChaosConfig:
    enabled: bool = False
    jitter_min_ms: int = 200
    jitter_max_ms: int = 1000
    network_fail_prob: float = 0.0
    tool_fail_prob: float = 0.0
    llm_bad_output_prob: float = 0.0

    @classmethod
    def from_env(cls) -> "ChaosConfig":
        return cls(
            enabled=os.getenv("CHAOS_MODE", "0") == "1",
            jitter_min_ms=int(os.getenv("CHAOS_JITTER_MIN_MS", "200")),
            jitter_max_ms=int(os.getenv("CHAOS_JITTER_MAX_MS", "1000")),
            network_fail_prob=float(os.getenv("CHAOS_NET_FAIL_PROB", "0.0")),
            tool_fail_prob=float(os.getenv("CHAOS_TOOL_FAIL_PROB", "0.0")),
            llm_bad_output_prob=float(os.getenv("CHAOS_LLM_BAD_OUTPUT_PROB", "0.0")),
        )


CHAOS_CONFIG = ChaosConfig.from_env()


def refresh_config() -> None:
    """Re-read environment variables. Useful for scripts that change them at runtime."""
    global CHAOS_CONFIG
    CHAOS_CONFIG = ChaosConfig.from_env()


def current_config_dict() -> dict[str, Any]:
    """Return the active chaos config for embedding in reports."""
    return asdict(CHAOS_CONFIG)


def apply_network_chaos() -> None:
    if not CHAOS_CONFIG.enabled:
        return
    if CHAOS_CONFIG.jitter_max_ms > 0:
        delay_ms = random.randint(CHAOS_CONFIG.jitter_min_ms, CHAOS_CONFIG.jitter_max_ms)
        time.sleep(delay_ms / 1000.0)
    if random.random() < CHAOS_CONFIG.network_fail_prob:
        raise ChaosNetworkError("Simulated network failure from chaos layer")


def apply_tool_chaos() -> None:
    if not CHAOS_CONFIG.enabled:
        return
    if random.random() < CHAOS_CONFIG.tool_fail_prob:
        raise ChaosToolError("Simulated tool failure from chaos layer")


def maybe_corrupt_llm_output(text: Any) -> Any:
    """Return malformed/empty output according to chaos settings."""
    if not CHAOS_CONFIG.enabled:
        return text
    if CHAOS_CONFIG.llm_bad_output_prob <= 0.0:
        return text
    if not isinstance(text, str):
        return text
    if random.random() >= CHAOS_CONFIG.llm_bad_output_prob:
        return text
    choice = random.choice(["empty", "garbage", "truncated"])
    if choice == "empty":
        return ""
    if choice == "garbage":
        return "{ not: valid json"
    # truncated
    half = max(1, len(text) // 2)
    return text[:half]

