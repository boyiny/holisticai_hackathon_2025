from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    keys = {
        "HOLISTIC_AI_TEAM_ID": os.getenv("HOLISTIC_AI_TEAM_ID"),
        "HOLISTIC_AI_API_TOKEN": os.getenv("HOLISTIC_AI_API_TOKEN"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "LANGSMITH_API_KEY": os.getenv("LANGSMITH_API_KEY"),
    }
    print("Environment readiness:")
    def looks_placeholder(val: str | None) -> bool:
        if not val:
            return False
        v = val.strip().lower()
        return v.startswith("sk-your") or v.endswith("here") or "your-" in v
    for k, v in keys.items():
        status = "set" if v else "missing"
        if looks_placeholder(v):
            status = "placeholder"
        print(f" - {k}: {status}")
    print("\nTip: copy .env.example to .env and fill appropriate keys.")


if __name__ == "__main__":
    main()
