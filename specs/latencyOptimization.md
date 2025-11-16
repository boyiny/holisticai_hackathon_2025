<!-- bbf8cba4-383e-431f-a8f4-61aa5b59760f 5b72287c-e51d-4572-afd5-22f580c532ac -->
# Plan: Optimize Dual Agents Latency and Tool Calls

### Goals

- Reduce end-to-end latency of `run_dual_agents` runs (from ~300s to much faster), accepting some quality loss.
- Keep using OpenAI models that support tool calling (e.g., `gpt-5-mini`, `gpt-4o-mini`) with LangGraph ReAct agents.
- Preserve existing behavior: phases, tool usage (Valyu validation + scheduler), telemetry and file outputs.

### 1. Baseline and configuration tightening

- Identify all places where models are selected and configured:
- `longevity/dual_agents.py` (passes `model` into agents).
- `core/react_agent/utils.py` (`load_chat_model` sets temperature, timeout).
- `core/react_agent/context.py` if it has defaults impacting speed.
- Reduce model-level overhead:
- Lower timeouts to a tighter but safe value (e.g., 15–20s) for `ChatOpenAI` and Bedrock where used.
- Reduce default temperature and any max tokens if explicitly set (favor shorter outputs).

### 2. Prompt and phase-level optimization

- Inspect prompts used to build the two agents:
- `longevity/longevity_agents.py` for `advocate_system` and `planner_system` content.
- Make prompts more concise while keeping role separation and safety constraints:
- Remove redundant wording, long examples, and any low-value instructional text.
- Ensure tool-usage instructions are explicit but compact (e.g., “Use `validate_claims` when you assert scientific effects; use `schedule_services` when committing to dates.”).
- Review hints added per phase in `dual_agents.py`:
- Simplify `[phase]` and `[shared_memory]` hints to smaller, more focused instructions to cut prompt token count.

### 3. Conversation and tool strategy adjustments

- Ensure the agents don’t over-talk:
- Add explicit instructions for **short, bullet-point style replies** unless summarizing the final plan.
- Encourage using tools early and concisely instead of long speculative reasoning.
- For phases where tools are rarely needed (e.g., Intake, PlanReview, Revision):
- Clarify prompts so they avoid unnecessary tool calls.
- For tool-heavy phases (PlanDraft, Audit, Scheduling):
- Keep tool instructions but bias towards minimal natural-language narration around tool results.

### 4. Model choice and hybrid strategy (fast path)

- Keep `gpt-5-mini` (or any tool-capable OpenAI model) as the **primary** model, but design for a fast variant:
- Suggest a configuration option to switch to `gpt-4o-mini` or similar for faster runs when acceptable.
- Add a `--small-model` CLI option for future use (even if we initially keep a single model) so the system can:
- Use a faster model for low-stakes phases (Start, Intake, PlanReview, Revision).
- Optionally keep `gpt-5-mini` for FinalPlan / Scheduling if needed later.

### 5. Hard limits on length and steps

- Within the agent configuration (`create_react_agent` / `Context`):
- Set a conservative `max_tokens` / `max_output_tokens` if exposed.
- Limit the number of ReAct tool-calling loops per phase (if configurable) to avoid long tool-think chains.
- Update prompts to explicitly say:
- “Respond in under N sentences unless you are in FinalPlan or FinalSummary.”

### 6. Telemetry-based tuning loop

- Use existing telemetry and LangSmith data to guide tuning:
- Measure per-phase latency before changes and after each optimization batch.
- Compare total tokens per run and latency distributions.
- Iterate on:
- Prompt brevity.
- Temperature and timeout settings.
- Phase-specific behavior (e.g., if a phase is repeatedly slow, tighten its instructions further).

### 7. Safety and regression checks

- Ensure that after optimization:
- Tool calls still occur in the right phases (Valyu for scientific claims, scheduler for appointments).
- Role separation (Advocate vs Planner) remains intact.
- Output files and schemas (`FinalPlan`, telemetry JSON) remain valid.

If you’re happy with this high-level plan, I’ll start by tightening model configuration and prompts (steps 1–3), then run a couple of test conversations and use LangSmith to demonstrate the latency reduction.

### To-dos

- [ ] Review model configuration and timeouts in load_chat_model and Context to lower latency-friendly defaults.
- [ ] Shorten advocate and planner system prompts and per-phase hints while preserving role separation and tool instructions.
- [ ] Adjust prompts to bias toward concise tool usage and minimal narration, especially in tool-heavy phases.
- [ ] Add optional CLI/config support for a faster secondary model for low-stakes phases (without changing current single-model default behavior).
- [ ] Configure shorter outputs and limited ReAct loops where possible to cap per-phase latency.
- [ ] Use LangSmith telemetry to compare latency and tokens before/after changes and refine prompts/settings as needed.
