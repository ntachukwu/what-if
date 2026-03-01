"""
Adapter: OllamaFrameExtractor

Extracts and scores video frames using AI for meme potential.
"""

from dataclasses import dataclass
import json
from pathlib import Path

import cv2  # type: ignore[import-untyped]
import ollama  # type: ignore[import-untyped]

from domain.models import VideoAnalysis


@dataclass
class ScoredFrame:
    """A video frame with meme potential score."""

    timestamp: float
    image_path: Path
    score: float
    caption: str | None = None


class OllamaFrameExtractor:
    """Extract and score frames using Ollama vision model."""

    def __init__(
        self,
        model: str = "llava:7b",
        num_candidates: int = 30,
        num_selected: int = 12,
    ) -> None:
        self.model = model
        self.num_candidates = num_candidates
        self.num_selected = num_selected

    def extract_scored_frames(
        self,
        video_path: Path,
        analysis: VideoAnalysis | None = None,
    ) -> list[ScoredFrame]:
        """Extract candidate frames and score them for meme potential."""
        candidate_frames = self._extract_candidate_frames(video_path)

        scored_frames = []
        for frame in candidate_frames:
            score, caption = self._score_frame(frame, analysis)
            scored_frames.append(
                ScoredFrame(
                    timestamp=frame.timestamp,
                    image_path=frame.image_path,
                    score=score,
                    caption=caption,
                )
            )

        scored_frames.sort(key=lambda f: f.score, reverse=True)
        return scored_frames[: self.num_selected]

    def _extract_candidate_frames(self, video_path: Path) -> list[ScoredFrame]:
        """Extract frames at regular intervals from video."""
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        if duration == 0:
            cap.release()
            raise ValueError(f"Invalid video: {video_path}")

        interval = duration / self.num_candidates
        frames = []

        tmpdir = video_path.parent / ".whatif_frames"
        tmpdir.mkdir(exist_ok=True)

        for i in range(self.num_candidates):
            timestamp = i * interval
            frame_number = int(timestamp * fps)

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()

            if ret:
                image_path = tmpdir / f"frame_{i:03d}.jpg"
                cv2.imwrite(str(image_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frames.append(
                    ScoredFrame(
                        timestamp=timestamp,
                        image_path=image_path,
                        score=0.0,
                    )
                )

        cap.release()
        return frames

    def _score_frame(
        self, frame: ScoredFrame, analysis: VideoAnalysis | None
    ) -> tuple[float, str | None]:
        """Score a frame for meme potential using AI."""
        context = ""
        if analysis:
            context = f"The video is about: {analysis.topic}. "
            f"Humor style: {analysis.humor_style or 'general'}."

        prompt = f"""{context}
Analyze this frame from a video and rate its MEME POTENTIAL from 0-10.
Consider:
- Is it funny/reaction-worthy?
- Is there an expressive face?
- Is something surprising happening?
- Is it a good reaction moment?

Respond ONLY with valid JSON:
{{"score": <number>, "caption": "<short description>"}}

Example: {{"score": 8.5, "caption": "Surprised face looking at camera"}}
"""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [str(frame.image_path)],
                    }
                ],
            )
            content = response.message.content  # type: ignore[union-attr]
            if content is None:
                return 5.0, None
            return self._parse_response(content)
        except Exception:
            return 5.0, None

    def _parse_response(self, content: str) -> tuple[float, str | None]:
        """Parse AI response into score and caption."""
        import re

        content = content.strip()

        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            data = json.loads(content)
            score = float(data.get("score", 5.0))
            caption = data.get("caption")
            return score, caption
        except (json.JSONDecodeError, ValueError, KeyError):
            match = re.search(r'"score":\s*(\d+\.?\d*)', content)
            if match:
                score = float(match.group(1))
                caption_match = re.search(r'"caption":\s*"([^"]*)"', content)
                caption = caption_match.group(1) if caption_match else None
                return score, caption
            return 5.0, None
