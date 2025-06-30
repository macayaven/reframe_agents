# Critical Fixes Required for ADK Web to Function

## 1. Prompt System Fix (HIGHEST PRIORITY)

### Current Problem
The system crashes on startup because it can't fetch prompts from Langfuse:
```python
# In each agent:
instruction=prompt_manager.fetch_prompt(settings.collect_agent_instruction_key)
# This will fail if Langfuse is not configured or prompts don't exist
```

### Required Prompts

#### 1.1 Collector Agent Prompt (`intake-agent-adk-instructions`)
```
You are a trauma-informed intake specialist helping users identify automatic thoughts.

Current conversation: ${conv_raw}

Your task:
1. Warmly greet the user
2. Ask about a recent situation that triggered difficult feelings
3. Identify their automatic thought (what went through their mind)
4. Explore the emotion and its intensity (0-10)
5. When you have all information, call exit_loop tool with the data

Be warm, validating, and use open-ended questions.
```

#### 1.2 Parser Agent Prompt (`intake-parser-agent-adk-instructions`)
```
Extract structured data from the conversation transcript.

Conversation: ${conv_raw}

Return ONLY valid JSON with this structure:
{
  "trigger_situation": "description of the triggering event",
  "automatic_thought": "the negative thought identified",
  "emotion": "primary emotion felt",
  "intensity": 7
}
```

#### 1.3 Analysis Agent Prompt (`reframe-agent-adk-instructions`)
```
You are a CBT therapist analyzing automatic thoughts.

User data: ${parsed}

Your task:
1. Identify cognitive distortions (e.g., MW=Mind Reading, CT=Catastrophizing)
2. Create a balanced alternative thought
3. Suggest a small actionable step (5-10 minutes)
4. Ask user to rate certainty in negative thought before/after

Generate analysis following CBT best practices.
```

### Immediate Fix Required
Create fallback system in `langfuse_cli.py`:
```python
FALLBACK_PROMPTS = {
    "intake-agent-adk-instructions": "...",
    "intake-parser-agent-adk-instructions": "...",
    "reframe-agent-adk-instructions": "...",
}

def _download_prompt(self, prompt_name: str) -> str:
    try:
        # existing code...
    except Exception as e:
        if prompt_name in FALLBACK_PROMPTS:
            return FALLBACK_PROMPTS[prompt_name]
        raise
```

## 2. State Management Fix

### Current State Flow Problems

#### 2.1 CollectorLoop Never Sets intake_data
```python
# Current: Only sets conv_raw via TranscriptAccumulator
# Needed: exit_loop tool must set intake_data
```

#### 2.2 Parser Doesn't Know Input Source
```python
# Current:
instruction=prompt_manager.fetch_prompt(...)  # No ${conv_raw} reference
# Needed: Instruction must reference ${conv_raw}
```

#### 2.3 AnalysisLoop Doesn't Set analysis_output
```python
# Current: No mechanism to save analysis results
# Needed: Must set state["analysis_output"]
```

### Required State Keys
```python
# After CollectorLoop:
state = {
    "conv_raw": [...],  # Set by TranscriptAccumulator
    "intake_data": {    # Must be set by exit_loop tool
        "trigger_situation": "...",
        "automatic_thought": "...",
        "emotion": "...",
        "intensity": 7
    }
}

# After Parser:
state = {
    ...previous,
    "parsed": {  # Set by parser output_key
        "trigger_situation": "...",
        "automatic_thought": "...",
        "emotion": "...",
        "intensity": 7
    }
}

# After AnalysisLoop:
state = {
    ...previous,
    "analysis_output": {  # Must be set somehow
        "distortions": ["MW", "CT"],
        "balanced_thought": "...",
        "micro_action": "...",
        "certainty_before": 8,
        "certainty_after": 4
    }
}
```

## 3. Exit Loop Tool Fix

### Current Implementation Check
```python
# app/tools/exit_loop.py needs to:
1. Extract data from conversation
2. Set state["intake_data"]
3. Signal loop termination
```

## 4. Missing Download in langfuse_cli.py

### Current
```python
required_prompts = [
    "intake-agent-adk-instructions",
    "reframe-agent-adk-instructions",
    "synthesis-agent-adk-instructions",
]
# Missing: "intake-parser-agent-adk-instructions"
```

### Fix
```python
required_prompts = [
    "intake-agent-adk-instructions",
    "intake-parser-agent-adk-instructions",  # ADD THIS
    "reframe-agent-adk-instructions",
    "synthesis-agent-adk-instructions",
]
```

## 5. Quick Test Script

Create `test_local.py`:
```python
import os
os.environ["GOOGLE_API_KEY"] = "your-key"
os.environ["LANGFUSE_HOST"] = "https://langfuse.com"
os.environ["LANGFUSE_PUBLIC_KEY"] = "dummy"
os.environ["LANGFUSE_SECRET_KEY"] = "dummy"

from app.agents.root import root_agent

# Test basic initialization
print("Agents initialized successfully!")
```

## Minimum Viable Fix Steps

1. **Add fallback prompts** to `langfuse_cli.py`
2. **Fix prompt download list** to include parser prompt
3. **Update exit_loop tool** to set intake_data
4. **Create method for AnalysisLoop** to set analysis_output
5. **Add .env.example** with required variables

With these fixes, `poetry run poe web` should at least start without crashing.