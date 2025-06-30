"""Unit tests for TranscriptAccumulator callback."""

from unittest.mock import MagicMock

from google.adk.models.llm_response import LlmResponse
from google.genai.types import Content, Part

from app.callbacks.transcript_acc import TranscriptAccumulator


def test_transcript_accumulator_basic():
    """Test basic transcript accumulation."""
    accumulator = TranscriptAccumulator()

    # Mock context
    ctx = MagicMock()
    ctx.state = {}
    ctx.user_content = Content(parts=[Part(text="Hello, I need help")])

    # Mock response
    response = LlmResponse(content=Content(parts=[Part(text="Hello! I'm here to help you.")]))

    result = accumulator(callback_context=ctx, llm_response=response)

    assert result is None
    assert "conv_raw" in ctx.state
    assert len(ctx.state["conv_raw"]) == 2
    assert ctx.state["conv_raw"][0] == {"role": "user", "text": "Hello, I need help"}
    assert ctx.state["conv_raw"][1] == {"role": "assistant", "text": "Hello! I'm here to help you."}


def test_transcript_accumulator_existing_transcript():
    """Test appending to existing transcript."""
    accumulator = TranscriptAccumulator()

    # Mock context with existing transcript
    ctx = MagicMock()
    ctx.state = {
        "conv_raw": [
            {"role": "user", "text": "First message"},
            {"role": "assistant", "text": "First response"},
        ]
    }
    ctx.user_content = Content(parts=[Part(text="Second message")])

    # Mock response
    response = LlmResponse(content=Content(parts=[Part(text="Second response")]))

    result = accumulator(callback_context=ctx, llm_response=response)

    assert result is None
    assert len(ctx.state["conv_raw"]) == 4
    assert ctx.state["conv_raw"][2] == {"role": "user", "text": "Second message"}
    assert ctx.state["conv_raw"][3] == {"role": "assistant", "text": "Second response"}


def test_transcript_accumulator_no_user_content():
    """Test with no user content."""
    accumulator = TranscriptAccumulator()

    # Mock context
    ctx = MagicMock()
    ctx.state = {}
    ctx.user_content = None

    # Mock response
    response = LlmResponse(content=Content(parts=[Part(text="Response only")]))

    result = accumulator(callback_context=ctx, llm_response=response)

    assert result is None
    assert "conv_raw" in ctx.state
    assert len(ctx.state["conv_raw"]) == 1
    assert ctx.state["conv_raw"][0] == {"role": "assistant", "text": "Response only"}


def test_transcript_accumulator_no_response():
    """Test with no response."""
    accumulator = TranscriptAccumulator()

    # Mock context
    ctx = MagicMock()
    ctx.state = {}
    ctx.user_content = Content(parts=[Part(text="User message only")])

    # Mock response
    response = None

    result = accumulator(callback_context=ctx, llm_response=response)

    assert result is None
    assert "conv_raw" in ctx.state
    assert len(ctx.state["conv_raw"]) == 1
    assert ctx.state["conv_raw"][0] == {"role": "user", "text": "User message only"}


def test_transcript_accumulator_multiple_parts():
    """Test with multiple parts in content."""
    accumulator = TranscriptAccumulator()

    # Mock context
    ctx = MagicMock()
    ctx.state = {}
    ctx.user_content = Content(parts=[Part(text="Part 1"), Part(text=" Part 2")])

    # Mock response with multiple parts
    response = LlmResponse(
        content=Content(parts=[Part(text="Response 1"), Part(text=" Response 2")])
    )

    result = accumulator(callback_context=ctx, llm_response=response)

    assert result is None
    assert "conv_raw" in ctx.state
    assert len(ctx.state["conv_raw"]) == 2
    assert ctx.state["conv_raw"][0] == {"role": "user", "text": "Part 1 Part 2"}
    assert ctx.state["conv_raw"][1] == {"role": "assistant", "text": "Response 1 Response 2"}


def test_transcript_accumulator_empty_text():
    """Test with empty text parts."""
    accumulator = TranscriptAccumulator()

    # Mock context
    ctx = MagicMock()
    ctx.state = {}
    ctx.user_content = Content(parts=[Part(text="")])

    # Mock response
    response = LlmResponse(content=Content(parts=[Part(text="")]))

    result = accumulator(callback_context=ctx, llm_response=response)

    assert result is None
    assert "conv_raw" in ctx.state
    assert len(ctx.state["conv_raw"]) == 0  # Empty text should not be added
