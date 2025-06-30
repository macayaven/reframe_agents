"""Simple PII-oriented safety filter used as *before_model_callback*.

If the user message contains obvious Personally Identifiable Information (PII)
such as a Social Security Number, the callback flags the event and *escalates*
so that the supervising agent (or human) can decide how to proceed.

Current logic - intentionally minimal for the POC:
    • Detect the literal token ``ssn`` (case-insensitive)
    • Detect bare US SSN numbers in the form ``123-45-6789`` or ``123456789``

When a match is found we:
    1. Set ``callback_context.actions.escalate = True`` so ADK knows the
       message requires manual intervention.
    2. Replace the model request with a short canned response informing the
       user that we cannot process that information.

The canned response is returned as an ``LlmResponse`` object, which short-
circuits the model call (that's the contract of *before_model_callback*).
"""

from __future__ import annotations

import re

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

# ---------------------------------------------------------------------------
# Pre-compiled regexes
# ---------------------------------------------------------------------------

_SSN_REGEXES: list[re.Pattern[str]] = [
    re.compile(r"\bssn\b", re.IGNORECASE),  # literal token
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # 123-45-6789
    re.compile(r"\b\d{9}\b"),  # 123456789
]


class SafetyGuard:
    def __call__(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> LlmResponse | None:  # type: ignore[override]
        # 1. Extract user text for scanning.
        user_content = callback_context.user_content
        if not user_content or not user_content.parts:
            return None  # Nothing to check.

        text_segments: list[str] = []
        for part in user_content.parts:
            if getattr(part, "text", None):
                text_segments.append(part.text)
        combined_text = " ".join(text_segments)

        # 2. Search for PII.
        if not any(regex.search(combined_text) for regex in _SSN_REGEXES):
            return None  # Looks safe - let the model run.

        # 3. Flag and short-circuit - escalate.
        callback_context._event_actions.escalate = True  # pylint: disable=protected-access

        response_text = (
            "I'm sorry, but I cannot help with that. A clinician will review "
            "your last message shortly."
        )

        # Returning LlmResponse causes ADK to skip the model call and use this
        # response instead.
        return LlmResponse(content=types.Content(parts=[types.Part(text=response_text)]))
