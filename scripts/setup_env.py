"""
Environment setup module for Holistic AI Hackathon projects.

This module provides a convenient way to set up the environment for any Python script
that needs to use Holistic AI Bedrock, OpenAI, LangSmith, and related tools.

Usage:
    from scripts.setup_env import setup_environment

    setup_environment()
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def setup_environment(env_file_path=None, verbose=True):
    """
    Set up the environment for Holistic AI Hackathon projects.

    This function:
    1. Loads environment variables from .env file (if found)
    2. Imports required packages
    3. Checks and validates API keys
    4. Configures LangSmith tracing if available

    Args:
        env_file_path (str or Path, optional): Path to .env file.
            If None, searches for .env in parent directory.
        verbose (bool): Whether to print status messages. Default: True.

    Returns:
        dict: Dictionary with status information about loaded keys and imports.
    """
    status = {
        'holistic_ai_loaded': False,
        'openai_loaded': False,
        'langsmith_loaded': False,
        'holistic_ai_bedrock_imported': False,
        'langgraph_imported': False,
        'monitoring_tools_imported': False
    }

    # ============================================
    # OPTION 1: Set API keys directly (Quick Start)
    # ============================================
    # Uncomment and set your keys here:
    # Recommended: Holistic AI Bedrock
    # os.environ["HOLISTIC_AI_TEAM_ID"] = "your-team-id-here"
    # os.environ["HOLISTIC_AI_API_TOKEN"] = "your-api-token-here"
    # Optional: OpenAI
    # os.environ["OPENAI_API_KEY"] = "your-openai-key-here"
    # os.environ["LANGSMITH_API_KEY"] = "your-langsmith-key-here"  # Required for LangSmith tracing
    # os.environ["LANGSMITH_PROJECT"] = "hackathon-2026"  # Optional
    # os.environ["LANGSMITH_TRACING"] = "true"  # Required for LangGraph tracing
    # os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"  # Optional (default)

    # ============================================
    # OPTION 2: Load from .env file (Recommended)
    # ============================================
    if env_file_path is None:
        # Automatically search for .env file in common locations
        possible_paths = [
            Path(__file__).parent.parent / '.env',  # Project root (most common)
            Path.cwd() / '.env',  # Current working directory
            Path.cwd().parent / '.env',  # Parent of current directory
        ]

        env_path = None
        for path in possible_paths:
            if path.exists():
                env_path = path
                break
    else:
        env_path = Path(env_file_path)
        possible_paths = [env_path]  # For error message consistency

    if env_path and env_path.exists():
        load_dotenv(env_path)
        if verbose:
            print(f"Loaded configuration from .env file: {env_path}")
    else:
        if verbose:
            print("WARNING: No .env file found - using environment variables or hardcoded keys")
            if env_file_path is None:
                print("  Searched locations:")
                for path in possible_paths:
                    print(f"    - {path}")

    # Import official packages
    # Import Holistic AI Bedrock helper function
    # Import from core module
    try:
        # Try to import from tutorials directory (for notebooks)
        tutorials_path = Path(__file__).parent.parent / 'tutorials'
        if tutorials_path.exists():
            sys.path.insert(0, str(tutorials_path))

        from holistic_ai_bedrock import HolisticAIBedrockChat, get_chat_model
        status['holistic_ai_bedrock_imported'] = True
        if verbose:
            print("✅ Holistic AI Bedrock helper function loaded")
    except ImportError:
        if verbose:
            print("⚠️  Could not import holistic_ai_bedrock")

    # Import LangGraph and LangChain components
    try:
        from langgraph.prebuilt import create_react_agent
        from langchain_core.messages import HumanMessage
        from langchain_core.tools import tool
        status['langgraph_imported'] = True
    except ImportError as e:
        if verbose:
            print(f"⚠️  Could not import LangGraph components: {e}")

    # Optional: OpenAI (if not using Bedrock)
    # from langchain_openai import ChatOpenAI

    # Import monitoring tools
    try:
        import tiktoken
        from codecarbon import EmissionsTracker
        from langsmith import Client
        status['monitoring_tools_imported'] = True
    except ImportError as e:
        if verbose:
            print(f"⚠️  Could not import monitoring tools: {e}")

    # Check API keys (Holistic AI Bedrock recommended, OpenAI optional)
    # Check Holistic AI Bedrock (recommended)
    if os.getenv('HOLISTIC_AI_TEAM_ID') and os.getenv('HOLISTIC_AI_API_TOKEN'):
        status['holistic_ai_loaded'] = True
        if verbose:
            print("✅ Holistic AI Bedrock credentials loaded (will use Bedrock)")

    # Check OpenAI (optional)
    if os.getenv('OPENAI_API_KEY'):
        status['openai_loaded'] = True
        if verbose:
            key_preview = os.getenv('OPENAI_API_KEY')[:10] + "..."
            print(f"OpenAI API key loaded: {key_preview}")
    else:
        if verbose:
            print("ℹ️  OpenAI API key not found - optional, will use Bedrock if available")

    # Check LangSmith API key (required for this tutorial)
    if os.getenv('LANGSMITH_API_KEY'):
        status['langsmith_loaded'] = True
        if verbose:
            ls_key = os.getenv('LANGSMITH_API_KEY')[:10] + "..."
            print(f"LangSmith API key loaded: {ls_key}")

        # Set required LangGraph tracing environment variables if not already set
        if not os.getenv('LANGSMITH_TRACING'):
            os.environ['LANGSMITH_TRACING'] = 'true'
            if verbose:
                print("  LANGSMITH_TRACING set to 'true' (required for LangGraph tracing)")

        if not os.getenv('LANGSMITH_ENDPOINT'):
            os.environ['LANGSMITH_ENDPOINT'] = 'https://api.smith.langchain.com'
            if verbose:
                print("  LANGSMITH_ENDPOINT set to 'https://api.smith.langchain.com'")

        langsmith_project = os.getenv('LANGSMITH_PROJECT', 'default')
        if verbose:
            print(f"  LangSmith project: {langsmith_project}")
            print("  LangSmith tracing will be fully functional!")
    else:
        if verbose:
            print("ERROR: LangSmith API key not found - tracing will not work!")
            print("  Get a free key at: https://smith.langchain.com")
            print("  This tutorial requires LangSmith to function properly!")

    if verbose:
        print("\nAll imports successful!")

    return status


# Make commonly used imports available at module level for convenience
def get_imports():
    """
    Get commonly used imports after setup_environment() has been called.

    Returns:
        dict: Dictionary with imported modules and functions.
    """
    imports = {}

    try:
        from holistic_ai_bedrock import HolisticAIBedrockChat, get_chat_model
        imports['HolisticAIBedrockChat'] = HolisticAIBedrockChat
        imports['get_chat_model'] = get_chat_model
    except ImportError:
        pass

    try:
        from langgraph.prebuilt import create_react_agent
        from langchain_core.messages import HumanMessage
        from langchain_core.tools import tool
        imports['create_react_agent'] = create_react_agent
        imports['HumanMessage'] = HumanMessage
        imports['tool'] = tool
    except ImportError:
        pass

    try:
        import tiktoken
        from codecarbon import EmissionsTracker
        from langsmith import Client
        imports['tiktoken'] = tiktoken
        imports['EmissionsTracker'] = EmissionsTracker
        imports['Client'] = Client
    except ImportError:
        pass

    return imports



if __name__ == "__main__":
    # Run setup when executed directly
    setup_environment()

