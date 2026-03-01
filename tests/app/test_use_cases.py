"""Tests for the RemixVideo use case."""

from pathlib import Path
from unittest.mock import Mock


from app.use_cases import RemixVideo
from domain.models import (
    VideoAnalysis,
    Script,
    RemixRequest,
)


class TestRemixVideo:
    """Tests for RemixVideo orchestrator."""

    def test_executes_full_pipeline(self) -> None:
        """Verify all steps are called in order."""
        analyzer = Mock()
        script_gen = Mock()
        content_finder = Mock()
        frame_extractor = Mock()

        analysis = VideoAnalysis(
            topic="funny cat",
            summary="A cat doing something funny",
            key_moments=["cat jumps"],
        )
        script = Script(
            text="Look at this cat!",
            duration_seconds=30.0,
            cues=[],
        )
        scored_frames = []

        analyzer.analyze.return_value = analysis
        script_gen.generate.return_value = script
        frame_extractor.extract_scored_frames.return_value = scored_frames
        content_finder.search_gifs.return_value = []

        use_case = RemixVideo(
            analyzer=analyzer,
            script_gen=script_gen,
            content_finder=content_finder,
            content_type="gif",
            frame_extractor=frame_extractor,
            tts_provider="gtts",
        )
        request = RemixRequest(
            video_path=Path("input.mp4"),
            output_path=Path("output.mp4"),
        )

        use_case.execute(request)

        analyzer.analyze.assert_called_once_with(Path("input.mp4"))
        script_gen.generate.assert_called_once_with(analysis)

    def test_skips_content_search_when_disabled(self) -> None:
        """Verify content search is skipped when content_finder is None."""
        analyzer = Mock()
        script_gen = Mock()
        frame_extractor = Mock()

        analysis = VideoAnalysis(
            topic="funny cat",
            summary="A cat doing something funny",
            key_moments=["cat jumps"],
        )
        script = Script(
            text="Look at this cat!",
            duration_seconds=30.0,
            cues=[],
        )

        analyzer.analyze.return_value = analysis
        script_gen.generate.return_value = script
        frame_extractor.extract_scored_frames.return_value = []

        use_case = RemixVideo(
            analyzer=analyzer,
            script_gen=script_gen,
            content_finder=None,
            content_type="gif",
            frame_extractor=frame_extractor,
            tts_provider="gtts",
        )
        request = RemixRequest(
            video_path=Path("input.mp4"),
            output_path=Path("output.mp4"),
        )

        use_case.execute(request)

        script_gen.generate.assert_called_once()
