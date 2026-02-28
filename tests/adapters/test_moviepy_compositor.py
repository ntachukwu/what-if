"""Tests for MoviePyCompositor."""

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


from adapters.moviepy_compositor import MoviePyCompositor
from domain.models import Script, ScriptCue, Meme, RemixRequest, RemixResult


class TestMoviePyCompositor:
    """Tests for MoviePyCompositor."""

    @patch("adapters.moviepy_compositor.VideoFileClip")
    @patch("adapters.moviepy_compositor.CompositeVideoClip")
    @patch("adapters.moviepy_compositor.ImageClip")
    def test_compose_creates_video(
        self, mock_image_clip, mock_composite, mock_video_file
    ) -> None:
        """Verify video is composed with overlays."""
        mock_video = MagicMock()
        mock_video_file.return_value = mock_video
        mock_video.size = (1920, 1080)
        mock_video.duration = 30

        mock_composite.return_value = MagicMock()

        mock_result = Mock()
        mock_result.write_videofile = Mock()

        mock_composite.return_value = mock_result

        compositor = MoviePyCompositor()

        request = RemixRequest(
            video_path=Path("input.mp4"),
            output_path=Path("output.mp4"),
        )
        script = Script(
            text="Test script",
            duration_seconds=30.0,
            cues=[
                ScriptCue(0.0, 10.0, "Hello!", None),
            ],
        )
        memes = [
            Meme(url="https://example.com/meme.gif", width=200, height=200),
        ]

        result = compositor.compose(request, script, memes)

        assert isinstance(result, RemixResult)
        assert result.success is True
