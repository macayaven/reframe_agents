# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Google ADK-based chat application that collects user context, applies CBT reasoning, and generates PDF reports. The project uses:
- Google ADK 1.5 framework
- Python 3.12+
- uv for dependency management
- Test-Driven Development approach

## Development Setup

### Dependency Management
This project uses `uv` for dependency management. Install dependencies with:
```bash
uv pip install -e .
uv pip install -e .[dev]
```

### Common Commands

**Development servers:**
```bash
poe web        # Launch ADK web UI
poe cli        # Run CLI interface
poe api        # Start API server
```

**Testing:**
```bash
poe test              # Run all tests
poe test-unit         # Run unit tests only
poe test-integration  # Run integration tests only
poe test-cov          # Run tests with coverage report
poe test-watch        # Run tests in watch mode
```

**Code quality:**
```bash
poe lint         # Run ruff linter
poe lint-fix     # Auto-fix linting issues
poe format       # Format code with black
poe format-check # Check formatting without changes
poe type-check   # Run mypy type checking
poe check        # Run all checks (lint, format, type-check, test-cov)
poe fix          # Fix all auto-fixable issues
```

**Deployment:**
```bash
adk deploy cloud_run ./reframe_agent --project <project-id> --region <region>
```

## Architecture

### Agent Pipeline
The application uses a sequential pipeline defined in `app/agents/root.py`:
1. **collector_loop** - Gathers intake data from user
2. **json_parser** - Converts transcript to structured JSON
3. **analysis_loop** - Performs CBT reasoning analysis
4. **PdfAgent** - Generates PDF report and saves artifact

### Key Components
- **Agents**: Located in `app/agents/`, implement Google ADK BaseAgent/LlmAgent/LoopAgent patterns
- **Callbacks**: In `app/callbacks/`, handle language detection, safety filtering, and transcript accumulation
- **Tools**: In `app/tools/`, provide PDF generation and loop control utilities
- **Services**: In `app/services/`, handle persistence (Supabase), tracing (Langfuse), and prompts

### Testing Structure
- Unit tests in `tests/unit/` - test individual components
- Integration tests in `tests/integration/` - test full pipeline flow
- Test configuration in `tests/integration/test_config.json`

## Environment Variables

Required:
- `GOOGLE_API_KEY` - Google AI API key
- `LANGFUSE_HOST` - Langfuse host URL
- `LANGFUSE_PUBLIC_KEY` - Langfuse public key
- `LANGFUSE_SECRET_KEY` - Langfuse secret key

Optional:
- `SUPABASE_REFRAME_DB_CONNECTION_STRING` - For persistent storage
- `ARIZE_SPACE_ID` - Arize monitoring space ID
- `ARIZE_API_KEY` - Arize API key
- `GCS_BUCKET_NAME` - Google Cloud Storage bucket (default: "re-frame")

## Important Implementation Notes

1. **Async Generators**: ADK agents must yield Events, not return coroutines. Use `yield Event(...)` pattern.

2. **Type Annotations**: Silence Pyright warnings with `# type: ignore[attr-defined]` when necessary for ADK-specific attributes.

3. **Session State**: Access via `ctx.session.state` for persisting data across agent calls.

4. **Artifact Storage**: PDFs are saved as artifacts with 120-second signed URLs.

5. **Development Workflow**: Always write tests first (TDD). Every feature must have both unit and integration tests.

## Current Status

The project structure is in place but several components need implementation:
- PdfAgent needs async-generator conversion
- Callbacks (lang_detect, safety_filters, transcript_acc) need implementation
- Integration test dataset needs proper configuration
- Unit tests need to be added for all agents and callbacks