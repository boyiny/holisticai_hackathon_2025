from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langsmith import Client

from eval.prompts import FinalPlanJudgeResponse, format_final_plan_prompt
from eval.utils import (
    DualAgentRunRecord,
    fetch_dual_agent_runs,
    get_langsmith_client,
    group_runs_by_scenario,
    load_user_profile_text,
)


@dataclass
class PlanPairEval:
    scenario_id: str
    reference_run_id: str
    comparison_run_id: str
    reference_outputs_dir: str
    comparison_outputs_dir: str
    similarity_score: float
    plan_a_quality: float
    plan_b_quality: float
    recommendation: str
    notes: str
    judge_model: str
    created_at: str


def _parse_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


def _evaluate_pair(
    llm: ChatOpenAI,
    user_context: str,
    reference: DualAgentRunRecord,
    comparison: DualAgentRunRecord,
) -> FinalPlanJudgeResponse:
    if not reference.final_plan_text or not comparison.final_plan_text:
        raise ValueError("Both runs must contain a serialized final plan.")
    prompt = format_final_plan_prompt(
        user_context=user_context,
        plan_a=reference.final_plan_text,
        plan_b=comparison.final_plan_text,
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    payload = _parse_json(str(content))
    return FinalPlanJudgeResponse.model_validate(payload)


def _record_feedback(client: Client, payload: PlanPairEval, dry_run: bool) -> None:
    if dry_run:
        return
    meta = {
        "scenario_id": payload.scenario_id,
        "reference_run_id": payload.reference_run_id,
        "reference_outputs_dir": payload.reference_outputs_dir,
        "comparison_run_id": payload.comparison_run_id,
        "comparison_outputs_dir": payload.comparison_outputs_dir,
        "judge_model": payload.judge_model,
        "notes": payload.notes,
    }
    client.create_feedback(
        run_id=payload.comparison_run_id,
        key="final_plan_consistency",
        score=payload.similarity_score / 10.0,
        value=meta | {"plan_role": "comparison"},
        comment=payload.notes,
    )
    client.create_feedback(
        run_id=payload.reference_run_id,
        key="final_plan_consistency_reference",
        score=payload.plan_a_quality / 10.0,
        value=meta | {"plan_role": "reference"},
        comment=payload.notes,
    )


def run_eval(args: argparse.Namespace) -> Dict[str, Any]:
    client = get_langsmith_client()
    runs = fetch_dual_agent_runs(
        client=client,
        project=args.project,
        limit=args.max_runs,
        since=args.since,
        run_name=args.run_name,
    )
    grouped = group_runs_by_scenario(runs, min_group_size=args.min_group_size)
    if not grouped:
        return {"pairs": [], "summary": {}, "note": "No comparable scenarios found."}
    user_context_text = args.user_context or load_user_profile_text(Path(args.user_profile))
    llm = ChatOpenAI(model=args.judge_model, temperature=0, timeout=120, max_tokens=800)
    pairs: List[PlanPairEval] = []
    for scenario_id, scenario_runs in grouped.items():
        reference = scenario_runs[0]
        for comparison in scenario_runs[1:]:
            result = _evaluate_pair(llm, user_context_text, reference, comparison)
            payload = PlanPairEval(
                scenario_id=scenario_id,
                reference_run_id=reference.run_id,
                comparison_run_id=comparison.run_id,
                reference_outputs_dir=str(reference.outputs_dir),
                comparison_outputs_dir=str(comparison.outputs_dir),
                similarity_score=result.similarity_score,
                plan_a_quality=result.plan_a_quality,
                plan_b_quality=result.plan_b_quality,
                recommendation=result.recommendation,
                notes=result.notes,
                judge_model=args.judge_model,
                created_at=datetime.utcnow().isoformat(),
            )
            pairs.append(payload)
            _record_feedback(client, payload, dry_run=args.dry_run)
    summary = {}
    if pairs:
        summary = {
            "avg_similarity": round(sum(p.similarity_score for p in pairs) / len(pairs), 3),
            "avg_plan_a_quality": round(sum(p.plan_a_quality for p in pairs) / len(pairs), 3),
            "avg_plan_b_quality": round(sum(p.plan_b_quality for p in pairs) / len(pairs), 3),
            "num_pairs": len(pairs),
            "project": args.project,
            "judge_model": args.judge_model,
        }
    return {
        "pairs": [asdict(p) for p in pairs],
        "summary": summary,
        "group_count": len(grouped),
        "min_group_size": args.min_group_size,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LangSmith-based final plan consistency eval.")
    parser.add_argument("--project", type=str, default=None, help="LangSmith project name.")
    parser.add_argument("--run-name", type=str, default="Dual Agents Longevity Conversation")
    parser.add_argument("--max-runs", type=int, default=40)
    parser.add_argument("--min-group-size", type=int, default=2)
    parser.add_argument("--since", type=str, default=None, help="ISO timestamp filter for runs.")
    parser.add_argument("--judge-model", type=str, default="gpt-4o-mini")
    parser.add_argument("--user-profile", type=str, default="user_info.json")
    parser.add_argument("--user-context", type=str, default=None, help="Override user context text.")
    parser.add_argument("--output-dir", type=str, default="data/evals")
    parser.add_argument("--dry-run", action="store_true", help="Skip feedback logging.")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    result = run_eval(args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"final_plan_eval_{ts}.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps({"summary": result.get("summary", {}), "output": str(out_path)}, indent=2))


if __name__ == "__main__":
    main()

