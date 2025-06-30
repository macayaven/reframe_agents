#!/usr/bin/env python3
"""Interactive test client for the Reframe Agent API with predefined test scenario."""

import json
import time
from typing import Any

import requests


class InteractiveReframeClient:
    """Interactive client for testing the Reframe Agent with a full conversation flow."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.conversation_history = []

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

        response = self.session.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()

    def extract_bot_message(self, events: list[dict[str, Any]]) -> str:
        """Extract the bot's message from events."""
        messages = []
        for event in events:
            if "content" in event and "parts" in event["content"]:
                for part in event["content"]["parts"]:
                    if (
                        "text" in part
                        and part["text"].strip()
                        and not part["text"].startswith("[Tool Call]")
                    ):
                        messages.append(part["text"].strip())
        return "\n".join(messages)

    def run_test_scenario(self):
        """Run a complete test scenario with a predefined conversation."""
        # Test scenario - social anxiety at work meeting
        test_responses = [
            "I had a really difficult experience at work yesterday during our team meeting.",
            "It was our weekly team meeting in the conference room. There were about 8 people there including my manager. We were discussing project updates and upcoming deadlines.",
            "When it was my turn to speak, I started feeling really anxious. My heart was racing and my hands were shaking. I kept thinking 'Everyone is judging me' and 'I'm going to mess this up and look incompetent.'",
            "I spoke really quickly and quietly. I avoided eye contact and kept looking at my notes. I think I even skipped some important points because I just wanted to finish as fast as possible. My voice was shaking.",
            "After I finished, my manager asked a follow-up question and I gave a really brief answer. The meeting moved on but I spent the rest of it feeling embarrassed. Afterwards, I felt exhausted and disappointed in myself. I kept replaying it in my mind thinking about how I could have done better.",
        ]

        # Setup
        app_name = "reframe_agent"
        user_id = f"test_user_{int(time.time())}"
        session_id = f"test_session_{int(time.time())}"

        print(f"\n{'='*60}")
        print("REFRAME AGENT TEST SCENARIO")
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

            events = self.send_message(app_name, user_id, session_id, message)
            bot_response = self.extract_bot_message(events)
            print(f"\n🤖 BOT: {bot_response}")

            # Continue with test responses
            response_index = 0
            max_exchanges = 10  # Prevent infinite loops
            exchange_count = 0

            while response_index < len(test_responses) and exchange_count < max_exchanges:
                time.sleep(1)  # Small delay to simulate real conversation

                user_message = test_responses[response_index]
                print(f"\n🧑 USER: {user_message}")

                events = self.send_message(app_name, user_id, session_id, user_message)
                bot_response = self.extract_bot_message(events)

                if bot_response:
                    print(f"\n🤖 BOT: {bot_response}")

                    # Check if bot is asking for more information
                    if any(
                        word in bot_response.lower()
                        for word in ["tell me", "describe", "what", "how", "more"]
                    ):
                        response_index += 1
                    else:
                        # Bot might be processing, wait for next prompt
                        pass

                exchange_count += 1

                # Check if we've completed the intake
                if any(event.get("author") == "JsonParser" for event in events):
                    print("\n✓ Intake completed, moving to parsing phase...")
                    break

            # Check final session state
            final_url = f"{self.base_url}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
            final_response = self.session.get(final_url)
            final_state = final_response.json()

            print(f"\n{'='*60}")
            print("FINAL SESSION STATE")
            print(f"{'='*60}")
            print(f"State keys: {list(final_state.get('state', {}).keys())}")

            if "parsed" in final_state.get("state", {}):
                print("\n✓ Successfully parsed intake data:")
                print(json.dumps(final_state["state"]["parsed"], indent=2))

            if "analysis" in final_state.get("state", {}):
                print("\n✓ Successfully analyzed with CBT framework:")
                print(json.dumps(final_state["state"]["analysis"], indent=2))

            # Check for artifacts (PDF)
            if "events" in final_state:
                for event in final_state["events"]:
                    if "artifactDelta" in event.get("actions", {}):
                        artifacts = event["actions"]["artifactDelta"]
                        if artifacts:
                            print("\n✓ PDF artifact generated:")
                            print(json.dumps(artifacts, indent=2))

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback

            traceback.print_exc()

            # Try to get debug info
            try:
                trace_url = f"{self.base_url}/debug/trace/session/{session_id}"
                trace = self.session.get(trace_url).json()
                print("\nDebug trace (last 5 events):")
                for event in trace[-5:]:
                    print(
                        f"  - {event.get('name', 'unknown')}: {event.get('attributes', {}).get('error.type', 'OK')}"
                    )
            except Exception:
                pass


if __name__ == "__main__":
    client = InteractiveReframeClient()
    client.run_test_scenario()
