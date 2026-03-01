"""
Domain models.

Pure data — no I/O, no dependencies, no framework.
These are the nouns of the application.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VideoAnalysis:
    """Result of analyzing a video."""

    topic: str
    summary: str
    key_moments: list[str]
    humor_style: str | None = None


@dataclass(frozen=True)
class Script:
    """A generated script for the video."""

    text: str
    duration_seconds: float
    cues: list["ScriptCue"]


@dataclass(frozen=True)
class ScriptCue:
    """A single cue in the script."""

    timestamp_start: float
    timestamp_end: float
    text: str
    meme_url: str | None = None


@dataclass(frozen=True)
class Meme:
    """A meme/GIF from the search results."""

    url: str
    width: int
    height: int
    title: str | None = None


@dataclass(frozen=True)
class RemixRequest:
    """Everything needed to remix a video."""

    video_path: Path
    output_path: Path
    num_segments: int = 12
    tts_provider: str = "gtts"
    background_color: str = "#0a0a0a"


@dataclass(frozen=True)
class VideoSegment:
    """A segment in the final remixed video."""

    frame_path: Path
    original_timestamp: float
    text: str
    meme_url: str | None = None
    start_time: float = 0.0
    duration: float = 4.0
    caption: str | None = None


@dataclass(frozen=True)
class RemixResult:
    """Outcome of a remixed video."""

    success: bool
    output_path: Path | None = None
    error: str | None = None
