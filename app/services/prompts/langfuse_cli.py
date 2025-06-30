"""Prompt manager that downloads and caches prompts from Langfuse."""

from functools import lru_cache
import os

from langfuse import Langfuse

from app.config.base import Settings


class _LangfusePromptManager:
    """Manages prompt downloading and caching from Langfuse."""

    def __init__(self) -> None:
        """Initialize the prompt manager."""
        self.settings = Settings()
        self._prompts: dict[str, str] = {}
        self._langfuse: Langfuse | None = None
        self._cache_dir = "/tmp/reframe_prompts"
        os.makedirs(self._cache_dir, exist_ok=True)

        # Try to download prompts but don't fail if Langfuse is unavailable
        try:
            self._download_all_prompts()
        except Exception as e:
            print(f"Warning: Failed to download prompts during initialization: {e}")
            print("Using fallback prompts for all agents")

    def _get_langfuse_client(self) -> Langfuse:
        """Get or create Langfuse client."""
        if not self._langfuse:
            self._langfuse = Langfuse(
                host=self.settings.langfuse_host,
                public_key=self.settings.langfuse_public_key,
                secret_key=self.settings.langfuse_secret_key,
            )
        return self._langfuse

    def _get_cache_path(self, prompt_name: str) -> str:
        """Get the cache file path for a prompt."""
        return os.path.join(self._cache_dir, f"{prompt_name}.txt")

    def _download_prompt(self, prompt_name: str) -> str:
        """Download a prompt from Langfuse and cache it."""
        try:
            # Try to load from memory cache first
            if prompt_name in self._prompts:
                return self._prompts[prompt_name]

            # Try to load from file cache
            cache_path = self._get_cache_path(prompt_name)
            if os.path.exists(cache_path):
                with open(cache_path, encoding="utf-8") as f:
                    prompt = f.read()
                    self._prompts[prompt_name] = prompt
                    return prompt

            # Download from Langfuse
            langfuse = self._get_langfuse_client()
            prompt_obj = langfuse.get_prompt(prompt_name)
            prompt = str(prompt_obj.compile())

            # Cache in memory and file
            self._prompts[prompt_name] = prompt
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(prompt)

            return prompt

        except Exception as e:
            # Fallback to default prompts
            print(f"Warning: Failed to download prompt '{prompt_name}': {e!s}")
            print(f"Using fallback prompt for '{prompt_name}'")

            fallback_prompts = {
                "intake-agent-adk-instructions": """You are a compassionate intake specialist helping users describe their challenging social situations.

Your goal is to gather detailed information about:
1. The specific social situation that was challenging
2. Their thoughts and feelings during the situation
3. How they responded or what behaviors they engaged in
4. The outcome and how they felt afterward

Guidelines:
- Be empathetic and non-judgmental
- Ask ONE clarifying question at a time to get specific details
- Help them identify thoughts, feelings, and behaviors
- After gathering all key information, you MUST call the exit_loop tool

IMPORTANT TOOL USAGE:
- You have access to the exit_loop tool
- You MUST call exit_loop when you have gathered:
  - Description of the social situation
  - Their thoughts during the situation
  - Their feelings/emotions
  - Their behaviors/actions
  - The outcome/aftermath
- Call the exit_loop tool when you have all the information
- Do NOT continue asking questions indefinitely - exit after collecting the key information""",
                "intake-parser-agent-adk-instructions": """You are a JSON parser that converts the collected intake information into a structured format.

Extract the following information from the conversation transcript and return it as JSON:
{
  "situation": "Description of the challenging social situation",
  "thoughts": ["List of thoughts the person had"],
  "feelings": ["List of emotions experienced"],
  "behaviors": ["List of behaviors or responses"],
  "outcome": "What happened and how they felt afterward",
  "timestamp": "Current ISO timestamp"
}

Be accurate and preserve the user's own words where possible.""",
                "reframe-agent-adk-instructions": """You are a CBT-trained analyst specializing in cognitive reframing for social anxiety.

Analyze the parsed intake data and provide:
1. Identification of cognitive distortions (e.g., mind reading, catastrophizing, all-or-nothing thinking)
2. Evidence for and against the negative thoughts
3. More balanced, realistic alternative thoughts
4. Behavioral suggestions for similar future situations
5. Validation of the person's experience while offering hope

Structure your analysis clearly with sections for each component.
Be compassionate, evidence-based, and practical in your suggestions.

IMPORTANT TOOL USAGE:
- You have access to the save_analysis tool
- You MUST call save_analysis when your analysis is complete
- Call save_analysis(analysis="YOUR_COMPLETE_CBT_ANALYSIS_TEXT_HERE") when done
- Include your ENTIRE analysis as the 'analysis' parameter
- Do NOT use exit_loop - use save_analysis instead""",
                "synthesis-agent-adk-instructions": """You are a synthesis specialist who creates comprehensive PDF reports.

Using the intake data and CBT analysis, create a well-formatted report that includes:
1. Summary of the situation
2. Identified thought patterns and cognitive distortions
3. Reframed perspectives with supporting evidence
4. Practical strategies and behavioral suggestions
5. Encouraging conclusion with next steps

Format the content for clarity and readability in a PDF document.""",
            }

            if prompt_name in fallback_prompts:
                prompt = fallback_prompts[prompt_name]
                # Cache the fallback prompt
                self._prompts[prompt_name] = prompt
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(prompt)
                return prompt
            raise RuntimeError(f"No fallback prompt available for '{prompt_name}'") from e

    def _download_all_prompts(self) -> dict[str, str]:
        """Download all required prompts and cache them."""
        required_prompts = [
            "intake-agent-adk-instructions",
            "intake-parser-agent-adk-instructions",  # Added parser prompt
            "reframe-agent-adk-instructions",
            "synthesis-agent-adk-instructions",
        ]

        for prompt_name in required_prompts:
            self._download_prompt(prompt_name)

        return self._prompts

    def _get_prompt(self, prompt_name: str) -> str:
        """Get a prompt, downloading if necessary."""
        if prompt_name not in self._prompts:
            return self._download_prompt(prompt_name)
        return self._prompts[prompt_name]

    def clear_cache(self) -> None:
        """Clear all cached prompts."""
        self._prompts.clear()
        # Optionally remove cache files
        for file in os.listdir(self._cache_dir):
            if file.endswith(".txt"):
                os.remove(os.path.join(self._cache_dir, file))

    @lru_cache  # noqa: B019
    def fetch_prompt(self, name: str) -> str:
        """Return the compiled prompt string by name.

        The prompt is cached in memory by the PromptManager; an additional
        `lru_cache` here lets us skip the attribute lookup entirely on hot paths.
        """
        return self._get_prompt(name)


prompt_manager = _LangfusePromptManager()
