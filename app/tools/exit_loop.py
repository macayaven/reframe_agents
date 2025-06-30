"""Exit loop tool."""

from google.adk.tools import LongRunningFunctionTool, ToolContext


def _exit_loop(tool_context: ToolContext):
    """Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end."""
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")

    # Access session through _invocation_context
    session = tool_context._invocation_context.session

    # Save the accumulated transcript to state for the next agent
    # The transcript accumulator callback should have stored the conversation
    if "transcript" in session.state:
        # Ensure the transcript is available for the parser
        session.state["intake_transcript"] = session.state.get("transcript", "")
        print(
            f"  [Tool Call] Saved intake transcript to state (length: {len(session.state['intake_transcript'])})"
        )
    elif "conv_raw" in session.state:
        # Build transcript from conv_raw if transcript not available
        conv_raw = session.state.get("conv_raw", [])
        transcript = "\n".join(
            f"{entry.get('role', 'unknown')}: {entry.get('text', '')}" for entry in conv_raw
        )
        session.state["intake_transcript"] = transcript
        print(f"  [Tool Call] Built intake transcript from conv_raw (length: {len(transcript)})")

    tool_context.actions.escalate = True
    # Return empty dict as tools should typically return JSON-serializable output
    return {}


exit_loop = LongRunningFunctionTool(
    func=_exit_loop,
)
