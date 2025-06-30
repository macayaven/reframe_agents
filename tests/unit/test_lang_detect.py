"""Unit tests for LangDetect callback."""

from unittest.mock import MagicMock

from google.genai.types import Content, Part

from app.callbacks.lang_detect import LangCallback


def test_lang_detect_english():
    """Test language detection for English text."""
    callback = LangCallback()

    # Mock context
    ctx = MagicMock()
    ctx.state = {}
    ctx.user_content = Content(parts=[Part(text="Hello, how are you?")])

    # Mock request
    request = MagicMock()

    result = callback(callback_context=ctx, llm_request=request)

    assert result is None
    assert ctx.state["lang"] == "en"


def test_lang_detect_spanish():
    """Test language detection for Spanish text."""
    callback = LangCallback()

    # Mock context
    ctx = MagicMock()
    ctx.state = {}
    ctx.user_content = Content(parts=[Part(text="¿Cómo estás? Me llamo María.")])

    # Mock request
    request = MagicMock()

    result = callback(callback_context=ctx, llm_request=request)

    assert result is None
    assert ctx.state["lang"] == "es"


def test_lang_detect_already_detected():
    """Test that language detection skips if already detected."""
    callback = LangCallback()

    # Mock context with existing language
    ctx = MagicMock()
    ctx.state = {"lang": "fr"}  # Already detected as French
    ctx.user_content = Content(parts=[Part(text="¿Cómo estás?")])

    # Mock request
    request = MagicMock()

    result = callback(callback_context=ctx, llm_request=request)

    assert result is None
    assert ctx.state["lang"] == "fr"  # Should not change


def test_lang_detect_no_content():
    """Test language detection with no user content."""
    callback = LangCallback()

    # Mock context
    ctx = MagicMock()
    ctx.state = {}
    ctx.user_content = None

    # Mock request
    request = MagicMock()

    result = callback(callback_context=ctx, llm_request=request)

    assert result is None
    assert ctx.state["lang"] == "en"  # Default to English


def test_lang_detect_empty_parts():
    """Test language detection with empty parts."""
    callback = LangCallback()

    # Mock context
    ctx = MagicMock()
    ctx.state = {}
    ctx.user_content = Content(parts=[])

    # Mock request
    request = MagicMock()

    result = callback(callback_context=ctx, llm_request=request)

    assert result is None
    assert ctx.state["lang"] == "en"  # Default to English


def test_lang_detect_multiple_parts():
    """Test language detection with multiple text parts."""
    callback = LangCallback()

    # Mock context
    ctx = MagicMock()
    ctx.state = {}
    ctx.user_content = Content(parts=[Part(text="Hello there"), Part(text=", ¿cómo estás?")])

    # Mock request
    request = MagicMock()

    result = callback(callback_context=ctx, llm_request=request)

    assert result is None
    assert ctx.state["lang"] == "es"  # Spanish characters detected
