"""
Adapter: OllamaScriptGenerator

Generates a script from video analysis using Ollama.
"""

import ollama  # type: ignore[import-untyped]

from domain.models import VideoAnalysis, Script, ScriptCue


class OllamaScriptGenerator:
    """Generate script using Ollama."""

    def __init__(self, model: str = "llama3.2") -> None:
        self._model = model

    def generate(self, analysis: VideoAnalysis) -> Script:
        """Create a script based on video analysis."""
        prompt = self._build_prompt(analysis)

        response = ollama.chat(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response["message"]["content"]
        return self._parse_response(content)

    def _build_prompt(self, analysis: VideoAnalysis) -> str:
        """Build the script generation prompt."""
        return f"""Based on this video analysis:
- Topic: {analysis.topic}
- Summary: {analysis.summary}
- Key moments: {", ".join(analysis.key_moments)}

Create an engaging, short script for a TikTok video. Return JSON with:
- text: The full script (1-3 sentences, conversational)
- duration_seconds: Estimated duration (15-60 seconds)
- cues: Array of cue objects with timestamp_start, timestamp_end, text

Return ONLY valid JSON."""

    def _parse_response(self, content: str) -> Script:
        """Parse response into Script."""
        import json

        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        data = json.loads(content)

        cues = []
        for cue_data in data.get("cues", []):
            cues.append(
                ScriptCue(
                    timestamp_start=cue_data.get("timestamp_start", 0.0),
                    timestamp_end=cue_data.get("timestamp_end", 10.0),
                    text=cue_data.get("text", ""),
                    meme_url=cue_data.get("meme_url"),
                )
            )

        return Script(
            text=data.get("text", ""),
            duration_seconds=data.get("duration_seconds", 30.0),
            cues=cues,
        )
