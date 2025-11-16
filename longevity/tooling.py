from __future__ import annotations

import random
import time
from threading import BoundedSemaphore
from typing import Iterable, List

from .schemas import Claim, ClaimValidation
from .valyu_validation import validate_claims as _validate_claims


# Global semaphore for external tool calls (HTTP, shared I/O)
_DEFAULT_LIMIT = 5
_tool_sem = BoundedSemaphore(_DEFAULT_LIMIT)


def set_tool_concurrency_limit(n: int) -> None:
    global _tool_sem
    _tool_sem = BoundedSemaphore(max(1, int(n)))


def concurrency_limited_validate_claims(
    claims: Iterable[Claim],
    url: str,
    timeout_s: int = 12,
    batch: bool = True,
    max_retries: int = 2,
) -> List[ClaimValidation]:
    """Wrap validate_claims with a concurrency limit and gentle backoff.

    Avoids hammering external validation service under load.
    """
    backoff_base = 0.25
    for attempt in range(max_retries + 1):
        acquired = _tool_sem.acquire(timeout=timeout_s)
        if not acquired:
            # Could not acquire within timeout -> brief backoff and retry
            time.sleep(backoff_base * (attempt + 1))
            continue
        try:
            # Delegate to underlying validator (already has its own retries)
            return _validate_claims(list(claims), url=url, timeout_s=timeout_s, batch=batch, max_retries=max_retries)
        finally:
            _tool_sem.release()
        # If somehow we reached here, sleep with jitter and retry
        time.sleep((2 ** attempt) * backoff_base + random.uniform(0, 0.2))
    # Final fallback – return unknowns via underlying call without concurrency (best effort)
    return _validate_claims(list(claims), url=url, timeout_s=timeout_s, batch=batch, max_retries=0)

