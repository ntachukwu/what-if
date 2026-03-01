"""Tests for MoviePyCompositor."""

from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


from adapters.moviepy_compositor import MoviePyCompositor
from domain.models import RemixRequest, RemixResult, VideoSegment


class TestMoviePyCompositor:
    """Tests for MoviePyCompositor."""

    @patch("adapters.moviepy_compositor.AudioFileClip")
    @patch("adapters.moviepy_compositor.CompositeVideoClip")
    @patch("adapters.moviepy_compositor.CompositeAudioClip")
    @patch("adapters.moviepy_compositor.ColorClip")
    @patch("adapters.moviepy_compositor.ImageClip")
    @patch("adapters.moviepy_compositor.TextClip")
    def test_compose_creates_video(
        self,
        mock_text_clip,
        mock_image_clip,
        mock_color_clip,
        mock_composite_audio,
        mock_composite,
        mock_audio,
    ) -> None:
        """Verify video is composed with segments."""
        mock_audio.return_value = MagicMock()

        mock_text = MagicMock()
        mock_text.with_start = MagicMock(return_value=mock_text)
        mock_text_clip.return_value = mock_text

        mock_img = MagicMock()
        mock_img.with_start = MagicMock(return_value=mock_img)
        mock_image_clip.return_value = mock_img

        mock_bg = MagicMock()
        mock_bg.with_fps = MagicMock(return_value=mock_bg)
        mock_bg.with_duration = MagicMock(return_value=mock_bg)
        mock_color_clip.return_value = mock_bg

        mock_composite.return_value = MagicMock()
        mock_result = Mock()
        mock_result.write_videofile = Mock()
        mock_composite.return_value = mock_result

        compositor = MoviePyCompositor()

        request = RemixRequest(
            video_path=Path("input.mp4"),
            output_path=Path("output.mp4"),
            num_segments=2,
        )

        audio_path = Path("temp.mp3")
        segments = [
            VideoSegment(
                frame_path=Path("frame1.jpg"),
                original_timestamp=0.0,
                text="Bold text!",
                meme_url=None,
                start_time=0.0,
                duration=4.0,
            ),
            VideoSegment(
                frame_path=Path("frame2.jpg"),
                original_timestamp=5.0,
                text="More text!",
                meme_url=None,
                start_time=4.0,
                duration=4.0,
            ),
        ]

        result = compositor.compose(
            request=request,
            segments=segments,
            audio_path=audio_path,
            background_color="#0a0a0a",
        )

        assert isinstance(result, RemixResult)
