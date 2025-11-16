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

## Performance optimization
Slow run ~300s, 29000 tokens: https://smith.langchain.com/public/5a6c1c09-7812-4721-931b-6c57579fdce8/r

fast run 81s, 9000 tokens: https://smith.langchain.com/public/eac327f8-89b3-4409-9791-0942255e4285/r
