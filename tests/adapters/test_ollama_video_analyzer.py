"""Tests for OllamaVideoAnalyzer."""

from pathlib import Path
from unittest.mock import Mock, patch


from adapters.ollama_video_analyzer import OllamaVideoAnalyzer
from domain.models import VideoAnalysis


class TestOllamaVideoAnalyzer:
    """Tests for OllamaVideoAnalyzer."""

    @patch("adapters.ollama_video_analyzer.cv2")
    @patch("adapters.ollama_video_analyzer.ollama")
    def test_analyze_extracts_frames_and_calls_ollama(
        self, mock_ollama, mock_cv2
    ) -> None:
        """Verify frames are extracted and sent to Ollama."""
        mock_video = Mock()
        mock_cv2.VideoCapture.return_value = mock_video
        mock_video.isOpened.return_value = True
        mock_video.get.return_value = 30.0
        mock_video.read.side_effect = [
            (True, "frame1"),
            (True, "frame2"),
            (False, None),
        ]
        mock_video.release.return_value = None

        mock_imencode = Mock(return_value=(True, b"encoded"))
        mock_cv2.imencode = mock_imencode

        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"topic": "funny cat", "summary": "A cat doing something funny", "key_moments": ["cat jumps"], "humor_style": "comedy"}'
            }
        }

        analyzer = OllamaVideoAnalyzer(model="llava:7b")
        result = analyzer.analyze(Path("test.mp4"))

        assert isinstance(result, VideoAnalysis)
        assert result.topic == "funny cat"
        assert result.summary == "A cat doing something funny"
        assert "cat jumps" in result.key_moments
