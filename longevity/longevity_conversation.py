from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

from .config import load_config
from .longevity_agents import (
    ADVOCATE_NAME,
    PLANNER_NAME,
    build_agent_profiles,
    load_company_resource,
    load_user_profile,
    seed_message_for_advocate,
)
from .save_conversation import append_text, save_json, save_text
from .schemas import PlanItem, PlanSummary
from .valyu_validation import extract_claims
from .utils import call_llm, MockLLM, ensure_provider_ready
from .memory import SharedMemory
from .tools import extract_requested_services, tool_schedule_services


def run_conversation() -> None:
    """CLI entrypoint; preserves existing behavior and adds optional mode/mock flags."""
    parser = argparse.ArgumentParser(description="Longevity multi-agent conversation")
    parser.add_argument("--turn-limit", type=int, default=10)
    parser.add_argument("--model", type=str, default="gpt-4o-mini")
    parser.add_argument("--valyu-url", type=str, default="http://localhost:3000/validate")
    parser.add_argument("--enable-valyu", action="store_true")
    parser.add_argument("--user-profile", type=str, default="user_info.json")
    parser.add_argument("--company-resource", type=str, default="company_resource.txt")
    parser.add_argument("--output-dir", type=str, default="data")
    parser.add_argument("--mode", type=str, choices=["baseline", "optimized"], default="baseline")
    parser.add_argument("--use-mock", action="store_true", help="Use MockLLM for offline/dev runs")
    args = parser.parse_args()

    result = run_longevity_conversation(
        turn_limit=args.turn_limit,
        model=args.model,
        valyu_url=args.valyu_url,
        enable_valyu=args.enable_valyu,
        user_profile=args.user_profile,
        company_resource=args.company_resource,
        output_dir=args.output_dir,
        mode=args.mode,
        use_mock=args.use_mock,
    )
    print(json.dumps({k: v for k, v in result.items() if k not in {"plan_struct"}}, indent=2))


def run_longevity_conversation(
    turn_limit: int = 10,
    model: str = "gpt-4o-mini",
    valyu_url: str = "http://localhost:3000/validate",
    enable_valyu: bool = False,
    user_profile: str | Path = "user_info.json",
    company_resource: str | Path = "company_resource.txt",
    output_dir: str | Path = "data",
    mode: str = "baseline",
    scenario_id: Optional[str] = None,
    use_mock: bool = False,
    small_model: Optional[str] = None,
    big_model: Optional[str] = None,
) -> Dict[str, Any]:
    """Programmatic runner for a single A2A longevity conversation.

    Returns a result dict with metrics and a structured plan for hashing.
    """
    cfg = load_config(
        turn_limit=turn_limit,
        model=model,
        valyu_url=valyu_url,
        enable_valyu=enable_valyu,
        user_profile=user_profile,
        company_resource=company_resource,
        output_dir=output_dir,
    )

    run_id = f"run_{int(time.time()*1000)}_{hashlib.sha1(str(time.time()).encode()).hexdigest()[:6]}"

    if not use_mock:
        # Fail fast if real provider is requested but not configured
        ensure_provider_ready(cfg.model)

    # Load inputs
    user = load_user_profile(cfg.user_profile_path)
    company_text = load_company_resource(cfg.company_resource_path)
    profiles = build_agent_profiles(user, company_text)

    # Prepare run directory & files
    run_dir = cfg.make_run_dir()
    transcript_path = run_dir / "conversation_history.txt"
    summary_txt_path = run_dir / "longevity_plan_summary.txt"
    summary_json_path = run_dir / "longevity_plan_summary.json"
    validity_path = run_dir / "scientific_validity_checks.json"
    telemetry_path = run_dir / "telemetry.json"

    # Session context and routing
    # Shared memory across turns
    memory = SharedMemory()
    memory.add_fact("user_name", user.get("name", "User"))
    memory.add_fact("goals", user.get("goals", []))

    # Seed conversation
    advocate_seed = seed_message_for_advocate(user)
    transcript: List[Tuple[str, str]] = [("advocate", advocate_seed)]
    append_text(transcript_path, [f"{ADVOCATE_NAME}: {advocate_seed}\n"]) 

    telemetry_log: List[dict] = []
    collected_claims = []
    tokens_total = 0

    def _llm_for(role_name: str, turn: int, task_type: str = ""):
        nonlocal tokens_total
        chosen_model = cfg.model
        if use_mock:
            mock = MockLLM(role_name)
            t0 = time.perf_counter()
            out = mock.invoke(transcript[-1][1] if transcript else "start")
            dt = time.perf_counter() - t0
            telemetry_log.append({"step": len(telemetry_log) + 1, "speaker": role_name, "latency_s": dt, "provider": "mock"})
            tokens_total += max(1, len(out) // 4)
            return out
        else:
            # Provide a brief memory state as additional context at each step
            memory_hint = ("human", f"[shared_memory] {memory.render_brief()}")
            resp, tel = call_llm(chosen_model, profiles.planner_system if role_name == PLANNER_NAME else profiles.advocate_system, [*transcript, memory_hint])
            telemetry_log.append({"step": len(telemetry_log) + 1, "speaker": role_name, **tel})
            tokens_total += int((len(resp) + 100) // 4)
            return resp

    # Turn-taking loop (advocate starts -> planner -> advocate ...)
    for turn in range(cfg.turn_limit):
        # Planner responds
        planner_resp = _llm_for(PLANNER_NAME, turn, task_type="plan_synthesis" if (turn % 3 == 0) else "ack")
        append_text(transcript_path, [f"{PLANNER_NAME}: {planner_resp}\n"]) 
        transcript.append(("assistant", planner_resp))
        new_claims = extract_claims(planner_resp, turn_index=turn, speaker=PLANNER_NAME)
        collected_claims.extend(new_claims)
        for c in new_claims:
            memory.add_claim({"text": c.text, "turn": c.turn_index, "speaker": c.speaker})
        telemetry_log.append({"type": "memory_update", "claims_added": len(new_claims)})
        # Schedule services if the planner mentions them
        req = extract_requested_services(planner_resp)
        if req:
            booked = tool_schedule_services(memory, req, user.get("id", user.get("name", "user")), run_dir, telemetry_log)
            if booked:
                transcript.append(("assistant", f"[tool:scheduler] scheduled: {', '.join(b['service_type'] for b in booked)}"))
                append_text(transcript_path, [f"TOOL(scheduler): {', '.join(b['service_type'] for b in booked)}\n"]) 

        # Advocate responds
        advocate_resp = _llm_for(ADVOCATE_NAME, turn, task_type="ack")
        append_text(transcript_path, [f"{ADVOCATE_NAME}: {advocate_resp}\n"]) 
        transcript.append(("human", advocate_resp))
        new_claims = extract_claims(advocate_resp, turn_index=turn, speaker=ADVOCATE_NAME)
        collected_claims.extend(new_claims)
        for c in new_claims:
            memory.add_claim({"text": c.text, "turn": c.turn_index, "speaker": c.speaker})
        telemetry_log.append({"type": "memory_update", "claims_added": len(new_claims)})

    # Validate collected claims (best-effort)
    validations = []
    if cfg.enable_valyu and collected_claims:
        # Defer import to avoid cycle
        from .valyu_validation import validate_claims
        t0 = time.perf_counter()
        validations_list = validate_claims(collected_claims, cfg.valyu_url, timeout_s=cfg.valyu_timeout_s, batch=True)
        dt = time.perf_counter() - t0
        telemetry_log.append({"type": "tool", "name": "valyu_validate", "count": len(validations_list), "latency_s": dt})
        # Save and add to memory
        payload = [
            {
                "claim": v.claim.__dict__,
                "validity": v.validity,
                "confidence": v.confidence,
                "evidence": v.evidence,
                "server_unavailable": v.server_unavailable,
            }
            for v in validations_list
        ]
        for p in payload:
            memory.add_validation(p)
        validations = payload
        save_json(validity_path, payload)

    # Scheduling: propose a few concrete appointments for a fixed set of services
    # Use appointments accumulated via tool calls; if none, create a simple baseline set
    from .schemas import Appointment
    appointments = [Appointment(**a) for a in memory.appointments]
    if not appointments:
        # Fallback deterministic schedule
        from .scheduling.clinic_scheduler import generate_slots, find_available_slots, book_slot
        slots = generate_slots(seed=cfg.seed)
        for svc in ["baseline_bloodwork", "vo2_test", "lifestyle_coaching"]:
            avail = find_available_slots(slots, svc)
            if not avail:
                continue
            appt = book_slot(slots, svc, user_id=user.get("id", user.get("name", "user")), persist_path=run_dir / "bookings.json")
            if appt:
                appointments.append(appt)

    # Draft simple plan items and total cost
    plan_items: List[PlanItem] = []
    total_cost = 0.0
    for i, appt in enumerate(appointments, start=1):
        ev_flag = _evidence_flag_for_service(appt.service_type, validations)
        total_cost += appt.price
        plan_items.append(
            PlanItem(
                month=min(i, 6),
                service=appt.service_type,
                rationale=f"Supports user goals via {appt.service_type}.",
                appointment=appt,
                evidence_flag=ev_flag,
            )
        )

    warnings = []
    low_evidence = [pi.service for pi in plan_items if pi.evidence_flag in {"low", "unknown"}]
    if low_evidence:
        warnings.append(
            "Evidence-uncertain items present: " + ", ".join(sorted(set(low_evidence))) + ". Consider clinician review."
        )
    summary = PlanSummary(
        user_name=user.get("name", "User"),
        total_cost=round(total_cost, 2),
        items=plan_items,
        warnings=warnings,
        disclaimers=[
            "This plan is educational and not medical advice.",
            "Discuss all interventions with a licensed clinician.",
        ],
    )

    # Save outputs
    save_text(summary_txt_path, _format_summary_text(summary))
    plan_dict = _summary_to_dict(summary)
    save_json(summary_json_path, plan_dict)
    save_json(telemetry_path, telemetry_log)

    # Append to global run index for UI discovery
    try:
        _append_run_index(
            outputs_dir=run_dir,
            run_id=run_id,
            user_name=user.get("name", "User"),
            success=True,
            plan=plan_dict,
            telemetry=telemetry_log,
            validations=[
                {
                    "claim": getattr(v.claim, "text", None) if hasattr(v, "claim") else None,
                    "validity": getattr(v, "validity", None),
                    "confidence": getattr(v, "confidence", None),
                    "server_unavailable": getattr(v, "server_unavailable", None),
                }
                for v in (validations or [])
            ],
        )
    except Exception:
        pass

    # Shape result
    success = True
    errors: List[str] = []
    result: Dict[str, Any] = {
        "run_id": run_id,
        "scenario_id": scenario_id or "default",
        "success": success,
        "num_turns": cfg.turn_limit,
        "plan_struct": plan_dict,
        "tokens_total": tokens_total,
        "latency_ms": int(sum(t.get("latency_s", 0.0) for t in telemetry_log) * 1000),
        "errors": errors,
        "outputs_dir": str(run_dir),
        "mode": mode,
    }
    return result


def _append_run_index(outputs_dir: Path, run_id: str, user_name: str, success: bool, plan: dict, telemetry: List[dict], validations: List[dict]) -> None:
    """Append a compact record to data/run_index.json and write a per-run manifest.

    This enables the frontend API to list runs and fetch details without scanning.
    """
    root = outputs_dir.parent.parent if outputs_dir.name.startswith("longevity_plan_") else outputs_dir.parent
    data_dir = root if (root.name == "data") else outputs_dir.parent
    index_path = data_dir / "run_index.json"
    manifest = {
        "id": outputs_dir.name,
        "run_id": run_id,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "user": user_name,
        "status": "success" if success else "failed",
        "plan_score": _plan_score(plan, validations),
        "outputs_dir": str(outputs_dir),
    }
    # write manifest for run details
    (outputs_dir / "manifest.json").write_text(json.dumps({
        "id": manifest["id"],
        "summary": plan,
        "telemetry": telemetry,
        "validations": validations,
        "conversation": (outputs_dir / "conversation_history.txt").read_text(encoding="utf-8") if (outputs_dir / "conversation_history.txt").exists() else "",
        "bookings": json.loads((outputs_dir / "bookings.json").read_text()) if (outputs_dir / "bookings.json").exists() else [],
    }, indent=2))
    # append to index
    try:
        existing = json.loads(index_path.read_text()) if index_path.exists() else []
    except Exception:
        existing = []
    # de-dup by id
    existing = [e for e in existing if e.get("id") != manifest["id"]]
    existing.insert(0, manifest)
    index_path.write_text(json.dumps(existing[:200], indent=2))


def _plan_score(plan: dict, validations: List[dict]) -> float:
    try:
        items = plan.get("items", [])
        if not items:
            return 0.0
        ok = sum(1 for it in items if (it.get("evidence_flag") == "ok"))
        low = sum(1 for it in items if (it.get("evidence_flag") == "low"))
        # simple heuristic score 0..100
        score = max(0.0, 100.0 * (ok / max(1, len(items)) - 0.25 * (low / max(1, len(items)))))
        return round(score, 1)
    except Exception:
        return 0.0


def _evidence_flag_for_service(service_type: str, validations) -> str:
    if not validations:
        return "unknown"
    # naive mapping: if any claim mentioning service is low-conf -> low
    text_hits = [v for v in validations if service_type.replace("_", " ") in (v.claim.text.lower())]
    if not text_hits:
        return "unknown"
    conf = max(v.confidence for v in text_hits if v.validity == "true") if any(v.validity == "true" for v in text_hits) else 0.0
    if conf >= 0.6:
        return "ok"
    return "low"


def _format_summary_text(summary: PlanSummary) -> str:
    lines = [
        f"LONGEVITY PLAN SUMMARY for {summary.user_name}",
        f"Total Cost (est.): ${summary.total_cost:.2f}",
        "",
        "Appointments:",
    ]
    for item in summary.items:
        appt = item.appointment
        if appt:
            lines.append(
                f"- M{item.month}: {item.service} @ {appt.start_iso} ({appt.staff_role}, {appt.location}) ${appt.price:.2f} [evidence: {item.evidence_flag}]"
            )
    if summary.warnings:
        lines.append("")
        lines.append("Warnings:")
        for w in summary.warnings:
            lines.append(f"- {w}")
    lines.append("")
    lines.append("Disclaimers:")
    for d in summary.disclaimers:
        lines.append(f"- {d}")
    return "\n".join(lines) + "\n"


def _summary_to_dict(summary: PlanSummary) -> dict:
    return {
        "user_name": summary.user_name,
        "total_cost": summary.total_cost,
        "items": [
            {
                "month": it.month,
                "service": it.service,
                "rationale": it.rationale,
                "evidence_flag": it.evidence_flag,
                "appointment": it.appointment.__dict__ if it.appointment else None,
            }
            for it in summary.items
        ],
        "warnings": summary.warnings,
        "disclaimers": summary.disclaimers,
    }


if __name__ == "__main__":
    run_conversation()
