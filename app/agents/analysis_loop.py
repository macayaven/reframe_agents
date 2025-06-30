from google.adk.agents import LoopAgent

from app.agents.analysis_llm import analyst_llm

analysis_loop = LoopAgent(
    name="AnalysisLoop",
    sub_agents=[analyst_llm],
    max_iterations=8,
)
