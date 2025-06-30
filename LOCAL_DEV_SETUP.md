# Local Development Setup Guide

## Quick Start (Minimal Setup)

### 1. Set Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add AT MINIMUM:
# - GOOGLE_API_KEY (required for ADK to work)
# - LANGFUSE_* keys (or the app will crash on startup)
```

### 2. Install Dependencies
```bash
# Using poetry
poetry install

# Or using uv
uv pip install -e .
uv pip install -e .[dev]
```

### 3. Run ADK Web Interface
```bash
poetry run poe web
```

## Current Blockers (Must Fix Before Running)

### ❌ Blocker 1: Missing Prompts
**Problem**: The app fetches prompts from Langfuse but they don't exist.
**Error**: `Failed to download prompt 'intake-agent-adk-instructions'`

**Temporary Fix**: Add to `app/services/prompts/langfuse_cli.py`:
```python
# Add after line 10
FALLBACK_PROMPTS = {
    "intake-agent-adk-instructions": "You are a caring assistant. Help the user identify their automatic thought. Current conversation: ${conv_raw}",
    "intake-parser-agent-adk-instructions": "Extract data from conversation ${conv_raw} and return JSON with: trigger_situation, automatic_thought, emotion, intensity",
    "reframe-agent-adk-instructions": "Analyze the thought in ${parsed} and provide CBT-based reframing.",
}

# Modify _download_prompt method to use fallbacks
```

### ❌ Blocker 2: State Management
**Problem**: Agents don't set required state keys.
**Error**: PDF generates empty because `intake_data` and `analysis_output` are never set.

**See**: `STATE_MANAGEMENT_ANALYSIS.md` for detailed fixes needed.

### ❌ Blocker 3: Exit Loop Tool
**Problem**: CollectorLoop never terminates properly.
**Error**: Conversation loops indefinitely.

**Required Fix**: Update `app/tools/exit_loop.py` to actually set state and signal completion.

## Testing Without External Services

### 1. Disable Langfuse
```python
# In app/services/prompts/langfuse_cli.py
# Add at top of _download_prompt:
if os.getenv("USE_LOCAL_PROMPTS", "false").lower() == "true":
    return FALLBACK_PROMPTS.get(prompt_name, "Default prompt")
```

### 2. Disable GCS Artifacts
```python
# The system already falls back to local storage if GCS fails
# Just ensure GCS_BUCKET_NAME is set to something
```

### 3. Use In-Memory Session Storage
```bash
# Don't set SUPABASE_REFRAME_DB_CONNECTION_STRING
# System will use in-memory storage automatically
```

## Manual Testing Flow

### 1. Start ADK Web
```bash
poetry run poe web
# Should open browser at http://localhost:8080
```

### 2. Expected Conversation Flow
```
Bot: "Hello, I'm here to help you explore your thoughts..."
You: "I felt anxious at work today"
Bot: "Can you tell me more about what happened?"
You: "My boss criticized my work in a meeting"
Bot: "What thoughts went through your mind?"
You: "I thought everyone thinks I'm incompetent"
Bot: "How did that make you feel?"
You: "Ashamed, about 8 out of 10"
[Bot should exit loop here and move to parsing]
```

### 3. Expected Outputs
- Parser should extract structured data
- Analysis should identify cognitive distortions
- PDF should contain all the information

## Common Errors & Solutions

### Error: "No module named 'google.adk'"
**Solution**: Install google-genai-adk package
```bash
poetry add google-genai-adk
```

### Error: "Failed to download prompt"
**Solution**: Implement fallback prompts (see Blocker 1)

### Error: "KeyError: 'intake_data'"
**Solution**: Fix state management (see STATE_MANAGEMENT_ANALYSIS.md)

### Error: "Maximum iterations reached"
**Solution**: Fix exit_loop tool to properly terminate

## Debug Mode

### Enable Detailed Logging
```python
# Add to app/agents/root.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check State Between Agents
```python
# Add to each agent's _produce method:
print(f"State after {self.name}: {ctx.session.state}")
```

## Next Steps After Local Setup Works

1. **Write Integration Tests**
   - Test full conversation flow
   - Test error scenarios
   - Test different languages

2. **Add Production Features**
   - Proper error handling
   - Request validation
   - Rate limiting
   - Monitoring

3. **Deploy to Cloud Run**
   ```bash
   adk deploy cloud_run ./reframe_agent --project YOUR_PROJECT --region us-central1
   ```