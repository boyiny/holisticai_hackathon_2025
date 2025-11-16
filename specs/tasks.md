1. chaos testing by introducting failures in llm calls, tool calls, network jitters, latency etc.: Prakash:

2. Use Valyu to make the conversation safe and medically correct: Boyin
3. Research on optimization and regulations : Joon
4. use parallel test and llm judge to do eval: Prakash
   - final plan consistency: `python scripts/eval_final_plan_consistency.py --project <langsmith_project> --max-runs 20 --dry-run`
   - conversation consistency: `python scripts/eval_conversation_consistency.py --project <langsmith_project> --max-runs 20 --summary-model gpt-4o-mini --dry-run`

## Performance optimization
Slow run ~300s, 29000 tokens: https://smith.langchain.com/public/5a6c1c09-7812-4721-931b-6c57579fdce8/r

fast run 81s, 9000 tokens: https://smith.langchain.com/public/eac327f8-89b3-4409-9791-0942255e4285/r
