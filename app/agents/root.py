from google.adk.agents import SequentialAgent

from app.agents.analysis_loop import analysis_loop
from app.agents.collect_loop import collector_loop
from app.agents.parser import json_parser
from app.agents.pdf_agent import PdfAgent

root_agent = SequentialAgent(
    name="ReframePipeline",
    sub_agents=[
        collector_loop,
        json_parser,
        analysis_loop,
        PdfAgent(),
    ],
)
