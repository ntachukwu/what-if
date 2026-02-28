"""Tests for OpenAIScriptGenerator."""

from unittest.mock import Mock, patch


from adapters.openai_script_generator import OpenAIScriptGenerator
from domain.models import VideoAnalysis, Script


class TestOpenAIScriptGenerator:
    """Tests for OpenAIScriptGenerator."""

    @patch("adapters.openai_script_generator.OpenAI")
    def test_generate_creates_script_from_analysis(self, mock_openai_class) -> None:
        """Verify script is generated from video analysis."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"text": "Look at this cat doing funny things!", "duration_seconds": 30.0, "cues": [{"timestamp_start": 0.0, "timestamp_end": 10.0, "text": "Look at this cat!", "meme_url": null}]}'
                    )
                )
            ]
        )

        generator = OpenAIScriptGenerator(api_key="test-key")
        analysis = VideoAnalysis(
            topic="funny cat",
            summary="A cat doing something funny",
            key_moments=["cat jumps"],
        )

        result = generator.generate(analysis)

        assert isinstance(result, Script)
        assert "cat" in result.text.lower()
        assert result.duration_seconds > 0
