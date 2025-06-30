# Implementation Plan for Reframe Agents E2E Testing

## Overview
This plan addresses all missing components needed to run a successful end-to-end test with ADK web locally.

## Priority 1: Critical Blockers (Must Fix First)

### 1.1 Prompt Management System
**Problem**: System requires prompts from Langfuse but has no fallback mechanism.

**Tasks**:
1. Create `app/prompts/fallback_prompts.py` with local prompt definitions
2. Update `app/services/prompts/langfuse_cli.py` to:
   - Try Langfuse first
   - Fall back to local prompts if Langfuse fails
   - Add missing prompt to download list
3. Create prompt templates that match expected format

**Files to create/modify**:
- `app/prompts/fallback_prompts.py` (new)
- `app/services/prompts/langfuse_cli.py` (modify)

### 1.2 State Management Flow
**Problem**: Agents don't properly set/read state keys.

**Current State Flow Issues**:
```
CollectorLoop → sets: conv_raw (via TranscriptAccumulator)
             → missing: intake_data

JsonParser → reads: conv_raw (needs to be in instruction)
          → sets: parsed
          → missing: intake_data extraction

AnalysisLoop → reads: parsed (via output_key)
            → missing: sets analysis_output

PdfAgent → reads: intake_data, analysis_output
        → both are missing!
```

**Tasks**:
1. Update CollectorLLM to extract and set `intake_data` when complete
2. Update JsonParser instruction to reference ${conv_raw}
3. Update AnalysisLLM to set `analysis_output`
4. Add state validation in each agent

**Files to modify**:
- `app/agents/collect_llm.py`
- `app/agents/parser.py`
- `app/agents/analysis_llm.py`
- `app/agents/pdf_agent.py`

### 1.3 Exit Loop Tool Implementation
**Problem**: LoopAgents need proper exit mechanism.

**Tasks**:
1. Verify `app/tools/exit_loop.py` properly signals loop termination
2. Update tool to set appropriate state flags
3. Ensure CollectorLLM calls exit_loop when data collection is complete

**Files to check/modify**:
- `app/tools/exit_loop.py`

## Priority 2: Core Functionality

### 2.1 Parser Agent Configuration
**Problem**: Parser doesn't know what to extract or how to read state.

**Tasks**:
1. Create parser prompt that:
   - Reads conversation from ${conv_raw}
   - Extracts: trigger_situation, automatic_thought, emotion, intensity
   - Returns structured JSON
2. Update parser to set both `parsed` and `intake_data` in state

**Files to modify**:
- `app/agents/parser.py`
- `app/prompts/fallback_prompts.py` (parser prompt)

### 2.2 Analysis Agent Output
**Problem**: Analysis agent doesn't set required output.

**Tasks**:
1. Update AnalysisLLM to:
   - Read from state["parsed"]
   - Generate CBT analysis
   - Set state["analysis_output"] with required structure
2. Fix output_key configuration

**Files to modify**:
- `app/agents/analysis_llm.py`
- `app/prompts/fallback_prompts.py` (analysis prompt)

### 2.3 PDF Content Generation
**Problem**: PDF generator expects specific data structure.

**Tasks**:
1. Review `app/tools/pdf_generator.py` expected format
2. Ensure intake_data and analysis_output match expected structure
3. Add error handling for missing data

**Files to modify**:
- `app/tools/pdf_generator.py`

## Priority 3: Testing Infrastructure

### 3.1 Environment Configuration
**Tasks**:
1. Create `.env.example` with all required variables
2. Create `docs/LOCAL_SETUP.md` with setup instructions
3. Add environment validation on startup

**Files to create**:
- `.env.example` (new)
- `docs/LOCAL_SETUP.md` (new)
- `app/config/base.py` (add validation)

### 3.2 Test Data and Fixtures
**Tasks**:
1. Create example conversation fixtures
2. Create integration test scenarios
3. Add mock Langfuse responses for testing

**Files to create**:
- `tests/fixtures/example_conversations.json` (new)
- `tests/fixtures/mock_prompts.json` (new)
- `tests/integration/test_full_workflow.py` (new)

## Priority 4: Error Handling and Robustness

### 4.1 External Service Failures
**Tasks**:
1. Add try/catch for Langfuse prompt fetching
2. Add fallback for GCS artifact storage
3. Add graceful degradation for missing services

**Files to modify**:
- `app/services/prompts/langfuse_cli.py`
- `app/agents/pdf_agent.py`

### 4.2 Callback Fixes
**Tasks**:
1. Fix SafetyGuard to use proper ADK API
2. Add error handling in callbacks
3. Test escalation flow

**Files to modify**:
- `app/callbacks/safety_filters.py`

## Priority 5: Optional Enhancements

### 5.1 Web Search Tool
**Tasks**:
1. Create `app/tools/web_search.py`
2. Add to AnalysisLLM tools
3. Update analysis prompt to use search when needed

**Files to create**:
- `app/tools/web_search.py` (new)

### 5.2 Monitoring and Logging
**Tasks**:
1. Add structured logging
2. Add performance metrics
3. Add health check endpoint

## Implementation Order

1. **Day 1**: Fix prompt system (Priority 1.1)
2. **Day 2**: Fix state management (Priority 1.2, 1.3)
3. **Day 3**: Fix agent configurations (Priority 2.1, 2.2, 2.3)
4. **Day 4**: Add testing infrastructure (Priority 3)
5. **Day 5**: Add error handling (Priority 4)

## Success Criteria

- [ ] `poetry run poe web` launches without errors
- [ ] User can complete full conversation flow
- [ ] PDF is generated with correct content
- [ ] All state transitions work correctly
- [ ] System works without external services (Langfuse, GCS)
- [ ] Integration tests pass

## Testing Checklist

1. **Unit Tests**:
   - [ ] Each agent initializes correctly
   - [ ] State management works
   - [ ] Tools function properly
   - [ ] Callbacks trigger correctly

2. **Integration Tests**:
   - [ ] Full workflow completes
   - [ ] Spanish language detection works
   - [ ] Safety filters trigger appropriately
   - [ ] PDF contains expected content

3. **Manual Testing**:
   - [ ] ADK web UI loads
   - [ ] Conversation flows naturally
   - [ ] Error messages are helpful
   - [ ] PDF download works