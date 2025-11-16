from __future__ import annotations

import json
import os
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
FRONTEND_DIR = ROOT / "frontend"


def _json_response(handler: SimpleHTTPRequestHandler, payload: Any, status: int = 200):
    body = json.dumps(payload, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _error(handler: SimpleHTTPRequestHandler, msg: str, code: int = 400):
    _json_response(handler, {"error": msg}, status=code)


def _list_runs() -> list[Dict[str, Any]]:
    if not DATA_DIR.exists():
        return []
    runs = []
    for d in sorted(DATA_DIR.iterdir()):
        if not d.is_dir() or not d.name.startswith("longevity_plan_"):
            continue
        ts = d.name.replace("longevity_plan_", "")
        try:
            timestamp = datetime.strptime(ts, "%Y%m%d_%H%M%S").isoformat()
        except Exception:
            timestamp = ts
        summary = d / "longevity_plan_summary.json"
        telemetry = d / "telemetry.json"
        validity = d / "scientific_validity_checks.json"
        user = "Unknown"
        status = "success"
        plan_score = None
        try:
            if summary.exists():
                js = json.loads(summary.read_text())
                user = js.get("user_name", user)
                warnings = js.get("warnings", [])
                status = "warning" if warnings else "success"
        except Exception:
            status = "failed"
        runs.append({
            "id": d.name,
            "timestamp": timestamp,
            "user": user,
            "plan_score": plan_score,
            "status": status,
        })
    return list(reversed(runs))


def _get_run(run_id: str) -> Dict[str, Any]:
    d = DATA_DIR / run_id
    if not d.exists():
        raise FileNotFoundError(run_id)
    def _load(p: Path, default: Any) -> Any:
        try:
            return json.loads(p.read_text()) if p.exists() else default
        except Exception:
            return default
    summary = _load(d / "longevity_plan_summary.json", {})
    telemetry = _load(d / "telemetry.json", [])
    validity = _load(d / "scientific_validity_checks.json", [])
    convo = (d / "conversation_history.txt").read_text() if (d / "conversation_history.txt").exists() else ""
    bookings = _load(d / "bookings.json", [])
    return {
        "id": run_id,
        "summary": summary,
        "telemetry": telemetry,
        "validations": validity,
        "conversation": convo,
        "bookings": bookings,
    }


def _metrics_overview() -> Dict[str, Any]:
    runs = _list_runs()
    latencies = []
    valyu_total = 0
    valyu_unknown = 0
    for r in runs:
        d = DATA_DIR / r["id"]
        try:
            tel = json.loads((d / "telemetry.json").read_text())
            latencies.extend([t.get("latency_s", 0) for t in tel])
        except Exception:
            pass
        try:
            checks = json.loads((d / "scientific_validity_checks.json").read_text())
            valyu_total += len(checks)
            valyu_unknown += sum(1 for c in checks if str(c.get("validity", "unknown")) == "unknown")
        except Exception:
            pass
    avg_latency = (sum(latencies) / len(latencies)) if latencies else None
    coverage = None
    if valyu_total:
        coverage = round(100 * (1 - (valyu_unknown / valyu_total)), 1)
    return {
        "avg_latency_s": avg_latency,
        "avg_tokens": None,
        "plan_consistency_score": None,
        "scientific_validity_coverage_pct": coverage,
        "runs_count": len(runs),
    }


def _tests_list() -> list[Dict[str, Any]]:
    tests = [
        {"name": "Consistency", "file": "tests/test_consistency.py", "description": "Repeated runs produce stable plans.", "status": "unknown"},
        {"name": "Chaos", "file": "tests/test_chaos.py", "description": "Fault injection resilience.", "status": "unknown"},
        {"name": "Load", "file": "tests/test_load.py", "description": "Parallel conversation runs.", "status": "unknown"},
        {"name": "Role Confusion", "file": "tests/test_role_confusion.py", "description": "No role flipping.", "status": "unknown"},
        {"name": "Scientific Safety", "file": "tests/test_scientific_safety.py", "description": "Detect unsafe claims.", "status": "unknown"},
    ]
    return tests


class APIServer(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):  # CORS preflight
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path.startswith("/api/"):
            try:
                if self.path == "/api/runs":
                    return _json_response(self, _list_runs())
                if self.path.startswith("/api/runs/"):
                    run_id = self.path.split("/api/runs/")[-1]
                    return _json_response(self, _get_run(run_id))
                if self.path == "/api/metrics/overview":
                    return _json_response(self, _metrics_overview())
                if self.path == "/api/tests":
                    return _json_response(self, _tests_list())
                return _error(self, "Not Found", 404)
            except FileNotFoundError:
                return _error(self, "Run not found", 404)
            except Exception as e:
                return _error(self, f"Server error: {e}", 500)

        # Serve frontend static files if present; SPA fallback to index.html
        if FRONTEND_DIR.exists():
            self.directory = str(FRONTEND_DIR)
            # Try file first
            target = (FRONTEND_DIR / self.path.lstrip("/")).resolve()
            if target.is_file():
                return super().do_GET()
            # Otherwise, serve index.html for client routing
            self.path = "/index.html"
            return super().do_GET()
        return super().do_GET()

    def do_POST(self):
        if self.path == "/api/tests/run":
            # Stub: accept request and return scheduled=true
            return _json_response(self, {"scheduled": True})
        return _error(self, "Not Found", 404)


def main():
    port = int(os.getenv("PORT", "5174"))
    addr = ("0.0.0.0", port)
    httpd = HTTPServer(addr, APIServer)
    print(f"API + static server running on http://{addr[0]}:{addr[1]}")
    print(" - /api/runs, /api/runs/<id>, /api/metrics/overview, /api/tests")
    if FRONTEND_DIR.exists():
        print(" - Serving frontend static from ./frontend")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
