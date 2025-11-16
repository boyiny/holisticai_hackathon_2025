<!-- 12d483fb-0c56-4fd9-9011-834f3d2ffc54 dbd93f4a-d039-4929-ab4a-a537fb630b8d -->
## Dual-Agent LLM-Judge Eval Plan

### Goals

- **Goal 1**: Use LangSmith's eval framework (reusing existing traces) to measure how consistent the `run_dual_agents` final plans are across repeated runs of the same scenario.
- **Goal 2**: Add a second eval focusing on overall conversation behavior (transcript + plan) for collaboration quality and alignment with user goals.

### High-Level Approach

- **Reuse LangSmith traces**: Leverage the existing `@traceable` runs (name `Dual Agents Longevity Conversation`) and their `metadata.outputs_dir` to locate `final_plan.json` and `conversation_history.txt` for each conversation.
- **Group comparable runs**: Define a grouping key (e.g., user profile or user name from the plan/user profile) so we can compare multiple runs of the same underlying scenario.
- **LLM judge via LangSmith evals**: For each group, create evaluation examples and run custom LLM-judge metrics using LangSmith's `Client.evaluate`/custom evaluators.
- **Two eval entry points**: Implement two scripts:
- `scripts/eval_final_plan_consistency.py` (final-plan-only consistency & quality).
- `scripts/eval_conversation_consistency.py` (transcript + plan behavior and cross-run similarity).

### Detailed Steps

1. **Clarify run selection & grouping strategy**

- Decide how to identify comparable runs (e.g., filter LangSmith runs by project/tag and group by user identity or profile path inferred from the plan/user profile).
- Document this assumption briefly so future eval runs know what “same scenario” means.

2. **Add shared eval utilities (LangSmith + filesystem helpers)**

- Create an `eval/` package (e.g., `eval/__init__.py`, `eval/utils.py`) with helpers to:
- Instantiate a LangSmith client from env vars.
- Query root runs for `Dual Agents Longevity Conversation` and extract `conversation_id`, `metadata.outputs_dir`, and timestamps.
- Load `final_plan.json` and `conversation_history.txt` from each `outputs_dir`.
- Group runs by scenario key and build in-memory structures like `{scenario_id: [run_info_with_plan_and_transcript...]}`.

3. **Design LLM-judge prompts and output schema**

- Define prompt templates for the **final-plan-only** eval:
- Input: user goals (from user profile or final plan), Plan A, Plan B.
- Ask for: (a) similarity score (e.g., 1–10), (b) overall quality/usefulness score, (c) short justification.
- Define prompt templates for the **conversation-level** eval:
- Option 1 (direct): Provide condensed transcript(s) + final plan(s) and ask for scores on collaboration quality, alignment with goals, and cross-run similarity.
- Option 2 (two-stage): First summarize each transcript, then compare summaries + plans for similarity and alignment.
- Choose a JSON-style response schema (e.g., `{"similarity_score": int, "quality_score": int, "notes": str}`) and ensure prompts instruct the judge to output valid JSON.

4. **Implement `scripts/eval_final_plan_consistency.py` (final-plan eval)**

- Use the shared utilities to:
- Fetch recent/root LangSmith runs for the dual-agent chain.
- Group runs into scenarios and, for each scenario with ≥2 runs, select plan pairs (e.g., canonical reference vs. comparison runs).
- For each pair, call a LangSmith LLM evaluator (e.g., custom `LLMStringEvaluator`) with the final plans and optional user-goals context, using the designed prompt.
- Log results back to LangSmith as an evaluation run (`evaluation_name` like `dual_agents_final_plan_consistency`) and also write a local JSON/CSV summary under `data/evals/` (per-scenario and aggregate stats: mean similarity, quality, etc.).

5. **Implement `scripts/eval_conversation_consistency.py` (conversation + plan eval)**

- Reuse the same run-grouping utilities, but load both **transcript** and **final plan** for each run.
- Optionally, add a summarization step (using a smaller/faster model) to condense each transcript into a short description of the conversation and plan rationale.
- For each scenario with multiple runs, call an LLM evaluator that:
- Compares cross-run behavior (are agents following similar reasoning and structure?),
- Checks that final plans are consistent with the conversations,
- Produces numeric scores and brief natural-language feedback.
- Record results into LangSmith evaluations (e.g., `dual_agents_conversation_consistency`) and a local JSON/CSV artifact.

6. **Wire up simple CLIs and configuration**

- For both eval scripts, provide CLI flags (e.g., `--project`, `--max-runs`, `--judge-model`, `--since`) so you can target specific subsets of runs.
- Ensure they fail fast with clear messages if LangSmith environment variables or required artifacts (like `final_plan.json`) are missing.

7. **Document and validate the eval flow**

- Add a short section to `README.md` or `specs/tasks.md` explaining:
- How to generate a batch of runs (e.g., via `scripts/run_parallel_test.py`).
- How to invoke each eval script and where to see results in LangSmith and on disk.
- Run both eval scripts on a small set of conversations to confirm:
- They correctly find runs and artifacts,
- They produce stable numeric scores,
- The prompts capture your intuitive sense of “similar and consistent outcomes.”

### To-dos

- [ ] Design LLM-judge prompts and JSON output schema for final-plan and conversation-level consistency evaluations.
- [ ] Create shared eval utilities to fetch LangSmith dual-agent runs, locate outputs on disk, and group runs by scenario.
- [ ] Implement scripts/eval_final_plan_consistency.py using LangSmith eval APIs and shared utilities to score final-plan similarity and quality across runs.
- [ ] Implement scripts/eval_conversation_consistency.py to evaluate conversation behavior and plan alignment across runs, optionally via transcript summaries.
- [ ] Run both eval scripts on a small batch of conversations, inspect LangSmith evaluation runs and local artifacts, and adjust prompts/thresholds as needed.