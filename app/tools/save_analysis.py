"""Save analysis tool for the analysis agent."""

from google.adk.tools import LongRunningFunctionTool, ToolContext


def _save_analysis(tool_context: ToolContext, analysis: str):
    """Save the CBT analysis to state for the PDF generator.

    Args:
        analysis: The complete CBT analysis text
    """
    print(f"  [Tool Call] save_analysis triggered by {tool_context.agent_name}")

    # Access session through _invocation_context
    session = tool_context._invocation_context.session

    # Save the analysis to state
    session.state["cbt_analysis"] = analysis
    print(f"  [Tool Call] Saved CBT analysis to state (length: {len(analysis)})")

    # Also save it as the final analysis for the loop
    session.state["final_analysis"] = analysis

    # Signal that we're done with the analysis loop
    tool_context.actions.escalate = True

    return {"status": "success", "analysis_length": len(analysis)}


save_analysis = LongRunningFunctionTool(
    func=_save_analysis,
)
