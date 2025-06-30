"""Unit tests for SafetyGuard callback."""

from unittest.mock import MagicMock

from google.genai.types import Content, Part

from app.callbacks.safety_filters import SafetyGuard


def test_safety_guard_safe_message():
    """Test that safe messages pass through."""
    guard = SafetyGuard()

    # Mock context
    ctx = MagicMock()
    ctx.user_content = Content(parts=[Part(text="Hello, I need help with anxiety")])

    # Mock request
    request = MagicMock()

    result = guard(callback_context=ctx, llm_request=request)

    assert result is None  # Should not block


def test_safety_guard_ssn_keyword():
    """Test blocking messages with SSN keyword."""
    guard = SafetyGuard()

    # Mock context
    ctx = MagicMock()
    ctx.user_content = Content(parts=[Part(text="My SSN is 123-45-6789")])
    ctx._event_actions = MagicMock()

    # Mock request
    request = MagicMock()

    result = guard(callback_context=ctx, llm_request=request)

    assert result is not None  # Should return canned response
    assert ctx._event_actions.escalate is True
    response_text = result.content.parts[0].text
    assert "sorry" in response_text
    assert "help with that" in response_text
    assert "clinician will review" in response_text


def test_safety_guard_ssn_pattern_dashes():
    """Test blocking SSN pattern with dashes."""
    guard = SafetyGuard()

    # Mock context
    ctx = MagicMock()
    ctx.user_content = Content(parts=[Part(text="The number is 123-45-6789")])
    ctx._event_actions = MagicMock()

    # Mock request
    request = MagicMock()

    result = guard(callback_context=ctx, llm_request=request)

    assert result is not None
    assert ctx._event_actions.escalate is True


def test_safety_guard_ssn_pattern_no_dashes():
    """Test blocking SSN pattern without dashes."""
    guard = SafetyGuard()

    # Mock context
    ctx = MagicMock()
    ctx.user_content = Content(parts=[Part(text="Number: 123456789")])
    ctx._event_actions = MagicMock()

    # Mock request
    request = MagicMock()

    result = guard(callback_context=ctx, llm_request=request)

    assert result is not None
    assert ctx._event_actions.escalate is True


def test_safety_guard_case_insensitive_ssn():
    """Test SSN keyword detection is case insensitive."""
    guard = SafetyGuard()

    # Mock context
    ctx = MagicMock()
    ctx.user_content = Content(parts=[Part(text="My SsN is hidden")])
    ctx._event_actions = MagicMock()

    # Mock request
    request = MagicMock()

    result = guard(callback_context=ctx, llm_request=request)

    assert result is not None
    assert ctx._event_actions.escalate is True


def test_safety_guard_no_content():
    """Test with no user content."""
    guard = SafetyGuard()

    # Mock context
    ctx = MagicMock()
    ctx.user_content = None

    # Mock request
    request = MagicMock()

    result = guard(callback_context=ctx, llm_request=request)

    assert result is None  # Should not block


def test_safety_guard_empty_parts():
    """Test with empty parts."""
    guard = SafetyGuard()

    # Mock context
    ctx = MagicMock()
    ctx.user_content = Content(parts=[])

    # Mock request
    request = MagicMock()

    result = guard(callback_context=ctx, llm_request=request)

    assert result is None  # Should not block


def test_safety_guard_multiple_parts():
    """Test with multiple parts containing PII."""
    guard = SafetyGuard()

    # Mock context
    ctx = MagicMock()
    ctx.user_content = Content(parts=[Part(text="My social is"), Part(text=" 123-45-6789")])
    ctx._event_actions = MagicMock()

    # Mock request
    request = MagicMock()

    result = guard(callback_context=ctx, llm_request=request)

    assert result is not None
    assert ctx._event_actions.escalate is True
