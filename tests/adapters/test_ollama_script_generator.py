"""Tests for OllamaScriptGenerator."""

from unittest.mock import patch


from adapters.ollama_script_generator import OllamaScriptGenerator
from domain.models import VideoAnalysis, Script


class TestOllamaScriptGenerator:
    """Tests for OllamaScriptGenerator."""

    @patch("adapters.ollama_script_generator.ollama")
    def test_generate_creates_fireship_style_script(self, mock_ollama) -> None:
        """Verify Fireship-style script is generated."""
        mock_ollama.chat.return_value = {
            "message": {
                "content": """{
  "title": "Wakanda Puns Be Like",
  "segments": [
    {"text": "Wakanda forever... or until the next Marvel movie!", "keywords": ["marvel"], "effect": "zoom"},
    {"text": "This is giving main character energy", "keywords": ["comedy"], "effect": "flash"}
  ],
  "intro": "Wait, you didn't know?",
  "outro": "Subscribe for more!"
}"""
            }
        }

        generator = OllamaScriptGenerator(model="llama3.2", num_segments=2)
        analysis = VideoAnalysis(
            topic="Black Panther",
            summary="Wakanda puns comedy",
            key_moments=["pun 1", "pun 2"],
            humor_style="sarcastic",
        )

        result = generator.generate(analysis)

        assert isinstance(result, Script)
        assert result.duration_seconds > 0
        assert len(result.cues) > 0
