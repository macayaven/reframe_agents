from google.adk.agents import LlmAgent

from app.callbacks.lang_detect import LangCallback
from app.callbacks.safety_filters import SafetyGuard
from app.callbacks.transcript_acc import TranscriptAccumulator
from app.tools.exit_loop import exit_loop

collector_llm = LlmAgent(
    name="CollectorLLM",
    model="gemini-2.",
    instruction=(
        "Charla con el usuario hasta obtener nombre, edad y motivo de la "
        "consulta. Cuando termines responde sólo:\n"
        '{"goal_reached": true}'
    ),
    before_model_callback=[LangCallback(), SafetyGuard()],
    after_model_callback=TranscriptAccumulator(),
    tools=[exit_loop],
)
