import json

from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.genai.types import Content, Part

from app.callbacks.lang_detect import LangCallback
from app.callbacks.safety_filters import SafetyGuard
from app.callbacks.transcript_acc import TranscriptAccumulator
from app.config.base import Settings
from app.services.prompts.langfuse_cli import prompt_manager
from app.tools.save_analysis import save_analysis

settings = Settings()


class AnalystLLMAgent(BaseAgent):
    """Analysis agent that uses parsed intake data."""

    async def _run_async_impl(self, ctx):
        """Analyze the parsed intake data."""
        # Get the parsed data from state
        parsed_data = ctx.session.state.get("parsed", {})

        if not parsed_data:
            yield Event(
                author=self.name,
                content=Content(
                    parts=[
                        Part(
                            text="No parsed intake data found. Please complete the intake and parsing steps first."
                        )
                    ]
                ),
            )
            return

        # Get the analysis instruction
        analysis_instruction = prompt_manager.fetch_prompt(settings.analysis_agent_instruction_key)

        # Create the prompt with the parsed data
        prompt = f"""{analysis_instruction}

Here is the structured intake data to analyze:

{json.dumps(parsed_data, indent=2)}

Please provide a comprehensive CBT analysis as specified in the instructions."""

        # Use the LLM to analyze
        from google.adk.agents import LlmAgent

        llm = LlmAgent(
            name="AnalystLLMCore",
            model=settings.google_ai_model,
            instruction=prompt,
            before_model_callback=[LangCallback(), SafetyGuard()],
            after_model_callback=[TranscriptAccumulator()],
            tools=[save_analysis],  # Tool for saving analysis
        )

        # Process through LLM
        async for llm_event in llm.run_async(ctx):
            yield llm_event


analyst_llm = AnalystLLMAgent(name="AnalystLLM")
