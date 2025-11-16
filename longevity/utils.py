from __future__ import annotations

import time
from typing import List, Tuple, Dict, Any, Optional

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from core.react_agent.utils import load_chat_model


def call_llm(
    model_name: str,
    system_prompt: str,
    conversation: List[Tuple[str, str]],
    temperature: float = 0.2,
) -> Tuple[str, Dict[str, Any]]:
    """Call an LLM with a system prompt and a sequence of (role, text) messages.

    Returns tuple(response_text, telemetry).
    """
    llm = load_chat_model(model_name)
    llm = llm.bind(temperature=temperature, stream=False)

    msgs: List[Any] = [SystemMessage(content=system_prompt)]
    for role, text in conversation:
        if role.lower() in {"user", "human", "advocate"}:
            msgs.append(HumanMessage(content=text))
        else:
            msgs.append(AIMessage(content=text))

    t0 = time.perf_counter()
    out = llm.invoke(msgs)
    dt = time.perf_counter() - t0

    content = out.content if isinstance(out, AIMessage) else getattr(out, "content", str(out))
    telemetry = {
        "latency_s": dt,
        "provider": model_name,
        # token usage not universally available across providers in this code path
    }
    return content, telemetry


class MockLLM:
    """Deterministic mock for tests and offline development."""

    def __init__(self, role_name: str):
        self.role_name = role_name

    def invoke(self, prompt: str) -> str:
        # Echo strategy based on last sentence for predictability
        base = prompt.strip().split("\n")[-1]
        return f"[{self.role_name}] Ack: {base[:120]} ..."


def ensure_provider_ready(model_name: str) -> None:
    """Fail fast with a clear message if provider credentials are missing/placeholder.

    - If model looks like OpenAI (gpt-/o3/o4), require OPENAI_API_KEY and not placeholder.
    - If model looks like Bedrock (us./mistral./claude/llama/nova), require Holistic AI creds.
    """
    import os

    def _is_placeholder(val: str) -> bool:
        v = val.strip().lower()
        return (v.startswith("sk-your") or v.endswith("here") or "your-" in v)

    openai_like = model_name.startswith(("gpt-", "o3", "o4"))
    bedrock_like = (
        model_name.startswith(("us.", "mistral."))
        or any(x in model_name.lower() for x in ("claude", "llama", "nova"))
    )

    if openai_like:
        key = os.getenv("OPENAI_API_KEY", "")
        if not key or _is_placeholder(key):
            raise RuntimeError(
                "OPENAI_API_KEY missing or placeholder. Set a real key in your environment or .env before using OpenAI models."
            )
    elif bedrock_like:
        tid = os.getenv("HOLISTIC_AI_TEAM_ID", "")
        tok = os.getenv("HOLISTIC_AI_API_TOKEN", "")
        if not (tid and tok):
            raise RuntimeError(
                "Holistic AI Bedrock credentials missing. Set HOLISTIC_AI_TEAM_ID and HOLISTIC_AI_API_TOKEN or choose an OpenAI model."
            )
