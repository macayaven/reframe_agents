"""Transcript accumulator callback for the agents."""

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse


def transcript_accumulator(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> LlmResponse | None:
    """Transcript accumulator callback for the agents.
    This is an after model callback
    """
    pass
