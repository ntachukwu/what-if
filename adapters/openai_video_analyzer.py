"""
Adapter: OpenAIVideoAnalyzer

Analyzes video using OpenAI GPT-4V to extract topic, summary, and key moments.
"""
# mypy: disable-error-code="misc,list-item,arg-type"

import base64
from pathlib import Path

import cv2
from openai import OpenAI

from domain.models import VideoAnalysis


class OpenAIVideoAnalyzer:
    """Analyze video using OpenAI's vision model."""

    def __init__(self, api_key: str, frame_interval: float = 5.0) -> None:
        self._client = OpenAI(api_key=api_key)
        self._frame_interval = frame_interval

    def analyze(self, video_path: Path) -> VideoAnalysis:
        """Extract frames and send to GPT-4V for analysis."""
        frames = self._extract_frames(video_path)
        frames_b64 = self._encode_frames(frames)

        prompt = self._build_prompt()

        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[  # type: ignore[misc,list-item]
                {  # type: ignore[misc,list-item]
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        *[
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{frame}"},
                            }
                            for frame in frames_b64[:5]  # Limit to 5 frames
                        ],
                    ],
                }
            ],
            max_tokens=500,
        )

        content = response.choices[0].message.content or ""
        return self._parse_response(content)

    def _extract_frames(self, video_path: Path) -> list:
        """Extract frames from video at intervals."""
        video = cv2.VideoCapture(str(video_path))
        if not video.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = video.get(cv2.CAP_PROP_FPS)
        interval_frames = int(fps * self._frame_interval)

        frames = []
        frame_idx = 0

        while True:
            ret, frame = video.read()
            if not ret:
                break

            if frame_idx % interval_frames == 0:
                frames.append(frame)

            frame_idx += 1

        video.release()
        return frames

    def _encode_frames(self, frames: list) -> list[str]:
        """Encode frames to base64."""
        encoded = []
        for frame in frames:
            _, buffer = cv2.imencode(".jpg", frame)
            encoded.append(base64.b64encode(buffer).decode("utf-8"))  # type: ignore[arg-type]
        return encoded

    def _build_prompt(self) -> str:
        """Build the analysis prompt."""
        return """Analyze this video and return a JSON object with:
- topic: What is the video about? (short phrase)
- summary: What happens in the video? (1-2 sentences)
- key_moments: List of interesting moments (array of strings)
- humor_style: What's the style of humor/engagement? (optional string)

Return ONLY valid JSON, no other text."""

    def _parse_response(self, content: str) -> VideoAnalysis:
        """Parse the GPT response into VideoAnalysis."""
        import json

        # Extract JSON from response
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        data = json.loads(content)

        return VideoAnalysis(
            topic=data.get("topic", ""),
            summary=data.get("summary", ""),
            key_moments=data.get("key_moments", []),
            humor_style=data.get("humor_style"),
        )
