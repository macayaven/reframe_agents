"""Unit tests for PdfAgent."""

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.pdf_agent import PdfAgent


@pytest.mark.asyncio
async def test_pdf_agent_yields_events():
    """Test that PdfAgent yields events as an async generator."""
    agent = PdfAgent()

    # Mock context
    ctx = AsyncMock()
    ctx.session.state = {"intake_data": {"name": "Test User"}, "analysis_output": "Test analysis"}
    ctx.save_artifact = AsyncMock(return_value="v1")
    ctx.get_artifact_url = AsyncMock(return_value="https://example.com/report.pdf")

    # Mock PDF generation
    with patch("app.agents.pdf_agent.build_pdf_bytes") as mock_build_pdf:
        mock_build_pdf.return_value = b"fake pdf content"

        # Collect events
        events = []
        async for event in agent._produce(ctx):
            events.append(event)

    # Verify we got 1 event
    assert len(events) == 1

    # Check final event
    assert events[0].author == "PdfGenerator"
    assert events[0].content.parts[0].text == "📄 PDF generated: https://example.com/report.pdf"

    # Check state was updated
    assert ctx.session.state["pdf_output"]["pdf_filename"] == "report.pdf"
    assert ctx.session.state["pdf_output"]["version"] == "v1"
    assert ctx.session.state["pdf_output"]["url"] == "https://example.com/report.pdf"


@pytest.mark.asyncio
async def test_pdf_agent_run_async_impl():
    """Test that _run_async_impl properly yields events."""
    agent = PdfAgent()

    # Mock context
    ctx = AsyncMock()
    ctx.session.state = {"intake_data": {}, "analysis_output": ""}
    ctx.save_artifact = AsyncMock(return_value="v1")
    ctx.get_artifact_url = AsyncMock(return_value="https://example.com/report.pdf")

    with patch("app.agents.pdf_agent.build_pdf_bytes", return_value=b"pdf"):
        events = []
        async for event in agent._run_async_impl(ctx):
            events.append(event)

        assert len(events) == 1
