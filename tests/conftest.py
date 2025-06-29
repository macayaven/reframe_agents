from collections import deque

from google.adk.artifacts import InMemoryArtifactService
from google.adk.models import BaseLlm  # <- for StubLLM typing
from google.genai.types import Content, Part
import pytest


##############################################################################
# Simple stub that replaces any LlmAgent's model with deterministic replies. #
##############################################################################
class StubLLM(BaseLlm):
    """Deterministic stand-in for any Gemini / GPT model used in tests."""

    def __init__(self, canned: deque[str]):
        super().__init__(model="stub")  # parent ctor expects a model name
        self._answers = canned

    async def generate_content_async(self, *_, **__):
        text = self._answers.popleft() if self._answers else "stub-reply"
        return Content(parts=[Part(text=text)], role="model")


@pytest.fixture(scope="session")
def artifact_service():
    """Artifact service for tests."""
    return InMemoryArtifactService()
