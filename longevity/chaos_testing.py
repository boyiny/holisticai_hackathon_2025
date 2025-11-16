from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional

from .chaos_layer import current_config_dict, refresh_config
from .dual_agents import run_dual_agents


def _percentile(values: List[int], pct: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    idx = int(round((pct / 100.0) * (len(ordered) - 1)))
    idx = max(0, min(len(ordered) - 1, idx))
    return int(ordered[idx])


def write_chaos_report(
    scenario: str,
    summary: Dict,
    runs: List[Dict],
    *,
    output_dir: Path | str = Path("data/tests"),
) -> Path:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = out_dir / f"chaos_{scenario}_{ts}.json"
    payload = {
        "scenario": scenario,
        "chaos_config": current_config_dict(),
        "summary": summary,
        "runs": runs,
    }
    path.write_text(json.dumps(payload, indent=2))
    return path


def run_chaos_benchmark(
    *,
    scenario: str,
    num_runs: int,
    concurrency: int,
    turn_limit: int,
    model: str,
    valyu_url: str,
    user_profile: str = "user_info.json",
    company_resource: str = "company_resource.txt",
    output_dir: str | Path = "data",
    small_model: Optional[str] = None,
) -> Dict:
    """Execute multiple dual-agent runs under chaos mode and return a summary."""
    refresh_config()
    runs: List[Dict] = []
    start = time.perf_counter()
    kwargs = {
        "turn_limit": turn_limit,
        "model": model,
        "valyu_url": valyu_url,
        "user_profile": user_profile,
        "company_resource": company_resource,
        "output_dir": output_dir,
        "small_model": small_model,
    }

    def _run(index: int) -> Dict:
        run_start = time.perf_counter()
        try:
            result = run_dual_agents(**kwargs)
            latency_ms = int((time.perf_counter() - run_start) * 1000)
            run_id = Path(result["outputs_dir"]).name
            record = {
                "run_id": run_id,
                "scenario": scenario,
                "success": bool(result.get("final_plan")),
                "latency_ms": latency_ms,
                "outputs_dir": result.get("outputs_dir"),
                "telemetry": result.get("telemetry"),
                "final_plan": result.get("final_plan"),
                "errors": [],
            }
            return record
        except Exception as exc:  # pragma: no cover - chaos intentionally raises
            latency_ms = int((time.perf_counter() - run_start) * 1000)
            return {
                "run_id": f"error_{index}",
                "scenario": scenario,
                "success": False,
                "latency_ms": latency_ms,
                "outputs_dir": None,
                "telemetry": None,
                "final_plan": None,
                "errors": [repr(exc)],
            }

    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as executor:
        futures = [executor.submit(_run, idx) for idx in range(num_runs)]
        for fut in as_completed(futures):
            runs.append(fut.result())

    elapsed = time.perf_counter() - start
    successes = sum(1 for r in runs if r["success"])
    latencies = [r["latency_ms"] for r in runs if r.get("latency_ms") is not None]
    summary = {
        "scenario": scenario,
        "num_runs": num_runs,
        "concurrency": concurrency,
        "elapsed_s": round(elapsed, 3),
        "success_rate": round(successes / num_runs, 3) if num_runs else 0.0,
        "p50_latency_ms": _percentile(latencies, 50),
        "p95_latency_ms": _percentile(latencies, 95),
        "avg_latency_ms": int(sum(latencies) / len(latencies)) if latencies else 0,
        "error_count": sum(1 for r in runs if r["errors"]),
        "errors_sample": [r["errors"][0] for r in runs if r["errors"]][:5],
    }
    report_path = write_chaos_report(
        scenario,
        summary=summary,
        runs=runs,
        output_dir=Path(output_dir) / "tests",
    )
    summary["report_path"] = str(report_path)
    return summary

