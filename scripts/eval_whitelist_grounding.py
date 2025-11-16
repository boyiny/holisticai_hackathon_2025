from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from langsmith import Client
from langsmith.run_trees import RunTree

from eval.whitelist_grounding_eval import (
    QueryEvalResult,
    _canonical_domain,
    _extract_urls,
    _load_lines_file,
    judge_answer_sources,
    judge_whitelist_compliance,
    run_whitelisted_search,
)
from eval.utils import get_langsmith_client


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="LangSmith-wired whitelisted grounding eval (Valyu)")

    # Inputs
    p.add_argument("--query", help="Single query to run")
    p.add_argument("--queries-file", help="Path to file with one query per line")

    # Sources
    p.add_argument("--include-sources", nargs="*", default=[], help="Domains/URLs to whitelist")
    p.add_argument("--whitelist-file", help="File with whitelisted domains/URLs, one per line")
    p.add_argument("--country", help="2-letter ISO code (e.g., uk, us)")

    # Config
    p.add_argument("--k", type=int, default=10, help="Max docs to retrieve")
    p.add_argument("--fast", action="store_true", help="Enable Valyu fast mode")
    p.add_argument("--valyu-api-key", help="Valyu API key (overrides VALYU_API_KEY env)")

    # Optional answer judging
    p.add_argument("--answer-text", help="Answer text to judge for whitelist citation compliance")

    # LangSmith
    p.add_argument("--project", type=str, default="whitelist_grounding_eval", help="LangSmith project name")
    p.add_argument("--tags", nargs="*", default=["eval", "whitelist", "valyu"], help="Tags for LangSmith runs")
    p.add_argument("--dry-run", action="store_true", help="Compute locally but skip LangSmith posting")

    # Output
    p.add_argument("--output-dir", type=str, default="data/evals", help="Directory to save JSON report")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Load queries
    queries: List[str] = []
    if args.query:
        queries.append(args.query)
    if args.queries_file:
        queries.extend(_load_lines_file(args.queries_file))
    if not queries:
        parser.error("Provide --query or --queries-file")

    # Load whitelist
    whitelist: List[str] = []
    whitelist.extend(args.include_sources or [])
    whitelist.extend(_load_lines_file(args.whitelist_file))
    if not whitelist:
        parser.error("Provide --include-sources or --whitelist-file with allowed domains/URLs")
    canonical_wl = sorted({_canonical_domain(s) for s in whitelist})

    api_key = args.valyu_api_key or os.getenv("VALYU_API_KEY")
    if not api_key:
        print("⚠️  VALYU_API_KEY not set; requests may fail.", file=sys.stderr)

    # LangSmith client
    ls_client: Optional[Client] = None
    if not args.dry_run:
        ls_client = get_langsmith_client()

    # Collect results
    results: List[QueryEvalResult] = []
    for q in queries:
        # Construct a run tree per query
        root = RunTree(
            name="Whitelist Grounding Eval",
            run_type="chain",
            project_name=args.project,
            inputs={
                "query": q,
                "k": args.k,
                "country": (args.country.upper() if args.country else None),
                "fast_mode": bool(args.fast),
                "whitelist": canonical_wl,
            },
            tags=args.tags,
            metadata={"tool": "valyu"},
        )

        # Search child run
        search_child = RunTree(
            name="valyu_search",
            run_type="tool",
            inputs={
                "query": q,
                "k": args.k,
                "country": (args.country.upper() if args.country else None),
                "fast_mode": bool(args.fast),
                "included_sources": whitelist,
            },
            parent_run=root,
        )

        urls, domains = run_whitelisted_search(
            q,
            include_sources=whitelist,
            k=args.k,
            country=(args.country.upper() if args.country else None),
            fast_mode=bool(args.fast),
            valyu_api_key=api_key,
        )
        non_wl = judge_whitelist_compliance(domains, canonical_wl)
        search_child.end(outputs={"urls": urls, "domains": domains, "non_whitelisted": non_wl})

        rec = QueryEvalResult(
            query=q,
            include_sources=whitelist,
            canonical_whitelist=canonical_wl,
            retrieved_urls=urls,
            retrieved_domains=[d for d in domains if d],
            non_whitelisted_domains=non_wl,
        )

        if args.answer_text:
            cited, non_wl_ans = judge_answer_sources(args.answer_text, canonical_wl)
            rec.answer = args.answer_text
            rec.cited_urls_in_answer = cited
            rec.non_whitelisted_in_answer = non_wl_ans

        # Root outputs + basic pass/fail
        metrics: Dict[str, Any] = {
            "retrieval_compliant": len(rec.non_whitelisted_domains) == 0,
            "retrieval_non_wl_count": len(rec.non_whitelisted_domains),
        }
        if args.answer_text:
            metrics.update(
                {
                    "answer_compliant": len(rec.non_whitelisted_in_answer or []) == 0,
                    "answer_non_wl_count": len(rec.non_whitelisted_in_answer or []),
                }
            )
        root.end(outputs={"result": asdict(rec), "metrics": metrics})

        # Post to LangSmith
        root_run_id = None
        if ls_client:
            try:
                posted = root.post(ls_client)
                root_run_id = getattr(posted, "id", None) or getattr(posted, "run_id", None)
            except Exception as e:
                print(f"⚠️  Failed to post run to LangSmith: {e}", file=sys.stderr)

            # Optionally, record feedback for easy scoring in UI
            if root_run_id:
                try:
                    ls_client.create_feedback(
                        run_id=str(root_run_id),
                        key="whitelist_retrieval_compliance",
                        score=1.0 if metrics["retrieval_compliant"] else 0.0,
                        value={
                            "non_whitelisted": rec.non_whitelisted_domains,
                            "whitelist": rec.canonical_whitelist,
                            "query": rec.query,
                        },
                        comment="Retrieval domain compliance with whitelist",
                    )
                    if args.answer_text is not None:
                        ls_client.create_feedback(
                            run_id=str(root_run_id),
                            key="whitelist_answer_citation_compliance",
                            score=1.0 if metrics.get("answer_compliant") else 0.0,
                            value={
                                "non_whitelisted": rec.non_whitelisted_in_answer or [],
                                "cited_urls": rec.cited_urls_in_answer or [],
                                "whitelist": rec.canonical_whitelist,
                                "query": rec.query,
                            },
                            comment="Answer citation domain compliance with whitelist",
                        )
                except Exception as e:
                    print(f"⚠️  Failed to record feedback: {e}", file=sys.stderr)

        results.append(rec)

    # Save report
    output_dir = REPO_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = output_dir / f"whitelist_grounding_eval_{ts}.json"
    payload = {
        "created_at": ts,
        "project": args.project,
        "valyu_fast_mode": bool(args.fast),
        "k": args.k,
        "country": (args.country.upper() if args.country else None),
        "results": [asdict(r) for r in results],
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(out_path), "queries": len(results)}, indent=2))


if __name__ == "__main__":
    main()

