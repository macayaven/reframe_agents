import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

@pytest.mark.asyncio
async def test_happy_flow():
    await AgentEvaluator.evaluate(
        agent_module="app.agents.root",
        eval_dataset_file_path_or_dir="tests/integration/happy_flow.test.json",
    )