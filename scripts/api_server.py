from __future__ import annotations

import json
import threading
import sys
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure project root is on sys.path so local packages like `longevity` can be imported
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import os
from dotenv import load_dotenv
from longevity.longevity_conversation import run_longevity_conversation
from longevity.dual_agents import run_dual_agents
from scripts.run_parallel_test import run_parallel


app = FastAPI(title="Longevity Agent API", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
INTRO_PATH = Path("Intro.mp4")


class ParallelRequest(BaseModel):
    concurrency: int = 10
    num_runs: int = 10
    mode: str = "optimized"  # "baseline" or "optimized"
    turn_limit: int = 10
    model: str = "gpt-4o-mini"
    valyu_url: str = "http://localhost:3000/validate"
    enable_valyu: bool = True
    small_model: str | None = None
    big_model: str | None = None
    use_mock: bool = False


class DuoRunRequest(BaseModel):
    turn_limit: int = 8
    model: str = "gpt-4o-mini"
    small_model: str | None = None


class TTSRequest(BaseModel):
    text: str
    voice_id: str
    model_id: str | None = None  # e.g., "eleven_multilingual_v2"


@app.get("/api/metrics/overview")
def metrics_overview() -> Dict[str, Any]:
    index = _read_index()
    if not index:
        return {
            "avg_latency_s": None,
            "avg_tokens": None,
            "plan_consistency_score": None,
            "scientific_validity_coverage_pct": None,
            "runs_count": 0,
        }
    # Aggregate from per-run manifests
    latencies: List[float] = []
    tokens: List[int] = []
    hashes: List[str] = []
    validity_hits = 0
    for item in index[:100]:
        manifest = _read_manifest(Path(item["outputs_dir"]))
        if not manifest:
            continue
        lat = sum(float(t.get("latency_s", 0.0)) for t in manifest.get("telemetry", []))
        latencies.append(lat)
        # tokens approximated from telemetry length if not present
        tokens.append(int(sum(len(str(t)) for t in manifest.get("telemetry", [])) // 40))
        hashes.append(_plan_hash(manifest.get("summary", {})))
        if manifest.get("validations"):
            validity_hits += 1
    avg_latency = sum(latencies) / len(latencies) if latencies else None
    avg_tokens = int(sum(tokens) / len(tokens)) if tokens else None
    # majority hash fraction
    majority = max(set(hashes), key=hashes.count) if hashes else None
    consistency = (sum(1 for h in hashes if h == majority) / len(hashes)) if hashes else None
    validity_cov = int(100 * validity_hits / len(index)) if index else None
    return {
        "avg_latency_s": avg_latency,
        "avg_tokens": avg_tokens,
        "plan_consistency_score": consistency,
        "scientific_validity_coverage_pct": validity_cov,
        "runs_count": len(index),
    }


@app.get("/api/runs")
def list_runs() -> List[Dict[str, Any]]:
    index = _read_index()
    return [
        {
            "id": it["id"],
            "timestamp": it.get("timestamp"),
            "user": it.get("user"),
            "plan_score": it.get("plan_score"),
            "status": it.get("status", "success"),
        }
        for it in index
    ]


@app.get("/api/runs/{run_id}")
def get_run(run_id: str) -> Dict[str, Any]:
    index = _read_index()
    item = next((i for i in index if i.get("id") == run_id), None)
    if not item:
        raise HTTPException(404, detail="Run not found")
    manifest = _read_manifest(Path(item["outputs_dir"]))
    if not manifest:
        raise HTTPException(404, detail="Manifest not found")
    return {
        "id": run_id,
        **manifest,
    }


@app.get("/assets/intro.mp4")
def get_intro_video():
    if not INTRO_PATH.exists():
        raise HTTPException(404, detail="Intro video not found")
    return FileResponse(str(INTRO_PATH), media_type="video/mp4")


@app.post("/api/run/parallel")
def run_parallel_endpoint(req: ParallelRequest) -> Dict[str, Any]:
    summary = run_parallel(
        concurrency=req.concurrency,
        num_runs=req.num_runs,
        mode=req.mode,
        scenario="ui_triggered",
        turn_limit=req.turn_limit,
        model=req.model,
        valyu_url=req.valyu_url,
        enable_valyu=req.enable_valyu,
        output_dir=DATA_DIR,
        use_mock=req.use_mock,
        small_model=req.small_model,
        big_model=req.big_model,
    )
    return summary


@app.post("/api/run/one")
def run_one() -> Dict[str, Any]:
    # Quick single optimized run, for debugging
    res = run_longevity_conversation(turn_limit=4, mode="optimized")
    return res


@app.post("/api/duo/run")
def run_duo_agents(req: DuoRunRequest) -> Dict[str, Any]:
    """Run the LEO↔LUNA dual-agent conversation and return the transcript messages."""
    res = run_dual_agents(
        turn_limit=req.turn_limit,
        model=req.model,
        small_model=req.small_model,
    )
    transcript_path = Path(res.get("transcript", ""))
    messages: list[dict] = []
    if transcript_path.exists():
        try:
            raw = transcript_path.read_text(encoding="utf-8").splitlines()
            for line in raw:
                if not line.strip():
                    continue
                # Expect lines like "Health Advocate: ..." or "Service Planner: ..."
                if ":" in line:
                    speaker, text = line.split(":", 1)
                    sp = speaker.strip()
                    role = "LEO" if sp.lower().startswith("health advocate") else ("LUNA" if sp.lower().startswith("service planner") else sp)
                    messages.append({"speaker": role, "text": text.strip()})
        except Exception:
            pass
    return {"outputs_dir": res.get("outputs_dir"), "messages": messages}


@app.post("/api/tts")
async def tts(req: TTSRequest):
    """Synthesize speech for given text using ElevenLabs TTS and return audio/mpeg bytes."""
    load_dotenv(override=False)
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise HTTPException(500, detail="ELEVENLABS_API_KEY missing on server")
    import httpx
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{req.voice_id}/stream"
    payload = {"text": req.text}
    if req.model_id:
        payload["model_id"] = req.model_id
    headers = {
        "xi-api-key": api_key,
        "accept": "audio/mpeg",
        "content-type": "application/json",
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            raise HTTPException(500, detail=f"TTS failed: {r.status_code} {r.text[:200]}")
        return Response(content=r.content, media_type="audio/mpeg")


def _read_index() -> List[Dict[str, Any]]:
    p = DATA_DIR / "run_index.json"
    try:
        return json.loads(p.read_text()) if p.exists() else []
    except Exception:
        return []


def _read_manifest(run_dir: Path) -> Dict[str, Any] | None:
    mp = run_dir / "manifest.json"
    if not mp.exists():
        return None
    try:
        return json.loads(mp.read_text())
    except Exception:
        return None


def _plan_hash(plan: Dict[str, Any]) -> str:
    try:
        return __import__("hashlib").sha256(json.dumps(plan, sort_keys=True).encode("utf-8")).hexdigest()
    except Exception:
        return ""


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5174)
