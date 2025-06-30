#!/usr/bin/env python3
"""Test the Reframe Agent with a realistic social anxiety scenario."""

import json
import time
from typing import Any

import requests


def create_session(base_url: str, session_id: str) -> dict[str, Any]:
    """Create a new session."""
    url = f"{base_url}/apps/reframe_agent/users/test_user/sessions/{session_id}"
    response = requests.post(url, json={"state": {}})
    response.raise_for_status()
    return response.json()


def send_message(base_url: str, session_id: str, message: str) -> list[dict[str, Any]]:
    """Send a message and get response."""
    url = f"{base_url}/run"
    data = {
        "appName": "reframe_agent",
        "userId": "test_user",
        "sessionId": session_id,
        "newMessage": {"role": "user", "parts": [{"text": message}]},
    }
    response = requests.post(url, json=data, timeout=60)
    response.raise_for_status()
    return response.json()


def extract_assistant_messages(events: list[dict[str, Any]]) -> list[str]:
    """Extract assistant messages from events."""
    messages = []
    for event in events:
        if "content" in event and "parts" in event["content"]:
            for part in event["content"]["parts"]:
                if "text" in part and part["text"].strip():
                    # Skip tool calls and continuation messages
                    text = part["text"].strip()
                    if not text.startswith("[Tool Call]") and "Continue processing" not in text:
                        messages.append(text)
    return messages


def main():
    base_url = "http://localhost:8000"
    session_id = f"real_test_{int(time.time())}"

    print("=== REALISTIC SOCIAL ANXIETY SCENARIO TEST ===\n")

    # Create session
    print("Creating session...")
    create_session(base_url, session_id)
    print(f"Session created: {session_id}\n")

    # Conversation flow
    conversation = [
        "I'd like to talk about a difficult social situation I experienced at work.",
        "It happened last week during our team meeting. There were about 10 people in the conference room, including my manager and some senior colleagues I don't know well.",
        "When it was my turn to present my project update, I suddenly felt overwhelmed. My heart started racing, my palms got sweaty, and I felt like everyone was staring at me, judging every word I said. I kept thinking 'They must think I'm incompetent' and 'I'm going to mess this up and look stupid.'",
        "I rushed through my presentation, speaking really fast and quietly. I avoided eye contact and kept my eyes glued to my notes. I even skipped some important points because I just wanted it to be over. My voice was shaking and I could feel my face turning red.",
        "After I finished, my manager asked a clarifying question and I gave a really brief, incomplete answer. The meeting moved on but I spent the rest of it feeling humiliated and angry at myself. Even days later, I keep replaying it in my mind, thinking about all the things I should have said differently.",
    ]

    for _i, message in enumerate(conversation):
        print(f"\n{'='*60}")
        print(f"USER: {message}")
        print(f"{'='*60}")

        # Send message
        events = send_message(base_url, session_id, message)

        # Extract and display responses
        responses = extract_assistant_messages(events)
        for response in responses:
            print(f"\nASSISTANT: {response}")

        # Check if we've moved to next phase
        for event in events:
            author = event.get("author", "")
            if author == "JsonParser":
                print("\n>>> MOVED TO JSON PARSING PHASE")
            elif author == "AnalystLLM":
                print("\n>>> MOVED TO ANALYSIS PHASE")
            elif author == "PdfGenerator":
                print("\n>>> PDF GENERATED!")
                # Extract PDF info if available
                if "content" in event and "parts" in event["content"]:
                    for part in event["content"]["parts"]:
                        if "text" in part and "PDF generated" in part["text"]:
                            print(f"    {part['text']}")

        time.sleep(1)  # Small delay between messages

    # Get final session state
    print(f"\n{'='*60}")
    print("FINAL SESSION STATE")
    print(f"{'='*60}")

    final_url = f"{base_url}/apps/reframe_agent/users/test_user/sessions/{session_id}"
    final_response = requests.get(final_url)
    final_state = final_response.json()

    state = final_state.get("state", {})

    # Show what was collected
    if "parsed" in state:
        print("\n### PARSED INTAKE DATA ###")
        print(json.dumps(state["parsed"], indent=2))

    if "cbt_analysis" in state:
        print("\n### CBT ANALYSIS ###")
        analysis = state["cbt_analysis"]
        print(analysis[:1000] + "..." if len(analysis) > 1000 else analysis)

    if "pdf_output" in state:
        print("\n### PDF OUTPUT ###")
        pdf_info = state["pdf_output"]
        print(f"Filename: {pdf_info.get('pdf_filename')}")
        print(f"Size: {pdf_info.get('pdf_size')} bytes")
        if "url" in pdf_info:
            print(f"URL: {pdf_info['url']}")


if __name__ == "__main__":
    main()
