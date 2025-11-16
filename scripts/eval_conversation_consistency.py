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

from eval.prompts import ConversationJudgeResponse, format_conversation_prompt
from eval.utils import (
    DualAgentRunRecord,
    fetch_dual_agent_runs,
    get_langsmith_client,
    group_runs_by_scenario,
    load_user_profile_text,
)


@dataclass
class ConversationPairEval:
    scenario_id: str
    reference_run_id: str
    comparison_run_id: str
    reference_outputs_dir: str
    comparison_outputs_dir: str
    collaboration_similarity: float
    alignment_a: float
    alignment_b: float
    reasoning_depth: float
    consistency_score: float
    recommendation: str
    notes: str
    judge_model: str
    summary_model: Optional[str]
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


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n[conversation truncated]"


def _summarize_transcript(
    llm: Optional[ChatOpenAI],
    user_context: str,
    transcript: str,
    plan_text: str,
) -> Optional[str]:
    if not llm:
        return None
    prompt = (
        "Summarize the following dual-agent conversation for evaluators.\n"
        "Highlight major decisions, disagreements, and key plan elements.\n"
        "Limit to 6 bullet points.\n\n"
        f"User context:\n{user_context}\n\nConversation:\n{transcript}\n\nPlan:\n{plan_text}"
    )
    msg = llm.invoke([HumanMessage(content=prompt)])
    content = msg.content
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content).strip()


def _evaluate_pair(
    llm: ChatOpenAI,
    user_context: str,
    reference: DualAgentRunRecord,
    comparison: DualAgentRunRecord,
    transcript_chars: int,
    summary_map: Dict[str, Optional[str]],
) -> ConversationJudgeResponse:
    if not reference.transcript_text or not comparison.transcript_text:
        raise ValueError("Both runs must provide transcripts.")
    if not reference.final_plan_text or not comparison.final_plan_text:
        raise ValueError("Both runs must include final plans.")
    transcript_a = _truncate(reference.transcript_text, transcript_chars)
    transcript_b = _truncate(comparison.transcript_text, transcript_chars)
    summary_a = summary_map.get(reference.run_id)
    summary_b = summary_map.get(comparison.run_id)
    prompt = format_conversation_prompt(
        user_context=user_context,
        transcript_a=transcript_a,
        plan_a=reference.final_plan_text,
        transcript_b=transcript_b,
        plan_b=comparison.final_plan_text,
        summary_a=summary_a,
        summary_b=summary_b,
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content
    if isinstance(content, list):
        content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
    payload = _parse_json(str(content))
    return ConversationJudgeResponse.model_validate(payload)


def _record_feedback(client: Client, payload: ConversationPairEval, dry_run: bool) -> None:
    if dry_run:
        return
    meta = {
        "scenario_id": payload.scenario_id,
        "reference_run_id": payload.reference_run_id,
        "comparison_run_id": payload.comparison_run_id,
        "judge_model": payload.judge_model,
        "summary_model": payload.summary_model,
        "notes": payload.notes,
    }
    client.create_feedback(
        run_id=payload.comparison_run_id,
        key="conversation_consistency",
        score=payload.consistency_score / 10.0,
        value=meta | {"plan_role": "comparison"},
        comment=payload.notes,
    )
    client.create_feedback(
        run_id=payload.reference_run_id,
        key="conversation_consistency_reference",
        score=payload.alignment_a / 10.0,
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
    judge_llm = ChatOpenAI(model=args.judge_model, temperature=0, timeout=120, max_tokens=900)
    summary_llm = None
    if args.summary_model:
        summary_llm = ChatOpenAI(model=args.summary_model, temperature=0, timeout=60, max_tokens=400)
    summaries: Dict[str, Optional[str]] = {}
    pairs: List[ConversationPairEval] = []
    for scenario_id, scenario_runs in grouped.items():
        for run in scenario_runs:
            if run.run_id in summaries:
                continue
            if not run.transcript_text or not run.final_plan_text:
                summaries[run.run_id] = None
                continue
            summaries[run.run_id] = _summarize_transcript(
                summary_llm,
                user_context_text,
                _truncate(run.transcript_text, args.transcript_chars),
                run.final_plan_text,
            )
        reference = scenario_runs[0]
        for comparison in scenario_runs[1:]:
            result = _evaluate_pair(
                llm=judge_llm,
                user_context=user_context_text,
                reference=reference,
                comparison=comparison,
                transcript_chars=args.transcript_chars,
                summary_map=summaries,
            )
            payload = ConversationPairEval(
                scenario_id=scenario_id,
                reference_run_id=reference.run_id,
                comparison_run_id=comparison.run_id,
                reference_outputs_dir=str(reference.outputs_dir),
                comparison_outputs_dir=str(comparison.outputs_dir),
                collaboration_similarity=result.collaboration_similarity,
                alignment_a=result.alignment_a,
                alignment_b=result.alignment_b,
                reasoning_depth=result.reasoning_depth,
                consistency_score=result.consistency_score,
                recommendation=result.recommendation,
                notes=result.notes,
                judge_model=args.judge_model,
                summary_model=args.summary_model,
                created_at=datetime.utcnow().isoformat(),
            )
            pairs.append(payload)
            _record_feedback(client, payload, dry_run=args.dry_run)
    summary = {}
    if pairs:
        summary = {
            "avg_collaboration": round(sum(p.collaboration_similarity for p in pairs) / len(pairs), 3),
            "avg_alignment_a": round(sum(p.alignment_a for p in pairs) / len(pairs), 3),
            "avg_alignment_b": round(sum(p.alignment_b for p in pairs) / len(pairs), 3),
            "avg_reasoning_depth": round(sum(p.reasoning_depth for p in pairs) / len(pairs), 3),
            "avg_consistency": round(sum(p.consistency_score for p in pairs) / len(pairs), 3),
            "num_pairs": len(pairs),
            "project": args.project,
            "judge_model": args.judge_model,
            "summary_model": args.summary_model,
        }
    return {
        "pairs": [asdict(p) for p in pairs],
        "summary": summary,
        "group_count": len(grouped),
        "min_group_size": args.min_group_size,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Conversation-level consistency eval.")
    parser.add_argument("--project", type=str, default=None, help="LangSmith project name.")
    parser.add_argument("--run-name", type=str, default="Dual Agents Longevity Conversation")
    parser.add_argument("--max-runs", type=int, default=30)
    parser.add_argument("--min-group-size", type=int, default=2)
    parser.add_argument("--since", type=str, default=None)
    parser.add_argument("--transcript-chars", type=int, default=6000, help="Max characters from each transcript.")
    parser.add_argument("--judge-model", type=str, default="gpt-4o-mini")
    parser.add_argument("--summary-model", type=str, default=None, help="Optional smaller model for transcript summaries.")
    parser.add_argument("--user-profile", type=str, default="user_info.json")
    parser.add_argument("--user-context", type=str, default=None)
    parser.add_argument("--output-dir", type=str, default="data/evals")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    result = run_eval(args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"conversation_eval_{ts}.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps({"summary": result.get("summary", {}), "output": str(out_path)}, indent=2))


if __name__ == "__main__":
    main()

