"""Tests for OllamaScriptGenerator."""

from unittest.mock import patch


from adapters.ollama_script_generator import OllamaScriptGenerator
from domain.models import VideoAnalysis, Script


class TestOllamaScriptGenerator:
    """Tests for OllamaScriptGenerator."""

    @patch("adapters.ollama_script_generator.ollama")
    def test_generate_creates_script_from_analysis(self, mock_ollama) -> None:
        """Verify script is generated from video analysis."""
        mock_ollama.chat.return_value = {
            "message": {
                "content": '{"text": "Look at this cat doing funny things!", "duration_seconds": 30.0, "cues": [{"timestamp_start": 0.0, "timestamp_end": 10.0, "text": "Look at this cat!", "meme_url": null}]}'
            }
        }

        generator = OllamaScriptGenerator(model="llama3.2")
        analysis = VideoAnalysis(
            topic="funny cat",
            summary="A cat doing something funny",
            key_moments=["cat jumps"],
        )

        result = generator.generate(analysis)

        assert isinstance(result, Script)
        assert "cat" in result.text.lower()
        assert result.duration_seconds > 0
