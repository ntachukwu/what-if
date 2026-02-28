"""Tests for the RemixVideo use case."""

from pathlib import Path
from unittest.mock import Mock


from app.use_cases import RemixVideo
from domain.models import (
    VideoAnalysis,
    Script,
    Meme,
    RemixRequest,
    RemixResult,
)


class TestRemixVideo:
    """Tests for RemixVideo orchestrator."""

    def test_executes_full_pipeline(self) -> None:
        """Verify all steps are called in order."""
        analyzer = Mock()
        script_gen = Mock()
        meme_finder = Mock()
        compositor = Mock()

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
        memes = [Meme(url="http://example.com/meme.gif", width=200, height=200)]

        analyzer.analyze.return_value = analysis
        script_gen.generate.return_value = script
        meme_finder.search.return_value = memes
        compositor.compose.return_value = RemixResult(
            success=True,
            output_path=Path("output.mp4"),
        )

        use_case = RemixVideo(analyzer, script_gen, meme_finder, compositor)
        request = RemixRequest(
            video_path=Path("input.mp4"),
            output_path=Path("output.mp4"),
        )

        result = use_case.execute(request)

        analyzer.analyze.assert_called_once_with(Path("input.mp4"))
        script_gen.generate.assert_called_once_with(analysis)
        meme_finder.search.assert_called_once_with("funny cat", limit=5)
        compositor.compose.assert_called_once()

        assert result.success is True
        assert result.output_path == Path("output.mp4")
