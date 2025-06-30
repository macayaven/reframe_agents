#!/usr/bin/env python3
"""Simple test script to verify the Reframe system works end-to-end."""

import asyncio
import os

from google.adk.context import Context
from google.adk.events import Event
from google.genai.types import Content, Part

# Import the root agent
from app.agents.root import root_agent


async def test_reframe_system():
    """Test the Reframe pipeline with a sample interaction."""

    # Create a test context
    ctx = Context()

    # Create an initial test message
    test_message = Event(
        author="user",
        content=Content(
            parts=[
                Part(
                    text="""I was at a party last night and felt really anxious.
        I kept thinking everyone was judging me and that I didn't belong there.
        I ended up leaving early and felt terrible about myself afterward."""
                )
            ]
        ),
    )

    print("Starting Reframe system test...")
    print(f"Test message: {test_message.content.parts[0].text}")
    print("-" * 80)

    try:
        # Run the root agent
        async for event in root_agent.run(ctx, test_message):
            if event.author and event.content and event.content.parts:
                print(f"\n[{event.author}]:")
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        print(part.text)
                print("-" * 40)

        # Check if PDF was generated
        if hasattr(ctx.session.state, "pdf_output"):
            pdf_info = ctx.session.state["pdf_output"]
            print("\n✅ PDF Generated Successfully!")
            print(f"   Filename: {pdf_info.get('pdf_filename')}")
            print(f"   URL: {pdf_info.get('url')}")
        else:
            print("\n❌ No PDF output found in session state")

    except Exception as e:
        print(f"\n❌ Error during test: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Check for required environment variables
    required_vars = [
        "GOOGLE_API_KEY",
        "LANGFUSE_HOST",
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables and try again.")
    else:
        asyncio.run(test_reframe_system())
