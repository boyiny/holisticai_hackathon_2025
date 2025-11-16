from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from .config import load_config
from .longevity_agents import build_agent_profiles, load_user_profile, load_company_resource, ADVOCATE_NAME, PLANNER_NAME, seed_message_for_advocate
from .memory import SharedMemory
from .save_conversation import append_text, save_json
from .tools_langchain import ValidateClaimsTool, ScheduleTool, set_tool_caller
from .plan_schema import FinalPlan
from .utils import ensure_provider_ready
from core.react_agent import create_react_agent


PHASES = [
    ("Start", ADVOCATE_NAME),
    ("Intake", ADVOCATE_NAME),
    ("PlanDraft", PLANNER_NAME),
    ("PlanReview", ADVOCATE_NAME),
    ("Audit", PLANNER_NAME),
    ("Revision", ADVOCATE_NAME),
    ("FinalPlan", PLANNER_NAME),
    ("Scheduling", PLANNER_NAME),
    ("FinalSummary", ADVOCATE_NAME),
]


def run_dual_agents(
    turn_limit: int = 10,
    model: str = "gpt-4o-mini",
    valyu_url: str = "http://localhost:3000/validate",
    user_profile: str | Path = "user_info.json",
    company_resource: str | Path = "company_resource.txt",
    output_dir: str | Path = "data",
    use_mock: bool = False,
) -> Dict[str, Any]:
    """Run two separate agents (LEO = Advocate, LUNA = Planner) sending messages back and forth per phases.

    Returns a dict with paths and the FinalPlan JSON (if produced).
    """
    load_dotenv()
    cfg = load_config(
        turn_limit=turn_limit,
        model=model,
        valyu_url=valyu_url,
        enable_valyu=True,
        user_profile=user_profile,
        company_resource=company_resource,
        output_dir=output_dir,
    )

    ensure_provider_ready(cfg.model)

    user = load_user_profile(cfg.user_profile_path)
    company = load_company_resource(cfg.company_resource_path)
    profiles = build_agent_profiles(user, company)

    run_dir = cfg.make_run_dir()
    transcript_path = run_dir / "conversation_history.txt"
    telemetry_path = run_dir / "telemetry.json"
    final_plan_path = run_dir / "final_plan.json"

    memory = SharedMemory()
    memory.add_fact("user_name", user.get("name", "User"))
    memory.add_fact("goals", user.get("goals", []))

    telemetry: List[dict] = []
    tools = [ValidateClaimsTool(default_url=cfg.valyu_url, telemetry=telemetry), ScheduleTool(telemetry=telemetry)]

    # Create two distinct agents with their own system prompts
    leo_agent = create_react_agent(
        tools=tools,
        model_name=cfg.model,
        system_prompt=(profiles.advocate_system + "\n\nYou are LEO (user-facing). Collaborate with LUNA. Keep non-medical."),
    )
    luna_agent = create_react_agent(
        tools=tools,
        model_name=cfg.model,
        system_prompt=(profiles.planner_system + "\n\nYou are LUNA (backend). Audit, schedule, validate. Keep non-medical."),
    )

    transcript: List[Tuple[str, str]] = []
    telemetry: List[dict] = []

    # Seed message from LEO
    seed = seed_message_for_advocate(user)
    transcript.append(("advocate", seed))
    append_text(transcript_path, [f"{ADVOCATE_NAME}: {seed}\n"]) 

    final_plan_obj: Optional[dict] = None

    # Iterate phases; within each, have the responsible agent act once
    for idx, (phase, speaker) in enumerate(PHASES):
        if idx >= cfg.turn_limit:
            break
        hint = ("human", f"[phase] {phase} | [shared_memory] {memory.render_brief()}")
        messages = [HumanMessage(content=transcript[-1][1])] if transcript else []
        messages.append(HumanMessage(content=hint[1]))

        t0 = time.perf_counter()
        # Tag the tool caller so telemetry knows which agent triggered the tool call
        set_tool_caller(speaker)
        if speaker == ADVOCATE_NAME:
            result = leo_agent.invoke({"messages": messages})
        else:
            result = luna_agent.invoke({"messages": messages})
        dt = time.perf_counter() - t0
        set_tool_caller(None)

        last = result["messages"][-1]
        content = getattr(last, "content", "")
        telemetry.append({"phase": phase, "speaker": speaker, "latency_s": dt})

        # Record to transcript
        role = "assistant" if speaker == PLANNER_NAME else "human"
        transcript.append((role, content))
        append_text(transcript_path, [f"{speaker}: {content}\n"]) 

        # If this is FinalPlan or FinalSummary, try to capture structured output as FinalPlan
        if phase in {"FinalPlan", "FinalSummary"}:
            # Try structured_output attachment; otherwise parse JSON, otherwise None
            try:
                final_obj = getattr(last, "additional_kwargs", {}).get("structured_output")
                if not final_obj:
                    final_obj = json.loads(content)
                # Validate via Pydantic
                final_plan = FinalPlan.model_validate(final_obj)
                final_plan_obj = final_plan.model_dump()
                break
            except Exception:
                pass

    # Persist outputs
    if final_plan_obj:
        save_json(final_plan_path, final_plan_obj)
    save_json(telemetry_path, telemetry)

    return {
        "outputs_dir": str(run_dir),
        "transcript": str(transcript_path),
        "telemetry": str(telemetry_path),
        "final_plan": str(final_plan_path) if final_plan_obj else None,
    }
