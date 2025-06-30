from google.adk.agents import BaseAgent
from google.adk.events import Event
from google.genai.types import Content, Part

from app.config.base import Settings
from app.services.prompts.langfuse_cli import prompt_manager

settings = Settings()


class JsonParserAgent(BaseAgent):
    """Parser agent that reads transcript from state and converts to JSON."""

    async def _run_async_impl(self, ctx):
        """Process the intake transcript from state."""
        # Get the transcript from state
        intake_transcript = ctx.session.state.get("intake_transcript", "")
        conv_raw = ctx.session.state.get("conv_raw", [])

        print(f"[JsonParser] Processing transcript with {len(conv_raw)} entries")
        print(f"[JsonParser] Intake transcript length: {len(intake_transcript)}")

        if not intake_transcript and not conv_raw:
            yield Event(
                author=self.name,
                content=Content(
                    parts=[
                        Part(
                            text="No intake transcript found in state. Please complete the intake process first."
                        )
                    ]
                ),
            )
            return

        # Build the full transcript if needed
        if not intake_transcript and conv_raw:
            intake_transcript = "\n".join(f"{entry['role']}: {entry['text']}" for entry in conv_raw)
            ctx.session.state["intake_transcript"] = intake_transcript

        # Get the parser instruction
        parser_instruction = prompt_manager.fetch_prompt(settings.parser_agent_instruction_key)

        # Create the prompt with the transcript
        prompt = f"""{parser_instruction}

Here is the intake conversation transcript to process:

{intake_transcript}

Please extract and structure this information as JSON as specified in the instructions."""

        # Use the LLM to parse
        from google.adk.agents import LlmAgent

        llm = LlmAgent(
            name="JsonParserLLM",
            model=settings.google_ai_model,
            instruction=prompt,
        )

        # Process through LLM
        async for llm_event in llm.run_async(ctx):
            if llm_event.content and llm_event.content.parts:
                # Extract JSON from the response
                response_text = ""
                for part in llm_event.content.parts:
                    if hasattr(part, "text") and part.text:
                        response_text += part.text

                # Try to extract JSON
                import json
                import re

                # Look for JSON in the response
                json_match = re.search(r"\{[\s\S]*\}", response_text)
                if json_match:
                    try:
                        parsed_data = json.loads(json_match.group())
                        ctx.session.state["parsed"] = parsed_data
                        print(f"[JsonParser] Successfully parsed JSON: {list(parsed_data.keys())}")

                        yield Event(
                            author=self.name,
                            content=Content(
                                parts=[
                                    Part(
                                        text=f"Successfully extracted intake data:\n{json.dumps(parsed_data, indent=2)}"
                                    )
                                ]
                            ),
                        )
                    except json.JSONDecodeError as e:
                        print(f"[JsonParser] Failed to parse JSON: {e}")
                        # Store raw response as fallback
                        ctx.session.state["parsed"] = {"raw_response": response_text}
                        yield llm_event
                else:
                    # No JSON found, store raw response
                    ctx.session.state["parsed"] = {"raw_response": response_text}
                    yield llm_event


json_parser = JsonParserAgent(name="JsonParser")
