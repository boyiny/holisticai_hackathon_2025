1. chaos testing by introducting failures in llm calls, tool calls, network jitters, latency etc.: Prakash:
   Spec plan file: specs/chaos_test.md
   Commands for chaos test:
   1. python scripts/run_chaos_llm_slow.py \
     --num-runs 4 --concurrency 2 --turn-limit 4 \
     --model gpt-4o-mini --small-model gpt-4o-mini
   2. python scripts/run_chaos_valyu_down.py \
     --num-runs 4 --concurrency 2 --turn-limit 4 \
     --model gpt-4o-mini --small-model gpt-4o-mini \
     --valyu-url http://localhost:3000/validate
   3. python scripts/run_chaos_scheduler_failures.py \
     --num-runs 4 --concurrency 2 --turn-limit 4 \
     --model gpt-4o-mini --small-model gpt-4o-mini

# Understanding Chaos report:

- All chaos scripts drop JSON reports in `data/tests/chaos_<scenario>_<timestamp>.json`. Each file has:
  - `scenario`: name of the chaos experiment (e.g. `llm_slow`, `valyu_down`, `scheduler_failures`).
  - `chaos_config`: the exact env/chaos parameters that were active (jitter ranges, failure probabilities, etc.).
  - `summary`: high-level metrics so you can compare runs at a glance:
    - `num_runs`, `concurrency`, `elapsed_s`: test dimensions and wall-clock time.
    - `success_rate`: fraction of conversations that produced a final plan (`final_plan` path not null).
    - `p50_latency_ms`, `p95_latency_ms`, `avg_latency_ms`: distribution of end-to-end runtimes per conversation.
    - `error_count` + `errors_sample`: how many runs hit unhandled errors (usually chaos-induced exceptions) and representative messages.
    - `report_path`: convenience pointer to the JSON file itself.
  - `runs`: array with one entry per conversation, containing:
    - `run_id`, `outputs_dir`, `telemetry`, `final_plan`: references to artifacts for that run.
    - `latency_ms`: total runtime for that conversation under chaos.
    - `errors`: list of errors for that run (empty when failures were gracefully absorbed).


2. Use Valyu to make the conversation safe and medically correct: Boyin
3. Research on optimization and regulations : Joon
4. use parallel test and llm judge to do eval: Prakash
   Spec plan file: specs/eval.md
   - final plan consistency: `python scripts/eval_final_plan_consistency.py --project <langsmith_project> --max-runs 20`
       - example report: data/evals/conversation_eval_20251116_123711.json
       - How to interpret the summary section in the report:
          - avg_collaboration: Average of the judge’s 0‑10 “collaboration similarity” scores across all scenario comparisons. It reflects how closely the two conversations’ advocate↔planner dynamics resemble each other (structure, turn-taking, cooperative tone).
          - avg_alignment_a / avg_alignment_b: Mean 0‑10 alignment scores for the reference run (“A”) and the comparison run (“B”) respectively. Each measures how well that conversation/plan combination stays true to the user’s goals and context.
          - avg_reasoning_depth: Average score for how thorough and coherent the reasoning is (did agents justify choices, sequence steps sensibly, surface trade‑offs).
          - avg_consistency: Mean 0‑10 rating for whether each conversation’s final plan actually follows from the dialogue (no hallucinated steps, conclusions tied to discussion).
          - num_pairs: Number of scenario comparisons the eval actually ran (each pair is one reference run vs. one comparison run for the same user profile).
          - project: The LangSmith project whose runs were evaluated (final_report_eval in your case).
          - judge_model: The model used as the LLM judge (defaults to gpt-4o-mini, configurable via --judge-model).
   - conversation consistency: `python scripts/eval_conversation_consistency.py --project <langsmith_project> --max-runs 20 --summary-model gpt-4o-mini`
       - example report: data/evals/conversation_eval_20251116_124355.json

# Understanding eval report:
When you open any generated eval JSON (for example `data/evals/conversation_eval_20251116_123711.json`), you’ll see two sections: `pairs` and `summary`.
- `pairs`: each entry compares two LangSmith runs of the same scenario (usually the same `user_profile`). It lists the run IDs, local artifact paths, and the judge’s per-run scores.
- Per-pair numeric fields:
  - `collaboration_similarity`: 0–10 score for how similar the two conversations’ advocate↔planner collaboration feels (structure, tone, back-and-forth).
  - `alignment_a` / `alignment_b`: 0–10 scores for how well each conversation stays aligned with user goals and constraints (A is the reference, B the comparison).
  - `reasoning_depth`: 0–10 score for how thorough and coherent the reasoning chain is within the pair.
  - `consistency_score`: 0–10 score for whether each conversation’s final plan logically follows from what was discussed (no hallucinated steps).
  - `recommendation`: judge’s winner (`conversation_a`, `conversation_b`, `tie`, or `insufficient`) with supporting `notes`.
- `summary`: aggregates across all pairs.
  - `avg_collaboration`, `avg_alignment_*`, `avg_reasoning_depth`, `avg_consistency`: simple averages of the per-pair scores (still 0–10 scale).
  - `num_pairs`: number of scenario comparisons that actually ran.
  - `project`: LangSmith project the runs were pulled from.
  - `judge_model`: LLM judge used (defaults to `gpt-4o-mini` unless you pass `--judge-model`).

## Performance optimization
Slow run ~300s, 29000 tokens: https://smith.langchain.com/public/5a6c1c09-7812-4721-931b-6c57579fdce8/r

fast run 81s, 9000 tokens: https://smith.langchain.com/public/eac327f8-89b3-4409-9791-0942255e4285/r
