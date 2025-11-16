from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from longevity.chaos_testing import run_chaos_benchmark


def _set_env(args: argparse.Namespace) -> None:
    os.environ["CHAOS_MODE"] = "1"
    os.environ["CHAOS_JITTER_MIN_MS"] = str(args.jitter_min)
    os.environ["CHAOS_JITTER_MAX_MS"] = str(args.jitter_max)
    os.environ["CHAOS_NET_FAIL_PROB"] = str(args.net_fail_prob)
    os.environ["CHAOS_TOOL_FAIL_PROB"] = str(args.tool_fail_prob)
    os.environ["CHAOS_LLM_BAD_OUTPUT_PROB"] = "0.0"


def main() -> None:
    parser = argparse.ArgumentParser(description="Chaos test: Scheduler tool failures")
    parser.add_argument("--num-runs", type=int, default=10)
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--turn-limit", type=int, default=6)
    parser.add_argument("--model", type=str, default="gpt-4o-mini")
    parser.add_argument("--small-model", type=str, default=None)
    parser.add_argument("--valyu-url", type=str, default="http://localhost:3000/validate")
    parser.add_argument("--user-profile", type=str, default="user_info.json")
    parser.add_argument("--company-resource", type=str, default="company_resource.txt")
    parser.add_argument("--output-dir", type=str, default="data")
    parser.add_argument("--jitter-min", type=int, default=0)
    parser.add_argument("--jitter-max", type=int, default=200)
    parser.add_argument("--net-fail-prob", type=float, default=0.0)
    parser.add_argument("--tool-fail-prob", type=float, default=0.5)
    args = parser.parse_args()

    _set_env(args)

    summary = run_chaos_benchmark(
        scenario="scheduler_failures",
        num_runs=args.num_runs,
        concurrency=args.concurrency,
        turn_limit=args.turn_limit,
        model=args.model,
        small_model=args.small_model,
        valyu_url=args.valyu_url,
        user_profile=args.user_profile,
        company_resource=args.company_resource,
        output_dir=args.output_dir,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

