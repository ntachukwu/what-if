"""
Adapter: OpenAIScriptGenerator

Generates a script from video analysis using OpenAI GPT.
"""

from openai import OpenAI

from domain.models import VideoAnalysis, Script, ScriptCue


class OpenAIScriptGenerator:
    """Generate script using OpenAI's GPT model."""

    def __init__(self, api_key: str) -> None:
        self._client = OpenAI(api_key=api_key)

    def generate(self, analysis: VideoAnalysis) -> Script:
        """Create a script based on video analysis."""
        prompt = self._build_prompt(analysis)

        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=500,
        )

        content = response.choices[0].message.content or ""
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
        """Parse GPT response into Script."""
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
