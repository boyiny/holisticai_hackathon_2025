from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

sys.path.append(str(Path(__file__).resolve().parents[1]))
from core.react_agent import create_react_agent
from longevity.tools_langchain import ValidateClaimsTool, ScheduleTool
from longevity.plan_schema import FinalPlan


def main():
    parser = argparse.ArgumentParser(description="Run planning agent with tool calls to produce a final plan (JSON)")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--user-name", default="Alice Nguyen")
    parser.add_argument("--focus", default="Sleep & Recovery")
    parser.add_argument("--valyu-url", default="http://localhost:3000/validate")
    parser.add_argument("--user-id", default="user-001")
    parser.add_argument("--output", default="data/final_plan.json")
    args = parser.parse_args()

    load_dotenv()

    tools = [
        ValidateClaimsTool(default_url=args.valyu_url),
        ScheduleTool(),
    ]

    sys_prompt = f"""
You are a longevity planning agent. Work in a strict, lifestyle-only scope (sleep, movement, nutrition, stress) and avoid medical advice.

Goal: Draft a 6-month plan for the user, then schedule relevant services and validate scientific-sounding recommendations.

Tool usage guidelines:
- Use validate_claims to check any scientific claims you propose.
- Use schedule_services to book appointments for baseline_bloodwork, vo2_test, scan, or lifestyle_coaching as appropriate.
- Include the scheduled appointments in the final output.

User: {args.user_name}
Focus area: {args.focus}
"""

    agent = create_react_agent(
        tools=tools,
        model_name=args.model,
        output_schema=FinalPlan,
        system_prompt=sys_prompt,
    )

    # One-shot instruction provides the structure; the agent may call tools then output as FinalPlan JSON
    task = (
        "Create a 6-month plan broken into items (month, category, action, rationale). "
        "If proposing lab/fitness appointments, schedule them via schedule_services(services=[...], user_id=...) and include these appointments in the final output. "
        "If citing evidence, call validate_claims(claims=[...]) and summarize the result in the evidence field of each item. "
        "Return only the final JSON object adhering strictly to the FinalPlan schema."
    )

    result = agent.invoke({"messages": [HumanMessage(content=task)]})
    # Try to extract structured output
    content = result["messages"][-1].content
    try:
        # If structured_output was attached (via our agent's formatting node), prefer that
        structured = getattr(result["messages"][-1], "additional_kwargs", {}).get("structured_output")
        final_obj = structured or json.loads(content)
    except Exception:
        final_obj = {"raw": content}

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(final_obj, indent=2))
    print(f"Saved plan → {out_path}")


if __name__ == "__main__":
    main()
