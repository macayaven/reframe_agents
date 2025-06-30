"""PdfAgent - deterministic final step that builds a PDF and saves it as an artifact."""

from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.genai.types import Blob, Content, Part

from app.config.base import Settings
from app.tools.pdf_generator import build_pdf_bytes

settings = Settings()


class PdfAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(name="PdfGenerator", description="Generates the final PDF report")
        # Future LLM integration will use settings.synthesis_agent_instruction_key
        # for fetching the prompt from the prompt service

    # ------------------------------------------------------------------ #
    # ADK ≥ 1.5 requires async generators that yield Events.             #
    # ------------------------------------------------------------------ #
    async def _run_async_impl(self, ctx):  # type: ignore[attr-defined]
        async for event in self._produce(ctx):
            yield event

    async def _run_live_impl(self, ctx):  # type: ignore[attr-defined]
        async for event in self._produce(ctx):
            yield event

    # ---------------------- helper ------------------------------------ #
    async def _produce(self, ctx):  # type: ignore[attr-defined]
        # Get session-level state
        state = ctx.session.state

        # Get the parsed intake data and CBT analysis from state
        intake_data = state.get("parsed", {})
        analysis_output = state.get("cbt_analysis", state.get("final_analysis", ""))

        # Log what we're working with
        print(f"  [PdfAgent] Building PDF with intake_data keys: {list(intake_data.keys())}")
        print(f"  [PdfAgent] Analysis output length: {len(analysis_output)}")

        pdf_bytes = build_pdf_bytes(
            intake_data=intake_data,
            analysis_output=analysis_output,
        )

        # Check if we have artifact service available
        if hasattr(ctx, "save_artifact") and callable(getattr(ctx, "save_artifact", None)):
            # Wrap bytes as a Part for save_artifact
            artifact_part = Part(inline_data=Blob(data=pdf_bytes, mime_type="application/pdf"))
            filename = "report.pdf"
            version = await ctx.save_artifact(filename=filename, artifact=artifact_part)

            url = await ctx.get_artifact_url(
                filename=filename,
                version=version,
                expiry_seconds=120,  # 2-minute signed link
            )

            # Store output in session state
            state["pdf_output"] = {
                "pdf_filename": filename,
                "version": version,
                "url": url,
            }

            # Emit final message with PDF link
            yield Event(
                author=self.name,
                content=Content(parts=[Part(text=f"📄 PDF generated: {url}")]),
            )  # type: ignore[attr-defined]
        else:
            # Fallback: Store PDF in state as base64
            import base64

            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

            # Store in session state
            state["pdf_output"] = {
                "pdf_filename": "report.pdf",
                "pdf_base64": pdf_base64,
                "pdf_size": len(pdf_bytes),
            }

            # Include PDF as attachment in the event
            pdf_part = Part(inline_data=Blob(data=pdf_bytes, mime_type="application/pdf"))

            # Emit final message with PDF data
            yield Event(
                author=self.name,
                content=Content(
                    parts=[
                        Part(
                            text=f"📄 PDF generated ({len(pdf_bytes)} bytes). The PDF data is included in the session state as base64."
                        ),
                        pdf_part,
                    ]
                ),
            )  # type: ignore[attr-defined]
