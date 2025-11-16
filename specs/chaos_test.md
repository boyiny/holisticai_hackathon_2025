<!-- bbf8cba4-383e-431f-a8f4-61aa5b59760f b97daf40-e9da-4557-83cf-16ccb716ef54 -->
# Plan: Chaos / Robustness / Reliability Testing for Dual-Agent Workflow

### Goals
- Systematically stress the dual-agent longevity workflow under **LLM failures, tool failures, and network jitter/latency**.
- Keep each test **separate** with its own configuration, run script, and JSON report under `data/tests/`.
- Prioritize tests that directly demonstrate **robustness** to outages and slowness in LLMs and tools (Valyu validator + scheduler).

---

## 1. Testing Infrastructure & Conventions

1. **Central chaos layer (already present)**
   - Reuse `longevity/chaos_layer.py` and extend/configure it as the single place to simulate:
     - Network jitter & timeouts: `apply_network_chaos()`
     - Tool-level failures & bad responses: `apply_tool_chaos()`
   - Drive it via env vars (`CHAOS_MODE`, `CHAOS_JITTER_MIN_MS`, `CHAOS_JITTER_MAX_MS`, `CHAOS_NET_FAIL_PROB`, `CHAOS_TOOL_FAIL_PROB`).

2. **Where to hook chaos in the code (no behavior change when disabled)**
   - LLM calls:
     - `longevity/utils.py::call_llm` and LangGraph-based agents in `core/react_agent/create_agent.py`.
     - Wrap model invocation with optional `apply_network_chaos()` before the call.
   - Valyu validator:
     - `longevity/valyu_validation.py::validate_claims`.
     - Before doing HTTP POST, call `apply_network_chaos()` and `apply_tool_chaos()` so tests can simulate slow/failed Valyu.
   - Scheduler / tools:
     - `longevity/tools.py::tool_schedule_services` and `longevity/tools_langchain.py::ScheduleTool._run`.
     - Call `apply_tool_chaos()` before booking slots to simulate scheduler failures.

3. **Result storage convention**
   - All chaos/robustness tests write JSON reports under `data/tests/` using a common pattern:
     - `chaos_<component>_<scenario>_<YYYYMMDD_HHMMSS>.json`.
   - Each report contains:
     - `summary`: high-level metrics (success rate, mean / p95 latency, error counts by type).
     - `runs`: one entry per conversation/test-run with fields like `run_id`, `scenario_id`, `success`, `errors`, `latency_ms`, `tokens_total`.
   - Make reports intentionally similar to `scripts/run_parallel_test.py` output for consistency.

4. **Execution pattern**
   - Use dedicated scripts under `scripts/` for each chaos scenario, e.g.:
     - `scripts/run_chaos_llm.py`
     - `scripts/run_chaos_tools.py`
     - `scripts/run_chaos_network.py`
   - Each script:
     - Accepts CLI flags for `--num-runs`, `--concurrency`, `--turn-limit`, `--model`, `--small-model`.
     - Sets chaos env vars (or expects them from the shell) and then internally calls either `run_dual_agents` or `run_parallel`.

---

## 2. High-Priority LLM Chaos Tests

### 2.1 LLM Timeout & Slow-Response Resilience

- **Objective**: Show that long or timed‑out LLM calls do not crash the workflow and that latency remains bounded when we inject jitter.
- **Injection**:
  - In `call_llm` and `create_react_agent` graph `call_model` node, call `apply_network_chaos()` right before `llm.invoke`.
  - Configure env for the test run:
    - `CHAOS_MODE=1`
    - `CHAOS_JITTER_MIN_MS=2000`, `CHAOS_JITTER_MAX_MS=8000` (simulate very slow responses).
    - `CHAOS_NET_FAIL_PROB=0.1` (10% of LLM calls raise `ChaosNetworkError`).
- **Test script**:
  - `scripts/run_chaos_llm_slow.py` using `run_parallel` or multiple `run_dual_agents` calls.
  - Run e.g. 20 conversations with `turn_limit=6`.
- **Metrics in report**:
  - Fraction of runs that still complete (`success_rate`).
  - Distribution of total conversation latency (p50, p95).
  - Count and sample of recovered LLM failures vs. fatal ones.
- **Expected robustness**:
  - Workflow logs clear errors when a step fails due to LLM timeout.
  - No unhandled exceptions; `success` is `False` but process exits cleanly.

### 2.2 LLM Random Failure / Bad Output Handling

- **Objective**: Ensure the system behaves sensibly when the LLM returns malformed or empty responses.
- **Injection**:
  - Extend chaos layer or a small wrapper around LLM that, with some probability, returns:
    - An empty string.
    - A string that is not valid JSON when structured output is expected.
  - Use a separate env flag, e.g. `CHAOS_LLM_BAD_OUTPUT_PROB`.
- **Test script**:
  - `scripts/run_chaos_llm_bad_output.py`.
  - During validation phases (`FinalPlan`, `FinalSummary`), capture how often JSON parsing fails and how the system falls back (e.g. `final_plan` remains `null` but conversation/telemetry still saved).
- **Metrics**:
  - Number of bad outputs per run.
  - Impact on `final_plan` production.
  - Presence of clear error messages in telemetry.

---

## 3. High-Priority Tool Chaos Tests (Valyu + Scheduler)

### 3.1 Valyu Endpoint Down / Erroring

- **Objective**: Validate that when `--valyu-url` is slow or erroring, the conversation still finishes and marks claims as `server_unavailable` without crashing.
- **Injection**:
  - In `valyu_validation.validate_claims`, call `apply_network_chaos()` and `apply_tool_chaos()` before the main POST.
  - For this test, set env:
    - `CHAOS_MODE=1`
    - `CHAOS_NET_FAIL_PROB=0.3` (30% network failures).
    - `CHAOS_TOOL_FAIL_PROB=0.3` (simulate HTTP 500 / malformed responses).
- **Test script**:
  - `scripts/run_chaos_valyu_down.py` (can wrap `run_parallel` in `baseline` or `optimized` mode).
- **Metrics & report fields**:
  - Count of validations attempted vs. successful.
  - Fraction of validations with `server_unavailable=true`.
  - Whether `plan_summary` still includes warnings like “Evidence-uncertain items present…”.
  - Ensure no unhandled exceptions from Valyu failures.

### 3.2 Scheduler Tool Failures

- **Objective**: Ensure that scheduler failures cause clear messaging (e.g., fallback “call clinic to book”) rather than silent failures.
- **Injection**:
  - In `tool_schedule_services` and/or `ScheduleTool._run`, call `apply_tool_chaos()` before `book_slot`.
  - Configure chaos to a high tool failure rate (e.g. `CHAOS_TOOL_FAIL_PROB=0.5`).
- **Test script**:
  - `scripts/run_chaos_scheduler_failures.py`.
- **Metrics**:
  - Number of attempted bookings vs. successful bookings per run.
  - Presence of fallback messaging in transcript or summary.
  - Impact on final plan (e.g. fewer appointments but explicit warnings instead of silent drops).

---

## 4. Network Jitter / Latency Scenarios

### 4.1 Moderate Jitter Across All External Calls

- **Objective**: Show that moderate jitter (hundreds of ms) does not significantly degrade overall latency beyond expected bounds.
- **Injection**:
  - Enable `CHAOS_MODE` with `CHAOS_JITTER_MIN_MS=100`, `CHAOS_JITTER_MAX_MS=500` and zero failure probabilities.
  - Use both `call_llm` and Valyu/scheduler chaos hooks.
- **Test script**:
  - `scripts/run_chaos_network_jitter.py` using `run_parallel` to measure aggregate p50/p95.
- **Metrics**:
  - Compare p50 / p95 latency vs. non-chaos baseline (from prior runs).
  - Verify that success rate remains ~1.0 and plans remain deterministic.

### 4.2 Heavy Jitter with Small-Model Fallback

- **Objective**: Validate the benefit of the `--small-model` fast path under high latency conditions.
- **Injection**:
  - Same as above but with `CHAOS_JITTER_MIN_MS=500`, `MAX_MS=2000`.
  - Run two variants:
    - A: `--small-model` not set.
    - B: `--small-model gpt-4o-mini` (or another faster model) with main model set to a heavier one.
- **Test script**:
  - `scripts/run_chaos_network_small_model_comparison.py` that runs both variants and writes a single JSON with two summaries.
- **Metrics**:
  - Compare latency distributions and success rates between A and B.
  - Demonstrate that the hybrid model architecture mitigates the slowdown.

---

## 5. Combined Failure Scenarios (Tier-2 Priority)

### 5.1 LLM Failures + Valyu Down

- **Objective**: Stress the workflow when both the LLM and Valyu are unreliable simultaneously.
- **Scenario**:
  - `CHAOS_NET_FAIL_PROB=0.2`, `CHAOS_TOOL_FAIL_PROB=0.4`, jitter 100–1000ms.
  - Run fewer conversations (e.g. 10) to keep cost manageable.
- **Test script**:
  - `scripts/run_chaos_combined_llm_valyu.py`.
- **Metrics**:
  - Overall success rate and error types.
  - How often both LLM and tools fail in the same run.
  - Ensure conversation/summary files still get written and index updated.

### 5.2 Scheduler Failures + High Concurrency

- **Objective**: Verify that concurrent runs under scheduler chaos do not corrupt shared files or produce cross-run contamination.
- **Scenario**:
  - Use `scripts/run_parallel_test.py` with `CHAOS_TOOL_FAIL_PROB=0.5` and `concurrency` ~ 10–20.
- **Metrics**:
  - Confirm that `outputs_dir` and `run_index.json` are correct per run.
  - No errors about file locking or JSON parse errors from partially written files.

---

## 6. Reporting & How to Prioritize Tests

### 6.1 Test prioritization

1. **P0 (must-have before demo)**
   - LLM slow/timeout resilience (2.1).
   - Valyu endpoint down/erroring (3.1).
   - Scheduler tool failures (3.2).
2. **P1 (strong robustness story)**
   - Moderate network jitter (4.1).
   - Combined LLM + Valyu failures (5.1).
3. **P2 (nice-to-have / extra credit)**
   - Heavy jitter + small-model comparison (4.2).
   - Scheduler failures + high concurrency (5.2).

### 6.2 Making results easy to read

- Each chaos script prints a short **summary** to stdout and writes a detailed JSON under `data/tests/`.
- Optionally add a lightweight CLI viewer, e.g. `scripts/overview.py` extended to show:
  - Latest chaos tests.
  - For each test: scenario name, success rate, p95 latency, and a “robustness verdict” (pass/fail based on thresholds).
- Use LangSmith project tags/metadata (e.g. `metadata.scenario = "chaos_llm_slow"`) so you can click from a chaos report JSON to the corresponding traces.

This plan keeps all actual chaos logic centralized and minimal, while giving you a portfolio of focused tests whose results are easy to compare and present to judges or reviewers.