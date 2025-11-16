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
   - final plan consistency: `python scripts/eval_final_plan_consistency.py --project <langsmith_project> --max-runs 20 --dry-run`
   - conversation consistency: `python scripts/eval_conversation_consistency.py --project <langsmith_project> --max-runs 20 --summary-model gpt-4o-mini --dry-run`

## Performance optimization
Slow run ~300s, 29000 tokens: https://smith.langchain.com/public/5a6c1c09-7812-4721-931b-6c57579fdce8/r

fast run 81s, 9000 tokens: https://smith.langchain.com/public/eac327f8-89b3-4409-9791-0942255e4285/r
