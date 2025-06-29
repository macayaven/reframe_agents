"""Language detection callback for the agents."""

from google.adk.agents.callback_context import CallbackContext
from google.genai import types


def lang_detect(callback_context: CallbackContext) -> types.Content | None:
    """Language detection callback for the agents.
    This is a before agent callback.
    """
    pass
