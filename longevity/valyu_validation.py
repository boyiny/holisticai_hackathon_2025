from __future__ import annotations

import re
import time
from typing import Iterable, List

import requests

from .schemas import Claim, ClaimValidation


SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def extract_claims(text: str, turn_index: int, speaker: str) -> List[Claim]:
    """Extract likely scientific claims using lightweight heuristics.

    Heuristics:
    - Sentences > 40 chars
    - Contain action-outcome patterns (reduces, improves, increases, lowers, risk, mortality, biomarker)
    - Or claim markers (studies show, clinical trial, proven)
    Returns Claim objects with neighbor context when available.
    """
    sentences = re.split(SENTENCE_SPLIT, text.strip()) if text.strip() else []
    claims: List[Claim] = []
    keywords = [
        r"reduces", r"improves", r"increases", r"lowers", r"risk", r"mortality",
        r"biomarker", r"studies?\s+show", r"clinical\s+trial", r"proven",
    ]
    pat = re.compile("|".join(keywords), re.IGNORECASE)
    for i, s in enumerate(sentences):
        s_norm = s.strip()
        if len(s_norm) < 40:
            continue
        if not pat.search(s_norm):
            continue
        before = sentences[i - 1].strip() if i - 1 >= 0 else None
        after = sentences[i + 1].strip() if i + 1 < len(sentences) else None
        claims.append(Claim(text=s_norm, turn_index=turn_index, speaker=speaker, context_before=before, context_after=after))
    return claims


def validate_claims(
    claims: Iterable[Claim],
    url: str,
    timeout_s: int = 12,
    batch: bool = True,
    max_retries: int = 2,
) -> List[ClaimValidation]:
    """Validate claims against Valyu-like endpoint.

    Expects endpoint to accept either:
    - POST { claims: [{text, context}], mode: "batch" }
      and return list of {validity, confidence, evidence}
    - or for single: POST { claim, context }
    Robust to server errors; falls back to unknown.
    """
    cl = list(claims)
    results: List[ClaimValidation] = []
    if not cl:
        return results

    def _unknown(c: Claim, server_unavailable: bool = False) -> ClaimValidation:
        return ClaimValidation(
            claim=c, validity="unknown", confidence=0.0, evidence=None, server_unavailable=server_unavailable, raw_response=None
        )

    try:
        if batch:
            payload = {
                "mode": "batch",
                "claims": [
                    {
                        "text": c.text,
                        "context": (c.context_before or "") + "\n" + (c.context_after or ""),
                        "turn_index": c.turn_index,
                        "speaker": c.speaker,
                    }
                    for c in cl
                ],
            }
            resp = _post_with_retries(url, payload, timeout_s, max_retries)
            if not resp or resp.status_code >= 400:
                return [_unknown(c, server_unavailable=True) for c in cl]
            data = resp.json()
            items = data if isinstance(data, list) else data.get("results", [])
            for c, item in zip(cl, items):
                validity = str(item.get("validity", "unknown")).lower()
                confidence = float(item.get("confidence", 0.0))
                evidence = item.get("evidence")
                results.append(
                    ClaimValidation(claim=c, validity=validity if validity in {"true", "false", "unknown"} else "unknown", confidence=confidence, evidence=evidence, raw_response=item)
                )
            # Handle length mismatch gracefully
            while len(results) < len(cl):
                results.append(_unknown(cl[len(results)], server_unavailable=False))
            return results
        else:
            for c in cl:
                payload = {
                    "claim": c.text,
                    "context": (c.context_before or "") + "\n" + (c.context_after or ""),
                }
                resp = _post_with_retries(url, payload, timeout_s, max_retries)
                if not resp or resp.status_code >= 400:
                    results.append(_unknown(c, server_unavailable=True))
                    continue
                item = resp.json()
                validity = str(item.get("validity", "unknown")).lower()
                confidence = float(item.get("confidence", 0.0))
                evidence = item.get("evidence")
                results.append(
                    ClaimValidation(claim=c, validity=validity if validity in {"true", "false", "unknown"} else "unknown", confidence=confidence, evidence=evidence, raw_response=item)
                )
            return results
    except Exception:
        # Total failure -> unknowns
        return [_unknown(c, server_unavailable=True) for c in cl]


def _post_with_retries(url: str, json_payload: dict, timeout_s: int, max_retries: int) -> requests.Response | None:
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            return requests.post(url, json=json_payload, timeout=timeout_s)
        except Exception as e:
            last_exc = e
            time.sleep(0.5 * (attempt + 1))
    return None

