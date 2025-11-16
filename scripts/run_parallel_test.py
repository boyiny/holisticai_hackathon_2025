from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure repo root is on sys.path when running as a script
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
import concurrent.futures as cf
import hashlib
import json
import statistics
import time
from typing import Any, Dict, List

from longevity.longevity_conversation import run_longevity_conversation


def _plan_hash(plan: Dict[str, Any]) -> str:
    try:
        data = json.dumps(plan, sort_keys=True).encode("utf-8")
    except Exception:
        data = str(plan).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _pctl(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = max(0, min(len(s) - 1, int(round((p / 100.0) * (len(s) - 1)))))
    return float(s[k])


def run_parallel(
    concurrency: int,
    num_runs: int,
    mode: str,
    scenario: str,
    turn_limit: int,
    model: str,
    valyu_url: str,
    enable_valyu: bool,
    output_dir: Path,
    use_mock: bool,
    small_model: str | None,
    big_model: str | None,
) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []

    def _one(i: int) -> Dict[str, Any]:
        try:
            return run_longevity_conversation(
                turn_limit=turn_limit,
                model=model,
                valyu_url=valyu_url,
                enable_valyu=enable_valyu,
                user_profile="user_info.json",
                company_resource="company_resource.txt",
                output_dir=str(output_dir),
                mode=mode,
                scenario_id=f"{scenario}-{i}",
                use_mock=use_mock,
                small_model=small_model,
                big_model=big_model,
            )
        except Exception as e:
            return {
                "run_id": f"error_{i}",
                "scenario_id": scenario,
                "success": False,
                "num_turns": 0,
                "plan_struct": {},
                "tokens_total": 0,
                "latency_ms": 0,
                "errors": [repr(e)],
                "mode": mode,
            }

    t0 = time.perf_counter()
    with cf.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futs = [ex.submit(_one, i) for i in range(num_runs)]
        for f in cf.as_completed(futs):
            results.append(f.result())
    dt = time.perf_counter() - t0

    # Metrics
    success_bools = [bool(r.get("success", False)) for r in results]
    success_rate = sum(1 for s in success_bools if s) / max(1, len(success_bools))
    latencies = [float(r.get("latency_ms", 0)) for r in results if r.get("latency_ms") is not None]
    p50 = _pctl(latencies, 50)
    p95 = _pctl(latencies, 95)
    tokens = [int(r.get("tokens_total", 0)) for r in results]
    avg_tokens = statistics.mean(tokens) if tokens else 0.0
    stdev_tokens = statistics.pstdev(tokens) if tokens else 0.0

    # Plan consistency via hash
    hashes: List[str] = []
    for r in results:
        plan = r.get("plan_struct", {})
        hashes.append(_plan_hash(plan))
    majority = None
    if hashes:
        majority = max(set(hashes), key=hashes.count)
    determinism = sum(1 for h in hashes if h == majority) / max(1, len(hashes))

    errors: List[str] = []
    for r in results:
        errors.extend(r.get("errors", []))

    summary = {
        "mode": mode,
        "num_runs": num_runs,
        "concurrency": concurrency,
        "elapsed_s": round(dt, 3),
        "success_rate": round(success_rate, 3),
        "p50_latency_ms": int(p50),
        "p95_latency_ms": int(p95),
        "avg_tokens_per_run": round(float(avg_tokens), 2),
        "tokens_stddev": round(float(stdev_tokens), 2),
        "plan_consistency": round(float(determinism), 3),
        "errors_sample": errors[:10],
    }

    # Persist report
    out_dir = Path(output_dir) / "tests"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"parallel_test_{mode}_{ts}.json"
    out = {
        "summary": summary,
        "runs": results,
    }
    out_path.write_text(json.dumps(out, indent=2))
    return summary


def main() -> None:
    p = argparse.ArgumentParser(description="Parallel load test for longevity conversation")
    p.add_argument("--concurrency", type=int, default=10)
    p.add_argument("--num-runs", type=int, default=20)
    p.add_argument("--mode", type=str, choices=["baseline", "optimized"], default="baseline")
    p.add_argument("--scenario", type=str, default="default")
    p.add_argument("--turn-limit", type=int, default=10)
    p.add_argument("--model", type=str, default="gpt-4o-mini")
    p.add_argument("--valyu-url", type=str, default="http://localhost:3000/validate")
    p.add_argument("--enable-valyu", action="store_true")
    p.add_argument("--output-dir", type=str, default="data")
    p.add_argument("--use-mock", action="store_true", help="Use MockLLM to avoid external providers")
    p.add_argument("--small-model", type=str, default=None)
    p.add_argument("--big-model", type=str, default=None)
    args = p.parse_args()

    summary = run_parallel(
        concurrency=args.concurrency,
        num_runs=args.num_runs,
        mode=args.mode,
        scenario=args.scenario,
        turn_limit=args.turn_limit,
        model=args.model,
        valyu_url=args.valyu_url,
        enable_valyu=args.enable_valyu,
        output_dir=Path(args.output_dir),
        use_mock=bool(args.use_mock),
        small_model=args.small_model,
        big_model=args.big_model,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
