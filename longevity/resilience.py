from __future__ import annotations

import random
import time
from typing import Any, Callable, Dict, Tuple

from .chaos_layer import (
    apply_network_chaos,
    apply_tool_chaos,
    ChaosNetworkError,
    ChaosToolError,
)


MAX_RETRIES = 3


def resilient_llm_call(call_fn: Callable[..., Any], *args, **kwargs) -> Tuple[Any, Dict]:
    """Wrap low-level LLM call with jitter, retries, and graceful failure.

    Returns (result, meta) where meta contains retry_count, last_error, etc.
    """
    retries = 0
    last_error = None

    while retries <= MAX_RETRIES:
        try:
            apply_network_chaos()
            result = call_fn(*args, **kwargs)
            return result, {"retries": retries, "last_error": last_error}
        except ChaosNetworkError as e:
            last_error = str(e)
            if retries == MAX_RETRIES:
                return None, {"retries": retries, "last_error": last_error, "hard_failure": True}
            delay = (2 ** retries) + random.uniform(0, 0.5)
            time.sleep(delay)
            retries += 1


def resilient_tool_call(call_fn: Callable[..., Any], *args, **kwargs) -> Tuple[Any, Dict]:
    """Wrap calls to external tools (Valyu, scheduler) with chaos + retries."""
    retries = 0
    last_error = None

    while retries <= MAX_RETRIES:
        try:
            apply_tool_chaos()
            apply_network_chaos()
            result = call_fn(*args, **kwargs)
            return result, {"retries": retries, "last_error": last_error}
        except (ChaosNetworkError, ChaosToolError, Exception) as e:
            last_error = str(e)
            if retries == MAX_RETRIES:
                return None, {"retries": retries, "last_error": last_error, "hard_failure": True}
            delay = (2 ** retries) + random.uniform(0, 0.5)
            time.sleep(delay)
            retries += 1

