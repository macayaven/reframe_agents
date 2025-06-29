from google.adk.agents import LlmAgent

json_parser = LlmAgent(
    name="JsonParser",
    model="gemini-1.5-pro",
    instruction=(
        "Convierte la conversación completa `${conv_raw}` en JSON con campos "
        "`name`, `age`, `reason`. Devuelve SOLO JSON."
    ),
    ouput_key=["conv_raw"],  # we saved it in the transcript callback
    output_key="parsed",  # state['parsed']
)
