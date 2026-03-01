"""
Adapter: TTS Service

Text-to-Speech using gTTS or Ollama.
"""

from pathlib import Path

from gtts import gTTS  # type: ignore[import-untyped]


class GTTSService:
    """Google TTS - free, fast, internet required."""

    def __init__(self, lang: str = "en", slow: bool = False) -> None:
        self.lang = lang
        self.slow = slow

    def generate(self, text: str, output_path: Path) -> Path:
        """Generate audio file from text."""
        tts = gTTS(text=text, lang=self.lang, slow=self.slow)
        tts.save(str(output_path))
        return output_path


class OllamaTTSService:
    """Ollama TTS - local, private, no internet needed."""

    def __init__(self, model: str = "llama3.2") -> None:
        self.model = model

    def generate(self, text: str, output_path: Path) -> Path:
        """Generate audio using Ollama (via chat with TTS output)."""
        import ollama

        prompt = f"""Generate a natural, conversational voiceover script from this text.
Make it sound like someone speaking casually to a camera.
Keep it the same length - don't add extra words.

Text: {text}

Output just the spoken text, nothing else:"""

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )

        spoken_text = response.message.content.strip()  # type: ignore[union-attr]

        tts = gTTS(text=spoken_text, lang="en", slow=False)
        tts.save(str(output_path))
        return output_path


def get_tts_service(provider: str) -> GTTSService | OllamaTTSService:
    """Get TTS service by provider name."""
    if provider == "ollama":
        return OllamaTTSService()
    return GTTSService()
