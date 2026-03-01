"""
Adapter: OllamaVideoAnalyzer

Analyzes video using Ollama with vision model (llava, llama3.2-vision, etc).
"""

import base64
from pathlib import Path

import cv2  # type: ignore[import-untyped]
import ollama  # type: ignore[import-untyped]

from domain.models import VideoAnalysis


class OllamaVideoAnalyzer:
    """Analyze video using Ollama's vision model."""

    def __init__(
        self,
        model: str = "llava:7b",
        frame_interval: float = 5.0,
    ) -> None:
        self._model = model
        self._frame_interval = frame_interval

    def analyze(self, video_path: Path) -> VideoAnalysis:
        """Extract frames and send to Ollama for analysis."""
        frames = self._extract_frames(video_path)

        first_frame = frames[0] if frames else None
        if first_frame is None:
            raise ValueError(f"No frames extracted from: {video_path}")

        prompt = self._build_prompt()

        response = ollama.chat(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [first_frame],
                }
            ],
        )

        content = response["message"]["content"]
        return self._parse_response(content)

    def _extract_frames(self, video_path: Path) -> list[str]:
        """Extract frames from video and return as base64."""
        video = cv2.VideoCapture(str(video_path))
        if not video.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = video.get(cv2.CAP_PROP_FPS)
        interval_frames = int(fps * self._frame_interval)

        frames_b64 = []
        frame_idx = 0

        while True:
            ret, frame = video.read()
            if not ret:
                break

            if frame_idx % interval_frames == 0:
                _, buffer = cv2.imencode(".jpg", frame)
                frames_b64.append(base64.b64encode(buffer).decode("utf-8"))  # type: ignore[arg-type]

            frame_idx += 1

        video.release()
        return frames_b64

    def _build_prompt(self) -> str:
        """Build the analysis prompt."""
        return """Analyze this video frame and return a JSON object with:
- topic: What is the video about? (short phrase)
- summary: What happens in the video? (1-2 sentences)
- key_moments: List of interesting moments (array of strings)
- humor_style: What's the style of humor/engagement? (optional string)

Return ONLY valid JSON, no other text."""

    def _parse_response(self, content: str) -> VideoAnalysis:
        """Parse the Ollama response into VideoAnalysis."""
        import json
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
            data = json.loads(content)
        except json.JSONDecodeError:
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                content = content[json_start:json_end]
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    content = re.sub(r",\s*}", "}", content)
                    content = re.sub(r",\s*]", "]", content)
                    content = content.replace("\n", " ").replace("\r", "")
                    content = re.sub(r"\s+", " ", content)
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError:
                        data = {
                            "topic": "video",
                            "summary": "content",
                            "key_moments": [],
                            "humor_style": None,
                        }
            else:
                data = {
                    "topic": "video",
                    "summary": "content",
                    "key_moments": [],
                    "humor_style": None,
                }

        return VideoAnalysis(
            topic=data.get("topic", ""),
            summary=data.get("summary", ""),
            key_moments=data.get("key_moments", []),
            humor_style=data.get("humor_style"),
        )
