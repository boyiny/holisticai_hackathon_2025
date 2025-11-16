from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure repo root is on sys.path when running from scripts/
sys.path.append(str(Path(__file__).resolve().parents[1]))

from longevity.dual_agents import run_dual_agents


def main():
    parser = argparse.ArgumentParser(description="Run LEO and LUNA as separate agents exchanging messages to produce a final plan")
    parser.add_argument("--turn-limit", type=int, default=9)
    parser.add_argument("--model", type=str, default="gpt-4o-mini")
    parser.add_argument("--valyu-url", type=str, default="http://localhost:3000/validate")
    parser.add_argument("--user-profile", type=str, default="user_info.json")
    parser.add_argument("--company-resource", type=str, default="company_resource.txt")
    parser.add_argument("--output-dir", type=str, default="data")
    parser.add_argument("--small-model", type=str, default=None, help="Optional faster model for low-stakes phases")
    args = parser.parse_args()

    res = run_dual_agents(
        turn_limit=args.turn_limit,
        model=args.model,
        valyu_url=args.valyu_url,
        user_profile=args.user_profile,
        company_resource=args.company_resource,
        output_dir=args.output_dir,
        small_model=args.small_model,
    )
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
