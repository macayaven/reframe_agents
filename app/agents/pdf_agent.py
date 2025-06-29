"""PdfAgent – deterministic final step that builds a PDF and saves it as an artifact."""
from typing import Any

from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.genai.types import Part, Blob, Content

from app.tools.pdf_generator import build_pdf_bytes


class PdfAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="PdfGenerator", description="Generates the final PDF report")

    # ------------------------------------------------------------------ #
    # ADK ≥ 1.5 requires these two coroutines (NOT generators).          #
    # They both call the same _produce helper and RETURN a dict.         #
    # ADK wraps that dict into an agent_output Event automatically.      #
    # ------------------------------------------------------------------ #
    async def _run_async_impl(self, ctx) -> Any:      # ctx is InvocationContext
        return await self._produce(ctx)

    async def _run_live_impl(self, ctx) -> Any:
        return await self._produce(ctx)

    # ---------------------- helper ------------------------------------ #
    async def _produce(self, ctx):
        # Get session-level state
        state = ctx.session.state

        pdf_bytes = build_pdf_bytes(
            intake_data=state.get("intake_data", {}),
            analysis_output=state.get("analysis_output", ""),
        )

        # Wrap bytes as a Part for save_artifact
        artifact_part = Part(
            inline_data=Blob(data=pdf_bytes, mime_type="application/pdf")
        )
        filename = "report.pdf"
        version = await ctx.save_artifact(filename=filename, artifact=artifact_part)

        url = await ctx.get_artifact_url(
            filename=filename,
            version=version,
            expiry_seconds=120,      # 2-minute signed link
        )

        # Log a simple assistant message so the trace isn’t empty
        await ctx.emit_event(  # helper → appends immediately
            Event(
                author=self.name,
                content=Content(parts=[Part(text="📄 PDF generated")]),
            )
        )

        # Return payload → ADK creates agent_output event
        return {"pdf_filename": filename, "version": version, "url": url}