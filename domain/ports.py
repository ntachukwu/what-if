"""
Ports — the contracts this application depends on.

These are interfaces (Python Protocols). The application layer only
ever talks to these. Adapters implement them.
"""

from pathlib import Path
from typing import Protocol

from domain.models import VideoAnalysis, Script, Meme, RemixResult, RemixRequest


class VideoAnalyzer(Protocol):
    """Analyze a video and extract its content."""

    def analyze(self, video_path: Path) -> VideoAnalysis:
        """Extract topic, summary, and key moments from video."""
        ...


class ScriptGenerator(Protocol):
    """Generate a script from video analysis."""

    def generate(self, analysis: VideoAnalysis) -> Script:
        """Create a script based on the video analysis."""
        ...


class MemeFinder(Protocol):
    """Find relevant memes/GIFs."""

    def search(self, query: str, limit: int = 5) -> list[Meme]:
        """Search for memes matching the query."""
        ...


class VideoCompositor(Protocol):
    """Compose the final video."""

    def compose(
        self, request: RemixRequest, script: Script, memes: list[Meme]
    ) -> RemixResult:
        """Combine video, script, and memes into final output."""
        ...
