#!/usr/bin/env python
"""Quick smoke test to verify agents initialize correctly."""

import os
import sys

# Set minimal environment variables for testing
os.environ["GOOGLE_API_KEY"] = os.environ.get("GOOGLE_API_KEY", "test-key")
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"
os.environ["LANGFUSE_PUBLIC_KEY"] = "test"
os.environ["LANGFUSE_SECRET_KEY"] = "test"

try:
    print("Testing agent initialization...")
    from app.agents.root import root_agent

    print("✅ Root agent initialized successfully")

    print("\nAgent structure:")
    print(f"- Root: {root_agent.name}")
    for i, agent in enumerate(root_agent.sub_agents):
        print(f"  {i+1}. {agent.name}")
        if hasattr(agent, "sub_agents") and agent.sub_agents:
            for sub in agent.sub_agents:
                print(f"     - {sub.name}")

    print("\n✅ All agents loaded successfully!")
    print("\nYou can now run: poetry run poe web")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
