#!/usr/bin/env python3
"""Simple client for testing the Reframe Agent API."""

import json
import time
from typing import Any

import requests


class ReframeAgentClient:
    """Client for interacting with the Reframe Agent API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def list_apps(self) -> list:
        """List all available apps."""
        response = self.session.get(f"{self.base_url}/list-apps")
        response.raise_for_status()
        return response.json()

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

    def get_session(self, app_name: str, user_id: str, session_id: str) -> dict[str, Any]:
        """Get session details."""
        url = f"{self.base_url}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def send_message(
        self, app_name: str, user_id: str, session_id: str, message: str, use_sse: bool = False
    ) -> Any:
        """Send a message to the agent."""
        endpoint = "/run_sse" if use_sse else "/run"
        url = f"{self.base_url}{endpoint}"

        data = {
            "appName": app_name,
            "userId": user_id,
            "sessionId": session_id,
            "newMessage": {"role": "user", "parts": [{"text": message}]},
        }

        if use_sse:
            # Handle Server-Sent Events
            response = self.session.post(url, json=data, stream=True)
            response.raise_for_status()

            events = []
            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        try:
                            event_data = json.loads(line[6:])
                            events.append(event_data)
                            print(f"Event: {event_data.get('author', 'unknown')}")
                        except json.JSONDecodeError:
                            pass
            return events
        response = self.session.post(url, json=data)
        response.raise_for_status()
        return response.json()

    def get_trace(self, event_id: str) -> dict[str, Any]:
        """Get trace information for an event."""
        url = f"{self.base_url}/debug/trace/{event_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_session_trace(self, session_id: str) -> dict[str, Any]:
        """Get trace information for a session."""
        url = f"{self.base_url}/debug/trace/session/{session_id}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def delete_session(self, app_name: str, user_id: str, session_id: str) -> None:
        """Delete a session."""
        url = f"{self.base_url}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
        response = self.session.delete(url)
        response.raise_for_status()


def test_reframe_agent():
    """Test the Reframe Agent with a simple flow."""
    client = ReframeAgentClient()

    # Test parameters
    app_name = "reframe_agent"
    user_id = f"test_user_{int(time.time())}"
    session_id = f"test_session_{int(time.time())}"

    print("\n=== Testing Reframe Agent ===")
    print(f"User ID: {user_id}")
    print(f"Session ID: {session_id}")

    try:
        # 1. List apps
        print("\n1. Listing available apps...")
        apps = client.list_apps()
        print(f"Available apps: {apps}")

        # 2. Create session
        print(f"\n2. Creating session for {app_name}...")
        initial_state = {"conversation_stage": "intake", "language": "en", "test_mode": True}
        session = client.create_session(app_name, user_id, session_id, initial_state)
        print(f"Session created: {session['id']}")

        # 3. Send initial message
        print("\n3. Sending initial message...")
        message = "Hello, I'd like to start the intake process."

        try:
            events = client.send_message(app_name, user_id, session_id, message)
            print(f"Received {len(events)} events")

            # Display events
            for i, event in enumerate(events):
                print(f"\nEvent {i+1}:")
                print(f"  Author: {event.get('author', 'unknown')}")
                if "content" in event and "parts" in event["content"]:
                    for part in event["content"]["parts"]:
                        if "text" in part:
                            print(f"  Text: {part['text'][:200]}...")
        except Exception as e:
            print(f"Error sending message: {e}")

            # Try to get debug info
            print("\n4. Getting session trace for debugging...")
            try:
                trace = client.get_session_trace(session_id)
                print(f"Session trace: {json.dumps(trace, indent=2)[:500]}...")
            except Exception as trace_error:
                print(f"Could not get trace: {trace_error}")

        # 5. Get final session state
        print("\n5. Getting final session state...")
        final_session = client.get_session(app_name, user_id, session_id)
        print(f"Final state keys: {list(final_session.get('state', {}).keys())}")

    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup
        try:
            print(f"\n6. Cleaning up - deleting session {session_id}...")
            client.delete_session(app_name, user_id, session_id)
            print("Session deleted successfully")
        except Exception:
            pass


if __name__ == "__main__":
    test_reframe_agent()
