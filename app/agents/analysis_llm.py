from google.adk.agents import LlmAgent

from app.callbacks.lang_detect import LangCallback
from app.callbacks.safety_filters import SafetyGuard
from app.callbacks.transcript_acc import TranscriptAccumulator

analyst_llm = LlmAgent(
    name="AnalystLLM",
    model="gemini-1.5-flash",
    instruction=(
        "Eres un analista. Usa `${parsed}` para conversar con el usuario. "
        "Si necesitas datos externos llama a `web_search`. "
        "Cuando el usuario quede satisfecho responde:\n"
        '{"analysis_done": true, "summary": "..."}'
    ),
    output_key="parsed",  # inject parsed JSON each turn
    before_agent_callback=[LangCallback(), SafetyGuard()],
    after_model_callback=[TranscriptAccumulator()],
)
