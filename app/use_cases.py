"""
Application layer — use cases that orchestrate the domain.

These coordinate the ports (adapters) to fulfill user requests.
"""

import logging
import tempfile
from pathlib import Path

from adapters.frame_extractor import OllamaFrameExtractor, ScoredFrame
from adapters.klipy_content_finder import KlipyContentFinder
from adapters.tts_service import get_tts_service
from domain.models import Meme, RemixRequest, RemixResult, Script, VideoSegment
from domain.ports import VideoAnalyzer, ScriptGenerator

logger = logging.getLogger(__name__)


class RemixVideo:
    """Orchestrate the Fireship-style video remix pipeline."""

    def __init__(
        self,
        analyzer: VideoAnalyzer,
        script_gen: ScriptGenerator,
        content_finder: KlipyContentFinder | None,
        content_type: str,
        frame_extractor: OllamaFrameExtractor,
        tts_provider: str,
    ) -> None:
        self._analyzer = analyzer
        self._script_gen = script_gen
        self._content_finder = content_finder
        self._content_type = content_type
        self._frame_extractor = frame_extractor
        self._tts_provider = tts_provider

    def execute(self, request: RemixRequest) -> RemixResult:
        """Run the full remix pipeline."""
        logger.info("Starting video remix pipeline...")

        logger.info("Analyzing video...")
        analysis = self._analyzer.analyze(request.video_path)

        logger.info("Extracting and scoring frames...")
        scored_frames = self._frame_extractor.extract_scored_frames(
            request.video_path, analysis
        )

        logger.info("Generating script...")
        script = self._script_gen.generate(analysis)

        logger.info("Generating TTS audio...")
        tts_service = get_tts_service(self._tts_provider)
        audio_path = Path(tempfile.mktemp(suffix=".mp3"))
        tts_service.generate(script.text, audio_path)

        logger.info("Finding memes for segments...")
        memes = self._search_memes(analysis.topic, request.num_segments)

        logger.info("Building segments...")
        segments = self._build_segments(
            scored_frames=scored_frames,
            script=script,
            memes=memes,
            num_segments=request.num_segments,
        )

        from adapters.moviepy_compositor import MoviePyCompositor

        compositor = MoviePyCompositor()
        result = compositor.compose(
            request=request,
            segments=segments,
            audio_path=audio_path,
            background_color=request.background_color,
        )

        if audio_path.exists():
            audio_path.unlink()

        return result

    def _search_memes(self, query: str, limit: int) -> list[Meme]:
        """Search for memes matching the query."""
        if not self._content_finder:
            return []

        try:
            if self._content_type == "gif":
                contents = self._content_finder.search_gifs(query, limit=limit)
            elif self._content_type == "sticker":
                contents = self._content_finder.search_stickers(query, limit=limit)
            elif self._content_type == "clip":
                contents = self._content_finder.search_clips(query, limit=limit)
            elif self._content_type == "meme":
                contents = self._content_finder.search_memes(query, limit=limit)
            else:
                contents = self._content_finder.search_gifs(query, limit=limit)
            return self._content_finder.to_memes(contents)
        except PermissionError as e:
            logger.warning(f"Content search skipped: {e}")
        except Exception as e:
            logger.warning(f"Content search failed: {e}")
        return []

    def _build_segments(
        self,
        scored_frames: list[ScoredFrame],
        script: Script,
        memes: list[Meme],
        num_segments: int,
    ) -> list[VideoSegment]:
        """Build video segments from frames and script."""
        segments = []
        segment_duration = script.duration_seconds / num_segments

        for i in range(min(num_segments, len(scored_frames), len(script.cues))):
            frame = scored_frames[i]
            cue = script.cues[i] if i < len(script.cues) else script.cues[-1]
            meme = memes[i] if i < len(memes) else None

            segment = VideoSegment(
                frame_path=frame.image_path,
                original_timestamp=frame.timestamp,
                text=cue.text,
                meme_url=meme.url if meme else None,
                start_time=i * segment_duration,
                duration=segment_duration,
                caption=frame.caption,
            )
            segments.append(segment)

        return segments
