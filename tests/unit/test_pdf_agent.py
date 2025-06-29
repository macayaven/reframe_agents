import pytest
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part

from app.agents.pdf_agent import PdfAgent


@pytest.mark.asyncio
async def test_pdf_agent_artifact_saved():
    runner = InMemoryRunner(PdfAgent(), app_name="pdf_unit")
    runner.artifact_service = InMemoryArtifactService()

    # Pre-seed minimal state
    sess = await runner.session_service.create_session(
        app_name="pdf_unit", user_id="u", session_id="s"
    )
    sess.state.update(intake_data={}, analysis_output="{}")

    events = await runner.run_async(
        user_id="u",
        session_id="s",
        new_message=Content(parts=[Part(text="")]),
    )

    delta = events[-1].actions.artifact_delta
    assert delta == {"report.pdf": 0}