#!/usr/bin/env python3
"""Smart test client that handles LoopAgent continuation messages."""

import json
import time
from typing import Any

import requests


class SmartReframeClient:
    """Smart client that detects and handles loop agent patterns."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_responses = [
            "I had a really difficult experience at work yesterday during our team meeting.",
            "It was our weekly team meeting in the conference room. There were about 8 people there including my manager. We were discussing project updates and upcoming deadlines.",
            "When it was my turn to speak, I started feeling really anxious. My heart was racing and my hands were shaking. I kept thinking 'Everyone is judging me' and 'I'm going to mess this up and look incompetent.'",
            "I spoke really quickly and quietly. I avoided eye contact and kept looking at my notes. I think I even skipped some important points because I just wanted to finish as fast as possible. My voice was shaking.",
            "After I finished, my manager asked a follow-up question and I gave a really brief answer. The meeting moved on but I spent the rest of it feeling embarrassed. Afterwards, I felt exhausted and disappointed in myself. I kept replaying it in my mind thinking about how I could have done better.",
        ]
        self.response_index = 0

    def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        initial_state: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a new session."""
        url = f"{self.base_url}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
        data = {"state": initial_state or {}}
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def send_message(
        self, app_name: str, user_id: str, session_id: str, message: str
    ) -> list[dict[str, Any]]:
        """Send a message and get response events."""
        url = f"{self.base_url}/run"

        data = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {"role": "user", "parts": [{"text": message}]},
        }

        response = self.session.post(url, json=data, timeout=60)
        response.raise_for_status()
        return response.json()

    def extract_messages(self, events: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Extract messages from events with their authors."""
        messages = []
        for event in events:
            author = event.get("author", "unknown")
            if "content" in event and "parts" in event["content"]:
                for part in event["content"]["parts"]:
                    if (
                        "text" in part
                        and part["text"].strip()
                        and not part["text"].startswith("[Tool Call]")
                    ):
                        messages.append({"author": author, "text": part["text"].strip()})
        return messages

    def is_loop_continuation(self, messages: list[dict[str, str]]) -> bool:
        """Check if this is a LoopAgent continuation message."""
        # Look for patterns that indicate loop continuation
        for msg in messages:
            text_lower = msg["text"].lower()
            if any(
                phrase in text_lower
                for phrase in ["continue processing", "exit or provide", "no more outputs"]
            ):
                return True
        return False

    def get_bot_question(self, messages: list[dict[str, str]]) -> str | None:
        """Extract the actual bot question from messages."""
        # Get the last meaningful bot message (not continuation)
        for msg in reversed(messages):
            if msg["author"] in ["CollectorLLM", "AnalystLLM", "JsonParser"]:
                text = msg["text"]
                if not any(
                    phrase in text.lower()
                    for phrase in ["continue processing", "exit or provide", "no more outputs"]
                ):
                    return text
        return None

    def run_test_scenario(self):
        """Run a complete test scenario with smart response handling."""
        # Setup
        app_name = "reframe_agent"
        user_id = f"test_user_{int(time.time())}"
        session_id = f"test_session_{int(time.time())}"

        print(f"\n{'='*60}")
        print("SMART REFRAME AGENT TEST")
        print(f"{'='*60}")
        print(f"Session: {session_id}")
        print(f"User: {user_id}")
        print(f"{'='*60}\n")

        try:
            # Create session
            print("Creating session...")
            self.create_session(
                app_name,
                user_id,
                session_id,
                {"test_mode": True, "scenario": "social_anxiety_work_meeting"},
            )
            print("✓ Session created\n")

            # Initial message
            print("Starting conversation...")
            message = "Hello, I'd like to talk about a challenging social situation."
            print(f"\n🧑 USER: {message}")

            # Track if we've moved past collector
            in_collector = True
            max_exchanges = 20
            exchange_count = 0

            while exchange_count < max_exchanges:
                events = self.send_message(app_name, user_id, session_id, message)
                messages = self.extract_messages(events)

                # Check if we've moved to next agent
                for event in events:
                    author = event.get("author", "")
                    if author == "JsonParser":
                        print("\n✅ Moved to JSON Parser phase")
                        in_collector = False
                    elif author == "AnalystLLM":
                        print("\n✅ Moved to Analysis phase")
                    elif author == "PdfGenerator":
                        print("\n✅ Moved to PDF Generation phase")

                # Check for loop continuation
                if self.is_loop_continuation(messages):
                    # This is a continuation request, provide next response
                    if self.response_index < len(self.test_responses):
                        message = self.test_responses[self.response_index]
                        print(f"\n🧑 USER (providing details): {message}")
                        self.response_index += 1
                    else:
                        # We've provided all responses, just acknowledge
                        message = "I've shared all the details about the situation."
                        print(f"\n🧑 USER: {message}")
                else:
                    # Get bot's actual question/response
                    bot_msg = self.get_bot_question(messages)
                    if bot_msg:
                        print(f"\n🤖 BOT: {bot_msg}")

                        # Determine appropriate response
                        if in_collector and self.response_index < len(self.test_responses):
                            # Provide next detail
                            message = self.test_responses[self.response_index]
                            print(f"\n🧑 USER: {message}")
                            self.response_index += 1
                        else:
                            # Just acknowledge
                            message = "Yes, that's correct."
                            print(f"\n🧑 USER: {message}")

                exchange_count += 1

                # Check if we're done
                if any(event.get("author") == "PdfGenerator" for event in events):
                    print("\n✅ Pipeline completed!")
                    break

                time.sleep(0.5)  # Small delay

            # Get final session state
            final_url = f"{self.base_url}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
            final_response = self.session.get(final_url)
            final_state = final_response.json()

            print(f"\n{'='*60}")
            print("FINAL RESULTS")
            print(f"{'='*60}")

            state = final_state.get("state", {})

            # Check parsed data
            if "parsed" in state:
                print("\n✅ Parsed intake data:")
                print(json.dumps(state["parsed"], indent=2))

            # Check analysis
            if "cbt_analysis" in state or "final_analysis" in state:
                analysis = state.get("cbt_analysis", state.get("final_analysis", ""))
                print(f"\n✅ CBT Analysis (length: {len(analysis)} chars)")
                print(analysis[:500] + "..." if len(analysis) > 500 else analysis)

            # Check PDF
            if "pdf_output" in state:
                pdf_info = state["pdf_output"]
                print("\n✅ PDF Generated:")
                print(f"   Filename: {pdf_info.get('pdf_filename')}")
                print(f"   URL: {pdf_info.get('url')}")

            # Check events for artifacts
            if "events" in final_state:
                for event in final_state["events"]:
                    if event.get("author") == "PdfGenerator":
                        content = event.get("content", {})
                        for part in content.get("parts", []):
                            if "text" in part and "PDF generated" in part["text"]:
                                print(f"\n✅ {part['text']}")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    client = SmartReframeClient()
    client.run_test_scenario()
