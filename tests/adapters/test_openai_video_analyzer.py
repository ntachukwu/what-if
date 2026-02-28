"""Tests for the OpenAIVideoAnalyzer adapter."""

from pathlib import Path
from unittest.mock import Mock, patch


from adapters.openai_video_analyzer import OpenAIVideoAnalyzer
from domain.models import VideoAnalysis


class TestOpenAIVideoAnalyzer:
    """Tests for OpenAIVideoAnalyzer."""

    @patch("adapters.openai_video_analyzer.cv2")
    @patch("adapters.openai_video_analyzer.OpenAI")
    def test_analyze_extracts_frames_and_calls_openai(
        self, mock_openai_class, mock_cv2
    ) -> None:
        """Verify frames are extracted and sent to OpenAI."""
        mock_video = Mock()
        mock_cv2.VideoCapture.return_value = mock_video
        mock_video.isOpened.return_value = True
        mock_video.get.return_value = 30.0  # Mock FPS
        mock_video.read.side_effect = [
            (True, "frame1"),
            (True, "frame2"),
            (False, None),
        ]
        mock_video.release.return_value = None

        mock_imencode = Mock(return_value=(True, b"encoded"))
        mock_cv2.imencode = mock_imencode

        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"topic": "funny cat", "summary": "A cat doing something funny", "key_moments": ["cat jumps"], "humor_style": "comedy"}'
                    )
                )
            ]
        )

        analyzer = OpenAIVideoAnalyzer(api_key="test-key")
        result = analyzer.analyze(Path("test.mp4"))

        assert isinstance(result, VideoAnalysis)
        assert result.topic == "funny cat"
        assert result.summary == "A cat doing something funny"
        assert "cat jumps" in result.key_moments
