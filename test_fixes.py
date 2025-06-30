#!/usr/bin/env python3
"""Test script to verify the fixes for the ADK issues."""

import asyncio
import os

from google.adk.context import Context
from google.adk.events import Event
from google.genai.types import Content, Part

from app.agents.analysis_llm import analyst_llm

# Import the agents
from app.agents.collect_llm import collector_llm
from app.agents.parser import json_parser
from app.agents.root import root_agent


async def test_individual_agents():
    """Test individual agents to diagnose issues."""

    # Create a test context
    ctx = Context()

    print("=" * 80)
    print("TESTING INDIVIDUAL AGENTS")
    print("=" * 80)

    # Test 1: Collector Agent
    print("\n1. Testing Collector Agent")
    print("-" * 40)

    # Simulate a conversation
    test_messages = [
        "I want to talk about a difficult social situation",
        "I was at a work meeting yesterday and felt really anxious when I had to present",
        "I kept thinking that everyone was judging me and that I would mess up. I felt my heart racing and my palms were sweaty",
        "I rushed through my presentation and avoided eye contact. I didn't answer questions well",
        "After the meeting, I felt terrible and kept replaying it in my mind, thinking I had embarrassed myself",
    ]

    for i, msg in enumerate(test_messages):
        print(f"\nUser message {i+1}: {msg}")
        user_event = Event(author="user", content=Content(parts=[Part(text=msg)]))

        async for event in collector_llm.run(ctx, user_event):
            if event.author and event.content and event.content.parts:
                print(f"[{event.author}]: {event.content.parts[0].text[:200]}...")

        # Check state
        conv_raw = ctx.session.state.get("conv_raw", [])
        print(f"Conversation entries: {len(conv_raw)}")

    # Check if transcript was saved
    intake_transcript = ctx.session.state.get("intake_transcript", "")
    print(f"\nIntake transcript saved: {len(intake_transcript)} chars")

    # Test 2: Parser Agent
    print("\n\n2. Testing Parser Agent")
    print("-" * 40)

    parser_event = Event(
        author="system", content=Content(parts=[Part(text="Parse the transcript")])
    )
    async for event in json_parser.run(ctx, parser_event):
        if event.author and event.content and event.content.parts:
            print(f"[{event.author}]: {event.content.parts[0].text[:500]}...")

    parsed_data = ctx.session.state.get("parsed", {})
    print(f"\nParsed data keys: {list(parsed_data.keys())}")

    # Test 3: Analysis Agent
    print("\n\n3. Testing Analysis Agent")
    print("-" * 40)

    analysis_event = Event(author="system", content=Content(parts=[Part(text="Analyze the data")]))
    async for event in analyst_llm.run(ctx, analysis_event):
        if event.author and event.content and event.content.parts:
            print(f"[{event.author}]: {event.content.parts[0].text[:500]}...")

    cbt_analysis = ctx.session.state.get("cbt_analysis", "")
    print(f"\nCBT analysis saved: {len(cbt_analysis)} chars")


async def test_full_pipeline():
    """Test the full pipeline with a simple message."""

    print("\n" + "=" * 80)
    print("TESTING FULL PIPELINE")
    print("=" * 80)

    ctx = Context()

    # Simple initial message
    test_message = Event(
        author="user", content=Content(parts=[Part(text="I need help with social anxiety")])
    )

    print(f"\nInitial message: {test_message.content.parts[0].text}")
    print("-" * 40)

    try:
        event_count = 0
        async for event in root_agent.run(ctx, test_message):
            event_count += 1
            if event.author and event.content and event.content.parts:
                text = event.content.parts[0].text
                print(f"\n[Event {event_count}] {event.author}: {text[:200]}...")

                # If it's a question from the bot, provide a response
                if event.author == "CollectorLLM" and "?" in text and event_count < 10:
                    # Simulate user responses
                    responses = {
                        1: "I was at a party last night",
                        2: "I felt really anxious and thought everyone was judging me",
                        3: "I kept to myself and left early",
                        4: "I felt terrible and lonely afterward",
                    }

                    if event_count in responses:
                        user_response = Event(
                            author="user",
                            content=Content(parts=[Part(text=responses[event_count])]),
                        )
                        print(f"\n[User Response]: {responses[event_count]}")

                        # Continue the pipeline with user response
                        async for next_event in root_agent.run(ctx, user_response):
                            event_count += 1
                            if (
                                next_event.author
                                and next_event.content
                                and next_event.content.parts
                            ):
                                text = next_event.content.parts[0].text
                                print(
                                    f"\n[Event {event_count}] {next_event.author}: {text[:200]}..."
                                )

        # Check final state
        print("\n" + "=" * 40)
        print("FINAL STATE CHECK:")
        print(f"- Conversation entries: {len(ctx.session.state.get('conv_raw', []))}")
        print(f"- Intake transcript: {len(ctx.session.state.get('intake_transcript', ''))} chars")
        print(f"- Parsed data: {list(ctx.session.state.get('parsed', {}).keys())}")
        print(f"- CBT analysis: {len(ctx.session.state.get('cbt_analysis', ''))} chars")
        print(f"- PDF output: {'Yes' if 'pdf_output' in ctx.session.state else 'No'}")

    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
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
        print("Running tests...")
        asyncio.run(test_individual_agents())
        # asyncio.run(test_full_pipeline())
