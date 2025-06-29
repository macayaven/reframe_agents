from google.adk.agents import LoopAgent

from app.agents.collect_llm import collector_llm

collector_loop = LoopAgent(
    name="CollectorLoop",
    sub_agents=[collector_llm],
    max_iterations=12,
    stop_condition=lambda ctx: ctx.state.get("collection_complete", False),
)
