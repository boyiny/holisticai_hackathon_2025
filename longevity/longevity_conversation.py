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
from .model_router import ModelRouter
from .save_conversation import append_text, save_json, save_text
from .schemas import PlanItem, PlanSummary
from .session import SessionContext
from .tooling import concurrency_limited_validate_claims
from .valyu_validation import extract_claims
from .utils import call_llm, MockLLM, ensure_provider_ready
from .scheduling.clinic_scheduler import (
    generate_slots,
    find_available_slots,
    book_slot,
)


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
    router = None
    if mode == "optimized":
        router = ModelRouter(
            small_model=small_model or cfg.model,
            big_model=big_model or cfg.model,
        )
    sess = SessionContext(
        session_id=run_id,
        run_dir=run_dir,
        user_profile=user,
        clinic_profile=company_text,
        mode=mode,
        small_model=(small_model or cfg.model),
        big_model=(big_model or cfg.model),
    )

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
        if router is not None:
            chosen_model = router.choose_model(task_type=task_type, turn_index=turn, speaker=("planner" if role_name == PLANNER_NAME else "advocate"))
        if use_mock:
            mock = MockLLM(role_name)
            t0 = time.perf_counter()
            out = mock.invoke(transcript[-1][1] if transcript else "start")
            dt = time.perf_counter() - t0
            telemetry_log.append({"step": len(telemetry_log) + 1, "speaker": role_name, "latency_s": dt, "provider": "mock"})
            tokens_total += max(1, len(out) // 4)
            return out
        else:
            resp, tel = call_llm(chosen_model, profiles.planner_system if role_name == PLANNER_NAME else profiles.advocate_system, transcript)
            telemetry_log.append({"step": len(telemetry_log) + 1, "speaker": role_name, **tel})
            tokens_total += int((len(resp) + 100) // 4)
            return resp

    # Turn-taking loop (advocate starts -> planner -> advocate ...)
    for turn in range(cfg.turn_limit):
        # Planner responds
        planner_resp = _llm_for(PLANNER_NAME, turn, task_type="plan_synthesis" if (turn % 3 == 0) else "ack")
        append_text(transcript_path, [f"{PLANNER_NAME}: {planner_resp}\n"]) 
        transcript.append(("assistant", planner_resp))
        collected_claims.extend(extract_claims(planner_resp, turn_index=turn, speaker=PLANNER_NAME))

        # Advocate responds
        advocate_resp = _llm_for(ADVOCATE_NAME, turn, task_type="ack")
        append_text(transcript_path, [f"{ADVOCATE_NAME}: {advocate_resp}\n"]) 
        transcript.append(("human", advocate_resp))
        collected_claims.extend(extract_claims(advocate_resp, turn_index=turn, speaker=ADVOCATE_NAME))

    # Validate collected claims (best-effort)
    validations = []
    if cfg.enable_valyu and collected_claims:
        if mode == "optimized":
            validations = concurrency_limited_validate_claims(
                collected_claims, cfg.valyu_url, timeout_s=cfg.valyu_timeout_s, batch=True
            )
        else:
            # Defer import to avoid cycle
            from .valyu_validation import validate_claims

            validations = validate_claims(collected_claims, cfg.valyu_url, timeout_s=cfg.valyu_timeout_s, batch=True)
        save_json(validity_path, [
            {
                "claim": v.claim.__dict__,
                "validity": v.validity,
                "confidence": v.confidence,
                "evidence": v.evidence,
                "server_unavailable": v.server_unavailable,
                "raw_response": v.raw_response,
            }
            for v in validations
        ])

    # Scheduling: propose a few concrete appointments for a fixed set of services
    slots = generate_slots(seed=cfg.seed)
    sess.scheduler_state["slots"] = slots
    appointments = []
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
