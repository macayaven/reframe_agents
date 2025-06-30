# Exit Loop Tool Fix Guide

## Current Implementation Analysis

### What It Does Now
```python
def _exit_loop(tool_context: ToolContext):
    tool_context.actions.escalate = True  # ✅ Correctly signals loop exit
    return {}  # ❌ Returns nothing useful
```

### What It Should Do
1. Extract structured data from the conversation
2. Save that data to session state
3. Signal loop termination

## The Problem

The CollectorLoop gathers information through conversation, but when it's time to exit:
- The tool just signals "escalate" 
- No data is saved to state
- The next agent (Parser) has no structured data to work with

## Solution Options

### Option 1: Pass Data as Parameters (Recommended)
```python
def _exit_loop(
    tool_context: ToolContext,
    trigger_situation: str,
    automatic_thought: str, 
    emotion: str,
    intensity: int
):
    """Exit loop and save collected intake data."""
    # Save to session state
    tool_context.session.state["intake_data"] = {
        "trigger_situation": trigger_situation,
        "automatic_thought": automatic_thought,
        "emotion": emotion,
        "intensity": intensity
    }
    tool_context.session.state["collection_complete"] = True
    
    # Signal loop exit
    tool_context.actions.escalate = True
    
    return {
        "status": "collection_complete",
        "data_saved": True
    }
```

### Option 2: Let LLM Structure the Data
```python
def _exit_loop(
    tool_context: ToolContext,
    collected_data: dict  # Let the LLM provide structured data
):
    """Exit loop and save collected intake data."""
    # Validate required fields
    required = ["trigger_situation", "automatic_thought", "emotion", "intensity"]
    if not all(k in collected_data for k in required):
        return {"error": "Missing required fields"}
    
    # Save to session state
    tool_context.session.state["intake_data"] = collected_data
    tool_context.session.state["collection_complete"] = True
    
    # Signal loop exit
    tool_context.actions.escalate = True
    
    return {"status": "collection_complete"}
```

## Updated Tool Definition

```python
"""Exit loop tool with data collection."""

from google.adk.tools import LongRunningFunctionTool, ToolContext


def _exit_loop(
    tool_context: ToolContext,
    trigger_situation: str,
    automatic_thought: str,
    emotion: str,
    intensity: int
):
    """
    Exit the collection loop after gathering all required information.
    
    Args:
        trigger_situation: The event that triggered the negative feelings
        automatic_thought: The negative thought that arose
        emotion: The primary emotion felt (e.g., "anxiety", "shame")
        intensity: Emotional intensity from 0-10
    """
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    print(f"  [Data Collected] Trigger: {trigger_situation}")
    print(f"  [Data Collected] Thought: {automatic_thought}")
    print(f"  [Data Collected] Emotion: {emotion} (intensity: {intensity})")
    
    # Save collected data to session state
    tool_context.session.state["intake_data"] = {
        "trigger_situation": trigger_situation,
        "automatic_thought": automatic_thought,
        "emotion": emotion,
        "intensity": intensity
    }
    
    # Mark collection as complete
    tool_context.session.state["collection_complete"] = True
    
    # Signal to exit the loop
    tool_context.actions.escalate = True
    
    return {
        "status": "Data collection complete",
        "data_saved": True,
        "next_step": "Parsing conversation transcript"
    }


exit_loop = LongRunningFunctionTool(
    func=_exit_loop,
)
```

## Prompt Update Required

The CollectorLLM prompt must instruct when and how to call the exit tool:

```
When you have collected:
1. A clear description of the triggering situation
2. The specific automatic thought
3. The emotion felt
4. The intensity (0-10)

Call the exit_loop tool with these parameters:
- trigger_situation: "description of what happened"
- automatic_thought: "the exact negative thought"  
- emotion: "the primary emotion"
- intensity: number from 0-10

Example:
exit_loop(
    trigger_situation="Boss criticized my presentation in front of team",
    automatic_thought="Everyone thinks I'm incompetent",
    emotion="shame",
    intensity=8
)
```

## Testing the Fix

```python
# Test that state is properly set
def test_exit_loop_saves_data():
    # Mock context
    mock_context = MockToolContext()
    
    # Call exit_loop
    _exit_loop(
        mock_context,
        trigger_situation="Failed exam",
        automatic_thought="I'm stupid",
        emotion="despair",
        intensity=9
    )
    
    # Verify state was set
    assert mock_context.session.state["intake_data"]["trigger_situation"] == "Failed exam"
    assert mock_context.session.state["collection_complete"] == True
    assert mock_context.actions.escalate == True
```

## Impact on Other Agents

After this fix:
- **Parser**: Can still parse conv_raw for additional context
- **Analysis**: Has structured data in state["intake_data"]
- **PDF**: Has the data it needs in state["intake_data"]

This fix ensures data flows properly through the entire pipeline.