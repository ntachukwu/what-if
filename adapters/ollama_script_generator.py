"""
Adapter: OllamaScriptGenerator

Generates a Fireship-style script from video analysis using Ollama.
"""

import json
import re
from typing import Any

import ollama  # type: ignore[import-untyped]

from domain.models import VideoAnalysis, Script, ScriptCue


class OllamaScriptGenerator:
    """Generate Fireship-style script using Ollama."""

    def __init__(self, model: str = "llama3.2", num_segments: int = 12) -> None:
        self._model = model
        self._num_segments = num_segments

    def generate(self, analysis: VideoAnalysis) -> Script:
        """Create a Fireship-style script based on video analysis."""
        prompt = self._build_prompt(analysis)

        response = ollama.chat(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )

        content = response["message"]["content"]
        return self._parse_response(content)

    def _build_prompt(self, analysis: VideoAnalysis) -> str:
        """Build Fireship-style script generation prompt."""
        return f"""Create a FIRESHIP-style video script based on this video analysis:

Topic: {analysis.topic}
Summary: {analysis.summary}
Key moments: {", ".join(analysis.key_moments[:5])}
Humor style: {analysis.humor_style or "general meme humor"}

Create {self._num_segments} punchy segments for a 45-60 second TikTok video.
Each segment should be:
- Bold/controversial take on the topic (1-2 sentences)
- Short, punchy, conversational
- Sarcastic or dramatic
- Perfect for text overlay + reaction meme

Return ONLY valid JSON with this structure:
{{
  "title": "Catchy video title",
  "segments": [
    {{
      "text": "Bold take statement...",
      "keywords": ["keyword1", "keyword2"],
      "effect": "zoom" | "flash" | "cut" | null
    }}
  ],
  "intro": "Hook statement for first 3 seconds",
  "outro": "Call to action at end"
}}

Make it funny, dramatic, and meme-worthy!"""

    def _parse_response(self, content: str) -> Script:
        """Parse response into Script with segments."""

        content = content.strip()

        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            data: dict[str, Any] = json.loads(content)
        except json.JSONDecodeError:
            try:
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    data = {
                        "segments": [{"text": content[:100]}],
                        "intro": "",
                        "outro": "",
                    }
            except (json.JSONDecodeError, AttributeError):
                data = {
                    "segments": [{"text": content[:100] if content else "placeholder"}],
                    "intro": "",
                    "outro": "",
                }

        _ = data.get("title", "Meme Video")
        intro = data.get("intro", "")
        outro = data.get("outro", "")
        segments = data.get("segments", [])

        total_duration = 60.0
        segment_duration = total_duration / len(segments) if segments else 4.0

        cues = []
        current_time = 0.0
        full_text = intro + " "

        for seg in segments:
            text = seg.get("text", "")
            full_text += text + " "

            cue = ScriptCue(
                timestamp_start=current_time,
                timestamp_end=current_time + segment_duration,
                text=text,
                meme_url=None,
            )
            cues.append(cue)
            current_time += segment_duration

        full_text += outro

        return Script(
            text=full_text.strip(),
            duration_seconds=current_time,
            cues=cues,
        )

    def _try_repair_json(self, content: str) -> dict[str, Any]:
        """Attempt to repair malformed JSON."""
        import re

        content = content.strip()

        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        try:
            return dict(json.loads(content))
        except json.JSONDecodeError:
            pass

        json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", content)
        if json_match:
            try:
                return dict(json.loads(json_match.group()))
            except json.JSONDecodeError:
                pass

        brace_count = 0
        start = None
        in_string = False
        escape_next = False

        for i, char in enumerate(content):
            if escape_next:
                escape_next = False
                continue
            if char == "\\":
                escape_next = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if in_string:
                continue

            if char == "{":
                if start is None:
                    start = i
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0 and start is not None:
                    try:
                        return dict(json.loads(content[start : i + 1]))
                    except json.JSONDecodeError:
                        pass

        raise ValueError(f"Could not parse JSON from: {content[:100]}")
