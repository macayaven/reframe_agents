"""Safety filters for the agents."""

from google.adk.agents.callback_context import CallbackContext
from google.genai import types


def safety_filters(callback_context: CallbackContext) -> types.Content | None:
    """This is a before agent callback."""
    pass
