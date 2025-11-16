from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from dotenv import load_dotenv
from langsmith import Client
from langsmith.utils import LangSmithNotFoundError
def _ensure_project_exists(client: Client, project_name: Optional[str]) -> None:
    if not project_name:
        return
    try:
        client.read_project(project_name=project_name)
    except LangSmithNotFoundError:
        client.create_project(project_name=project_name, description="Created automatically by eval scripts", upsert=True)

# Ensure LANGSMITH / provider environment variables from .env are available
load_dotenv(override=False)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_NAME = "Dual Agents Longevity Conversation"


@dataclass
class DualAgentRunRecord:
    run_id: str
    name: str
    conversation_id: str
    outputs_dir: Path
    final_plan_path: Optional[Path]
    final_plan_dict: Optional[Dict[str, Any]]
    final_plan_text: Optional[str]
    transcript_path: Optional[Path]
    transcript_text: Optional[str]
    scenario_id: str
    user_name: Optional[str]
    metadata: Dict[str, Any]
    inputs: Dict[str, Any]
    started_at: Optional[datetime]


def get_langsmith_client() -> Client:
    api_url = os.getenv("LANGSMITH_API_URL")
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        raise RuntimeError("LANGSMITH_API_KEY is required for evaluation scripts.")
    return Client(api_url=api_url, api_key=api_key)


def _resolve_repo_path(path_str: str) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    return path


def _load_file_text(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def _extract_outputs_dir(outputs: Optional[Dict[str, Any]]) -> Optional[str]:
    if not outputs:
        return None
    if isinstance(outputs, dict) and "outputs_dir" in outputs:
        return outputs["outputs_dir"]
    result = outputs.get("result") if isinstance(outputs, dict) else None
    if isinstance(result, dict) and "outputs_dir" in result:
        return result["outputs_dir"]
    return None


def _extract_final_plan(outputs: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not outputs:
        return None
    if isinstance(outputs, dict) and "final_plan" in outputs and isinstance(outputs["final_plan"], dict):
        return outputs["final_plan"]
    result = outputs.get("result") if isinstance(outputs, dict) else None
    if isinstance(result, dict) and isinstance(result.get("final_plan"), dict):
        return result["final_plan"]
    return None


def _load_plan_from_disk(outputs_dir: Path) -> Tuple[Optional[Path], Optional[Dict[str, Any]], Optional[str]]:
    candidates: Sequence[Tuple[str, bool]] = [
        ("final_plan.json", True),
        ("longevity_plan_summary.json", True),
        ("manifest.json", True),
        ("longevity_plan_summary.txt", False),
    ]
    for filename, is_json in candidates:
        path = outputs_dir / filename
        if not path.exists():
            continue
        if is_json:
            data = _load_json(path)
            if not data:
                continue
            if filename == "manifest.json":
                summary = data.get("summary")
                if not isinstance(summary, dict):
                    continue
                return path, summary, json.dumps(summary, indent=2)
            return path, data, json.dumps(data, indent=2)
        text = _load_file_text(path)
        if text:
            return path, None, text
    return None, None, None


def _infer_scenario_id(
    plan: Optional[Dict[str, Any]],
    metadata: Dict[str, Any],
    outputs_dir: Path,
    inputs: Dict[str, Any],
) -> Tuple[str, Optional[str]]:
    scenario = metadata.get("scenario_id")
    user_name = None
    if plan:
        user_name = plan.get("user_name")
    if not scenario and user_name:
        scenario = user_name
    if not scenario:
        user_profile = inputs.get("user_profile")
        if user_profile:
            scenario = Path(user_profile).stem
    if not scenario:
        scenario = metadata.get("conversation_id")
    if not scenario:
        scenario = outputs_dir.name
    return _slugify(str(scenario)), user_name


def _extract_plan_text_from_transcript(transcript: Optional[str]) -> Optional[str]:
    if not transcript:
        return None
    lines = [line.strip() for line in transcript.strip().splitlines() if line.strip()]
    for line in reversed(lines):
        if ": " in line:
            speaker, content = line.split(": ", 1)
            if content:
                return f"{speaker}: {content}"
    return lines[-1] if lines else None


def _slugify(value: str) -> str:
    lowered = value.strip().lower()
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in lowered)
    parts = [p for p in cleaned.split("-") if p]
    return "-".join(parts) or "scenario"


def fetch_dual_agent_runs(
    client: Client,
    project: Optional[str] = None,
    limit: int = 50,
    since: Optional[str] = None,
    run_name: str = DEFAULT_RUN_NAME,
) -> List[DualAgentRunRecord]:
    since_dt: Optional[datetime] = None
    if since:
        try:
            since_dt = datetime.fromisoformat(since)
        except ValueError:
            raise ValueError("Parameter 'since' must be ISO formatted, e.g., 2025-11-16T00:00:00")
    records: List[DualAgentRunRecord] = []
    fetch_limit = max(limit * 3, limit) if limit else None
    _ensure_project_exists(client, project)
    run_iter = client.list_runs(
        project_name=project,
        run_type="chain",
        is_root=True,
        start_time=since_dt,
        limit=fetch_limit,
    )
    for run in run_iter:
        if run_name and getattr(run, "name", "") != run_name:
            continue
        outputs_dict = getattr(run, "outputs", None)
        outputs_dir_str = _extract_outputs_dir(outputs_dict)
        if not outputs_dir_str:
            continue
        outputs_dir = _resolve_repo_path(outputs_dir_str)
        plan_path, plan_dict_disk, plan_text_disk = _load_plan_from_disk(outputs_dir)
        plan_dict = plan_dict_disk or _extract_final_plan(outputs_dict)
        transcript_path = outputs_dir / "conversation_history.txt"
        transcript_text = _load_file_text(transcript_path)
        plan_text = plan_text_disk or (json.dumps(plan_dict, indent=2) if plan_dict else None)
        if not plan_text:
            plan_text = _extract_plan_text_from_transcript(transcript_text)
        metadata = dict(getattr(run, "metadata", {}) or {})
        metadata.setdefault("conversation_id", outputs_dir.name)
        scenario_id, user_name = _infer_scenario_id(plan_dict, metadata, outputs_dir, getattr(run, "inputs", {}) or {})
        record = DualAgentRunRecord(
            run_id=str(getattr(run, "id", "")),
            name=getattr(run, "name", ""),
            conversation_id=metadata.get("conversation_id", outputs_dir.name),
            outputs_dir=outputs_dir,
            final_plan_path=plan_path,
            final_plan_dict=plan_dict,
            final_plan_text=plan_text,
            transcript_path=transcript_path if transcript_path.exists() else None,
            transcript_text=transcript_text,
            scenario_id=scenario_id,
            user_name=user_name,
            metadata=metadata,
            inputs=getattr(run, "inputs", {}) or {},
            started_at=getattr(run, "start_time", None),
        )
        records.append(record)
        if len(records) >= limit:
            break
    return records


def group_runs_by_scenario(runs: Iterable[DualAgentRunRecord], min_group_size: int = 2) -> Dict[str, List[DualAgentRunRecord]]:
    groups: Dict[str, List[DualAgentRunRecord]] = {}
    for run in runs:
        groups.setdefault(run.scenario_id, []).append(run)
    pruned: Dict[str, List[DualAgentRunRecord]] = {}
    for scenario, scenario_runs in groups.items():
        if len(scenario_runs) < min_group_size:
            continue
        pruned[scenario] = sorted(scenario_runs, key=lambda r: r.started_at or datetime.min)
    return pruned


def load_user_profile_text(path: Path) -> str:
    data = _load_json(path)
    if not data:
        text = _load_file_text(path)
        return text or ""
    lines = []
    for key, value in data.items():
        if isinstance(value, (list, tuple)):
            formatted = ", ".join(str(v) for v in value)
        elif isinstance(value, dict):
            formatted = json.dumps(value, indent=2)
        else:
            formatted = str(value)
        lines.append(f"{key}: {formatted}")
    return "\n".join(lines)


__all__ = [
    "Client",
    "DualAgentRunRecord",
    "fetch_dual_agent_runs",
    "get_langsmith_client",
    "group_runs_by_scenario",
    "load_user_profile_text",
]

