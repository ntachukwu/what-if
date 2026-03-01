"""
Adapter: MoviePyCompositor

Composites Fireship-style video with frames, memes, text, and audio.
"""

import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from moviepy import (  # type: ignore[import-untyped]
    ColorClip,
    CompositeVideoClip,
    CompositeAudioClip,
    ImageClip,
    TextClip,
    AudioFileClip,
)

from domain.models import RemixRequest, RemixResult, VideoSegment


class MoviePyCompositor:
    """Compose Fireship-style video with segments."""

    TARGET_SIZE = (1080, 1920)  # TikTok vertical
    FONTSIZE = 60
    TEXTCOLOR = "white"
    STROKECOLOR = "black"
    STROKEWIDTH = 3

    def compose(
        self,
        request: RemixRequest,
        segments: list[VideoSegment],
        audio_path: Path,
        background_color: str = "#0a0a0a",
    ) -> RemixResult:
        """Compose final video from segments."""
        try:
            bg_color = self._hex_to_rgb(background_color)
            background = ColorClip(size=self.TARGET_SIZE, color=bg_color, duration=0)
            background = background.with_fps(30)

            total_duration = max(s.start_time + s.duration for s in segments)
            background = background.with_duration(total_duration)

            clips = [background]

            for segment in segments:
                clip = self._create_segment_clip(segment)
                clips.append(clip)

            final = CompositeVideoClip(clips)

            audio = AudioFileClip(str(audio_path))
            final_audio = CompositeAudioClip([audio])
            final = final.with_audio(final_audio)

            final.write_videofile(
                str(request.output_path),
                codec="libx264",
                audio_codec="aac",
                fps=30,
                logger=None,
            )

            final.close()
            audio.close()

            return RemixResult(
                success=True,
                output_path=request.output_path,
            )

        except Exception as e:
            return RemixResult(
                success=False,
                error=str(e),
            )

    def _create_segment_clip(self, segment: VideoSegment) -> CompositeVideoClip:
        """Create a single segment clip with frame, meme, and text."""
        duration = segment.duration
        start_time = segment.start_time

        base = ColorClip(
            size=self.TARGET_SIZE,
            color=self._hex_to_rgb("#0a0a0a"),
            duration=duration,
        )
        base = base.with_fps(30)

        frame_clip = ImageClip(str(segment.frame_path), duration=duration)
        frame_clip = frame_clip.resized(height=self.TARGET_SIZE[1] * 0.7)
        frame_clip = frame_clip.with_position(("center", "top"))

        meme_clip = None
        if segment.meme_url:
            try:
                meme_path = self._download_meme(segment.meme_url)
                meme_clip = ImageClip(str(meme_path), duration=duration)
                meme_clip = meme_clip.resized(height=400)
                meme_clip = meme_clip.with_position(("center", "center"))
            except Exception:
                pass

        text_clip = TextClip(
            text=segment.text,
            font_size=self.FONTSIZE,
            color=self.TEXTCOLOR,
            stroke_color=self.STROKECOLOR,
            stroke_width=self.STROKEWIDTH,
            method="caption",
            size=(self.TARGET_SIZE[0] - 100, None),
            duration=duration,
        )
        text_clip = text_clip.with_position(("center", "bottom"))

        all_clips = [base, frame_clip, text_clip]
        if meme_clip:
            all_clips.append(meme_clip)

        composite = CompositeVideoClip(all_clips)
        composite = composite.with_start(start_time)

        return composite

    def _download_meme(self, url: str) -> Path:
        """Download meme to temp file."""
        req = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            },
        )
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as f:
            with urlopen(req, timeout=30) as response:
                f.write(response.read())
            return Path(f.name)

    def _hex_to_rgb(self, hex_color: str) -> tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )  # type: ignore[return-value]
