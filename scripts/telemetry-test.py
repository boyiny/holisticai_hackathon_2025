import os
import sys
import time
import uuid
from pathlib import Path
from setup_env import setup_environment

# Add tutorials directory to path for holistic_ai_bedrock import
tutorials_path = Path(__file__).parent.parent / 'tutorials'
if tutorials_path.exists():
    sys.path.insert(0, str(tutorials_path))

from holistic_ai_bedrock import get_chat_model
from langgraph.prebuilt import create_react_agent
from langsmith import Client
import tiktoken

# Set up environment (will load .env, check keys, configure LangSmith)
setup_environment()

# Set up token counting for Claude models
# Claude models use cl100k_base encoding (same as GPT-4)
def count_tokens(text: str) -> int:
    """Count tokens in text using tiktoken (Claude uses cl100k_base encoding)."""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(str(text)))
    except Exception:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        return len(str(text)) // 4

# Create agent with automatic LangSmith tracing
# Use get_chat_model() - uses Holistic AI Bedrock by default (recommended)
llm_traced = get_chat_model("claude-3-5-sonnet")  # Uses Holistic AI Bedrock (recommended)
agent_traced = create_react_agent(llm_traced, tools=[])

langsmith_project = os.getenv('LANGSMITH_PROJECT', 'default')

print("Agent created with automatic LangSmith tracing!")
print(f"  Model: claude-3-5-sonnet (via Bedrock if available)")
print(f"  Project: {langsmith_project}")
print(f"\nEvery agent.invoke() call will be traced to:")
print(f"  https://smith.langchain.com")

if not os.getenv('LANGSMITH_API_KEY'):
    print("\nWARNING: No LangSmith API key found!")
    print("  Tracing will not work without it.")
    print("  Get a free key at: https://smith.langchain.com")

# Generate a unique run ID for tracking
run_id = str(uuid.uuid4())

print(f"Run ID: {run_id}")
print("\nRunning agent...\n")

# Prepare input message
input_message = "Explain Artificial Intelligence in one sentence."
input_tokens = count_tokens(input_message)

# Run the agent with metadata
start_time = time.time()
result = agent_traced.invoke(
    {"messages": [("user", input_message)]},
    {"run_id": run_id, "tags": ["tutorial", "observability"]}
)
elapsed = time.time() - start_time

response = result['messages'][-1].content
output_tokens = count_tokens(str(response))
total_tokens = input_tokens + output_tokens

# Debug: Check if response_metadata is being set correctly
if hasattr(result['messages'][-1], 'response_metadata'):
    print(f"\nDEBUG: response_metadata = {result['messages'][-1].response_metadata}")
else:
    print("\nDEBUG: No response_metadata found on message")

# Check the actual LLM run in LangSmith to see if token usage is there
if os.getenv('LANGSMITH_API_KEY'):
    try:
        ls_client = Client()
        parent_run = ls_client.read_run(run_id)
        print(f"\nDEBUG: Parent run type: {parent_run.run_type}")

        # Find the child LLM run
        if hasattr(parent_run, 'child_runs') and parent_run.child_runs:
            for child_run in parent_run.child_runs:
                if child_run.run_type == 'llm':
                    print(f"DEBUG: Found LLM child run: {child_run.id}")
                    print(f"DEBUG: Child run outputs: {getattr(child_run, 'outputs', 'N/A')}")
                    print(f"DEBUG: Child run extra: {getattr(child_run, 'extra', 'N/A')}")
                    # Check if we can read the full run details
                    try:
                        full_child_run = ls_client.read_run(child_run.id)
                        print(f"DEBUG: Full child run extra: {getattr(full_child_run, 'extra', 'N/A')}")
                        print(f"DEBUG: Full child run outputs: {getattr(full_child_run, 'outputs', 'N/A')}")
                    except Exception as e:
                        print(f"DEBUG: Could not read full child run: {e}")
                    break
    except Exception as e:
        print(f"\nDEBUG: Error checking LangSmith runs: {e}")

print("Response:")
print(f"  {response}")
print(f"\nLatency: {elapsed:.2f}s")
print(f"Tokens: {input_tokens} input + {output_tokens} output = {total_tokens} total")

# Token usage is now automatically included in response_metadata by the model
# LangSmith will read it directly from the LLM run's response_metadata
print("✅ Token usage should now be visible in LangSmith UI")
print("\n" + "="*70)
print("View this trace in LangSmith:")

# Try to get the exact URL
if os.getenv('LANGSMITH_API_KEY'):
    try:
        ls_client = Client()
        run_url = ls_client.read_run(run_id).url
        print(f"  {run_url}")
    except Exception:
        print(f"  https://smith.langchain.com")
        print(f"  Project: {langsmith_project}")
        print(f"  Search for run ID: {run_id}")
else:
    print("  (LangSmith API key not set - tracing disabled)")

print("\nThe trace shows:")
print("  - Full conversation history")
print("  - Token usage breakdown")
print("  - Latency at each step")
print("  - Model parameters used")
