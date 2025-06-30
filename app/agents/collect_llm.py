from google.adk.agents import LlmAgent

from app.callbacks.lang_detect import LangCallback
from app.callbacks.safety_filters import SafetyGuard
from app.callbacks.transcript_acc import TranscriptAccumulator
from app.config.base import Settings
from app.services.prompts.langfuse_cli import prompt_manager
from app.tools.exit_loop import exit_loop

settings = Settings()

collector_llm = LlmAgent(
    name="CollectorLLM",
    model=settings.google_ai_model,
    instruction=prompt_manager.fetch_prompt(settings.collect_agent_instruction_key),
    before_model_callback=[LangCallback(), SafetyGuard()],
    after_model_callback=TranscriptAccumulator(),
    tools=[exit_loop],
)
