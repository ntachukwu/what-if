"""
Adapter: MoviePyCompositor

Composes final video using MoviePy.
"""

from moviepy import CompositeVideoClip, ImageClip, VideoFileClip  # type: ignore[import-untyped]

from domain.models import Script, Meme, RemixRequest, RemixResult


class MoviePyCompositor:
    """Compose video with overlays using MoviePy."""

    TARGET_SIZE = (1080, 1920)  # TikTok vertical

    def compose(
        self, request: RemixRequest, script: Script, memes: list[Meme]
    ) -> RemixResult:
        """Compose final video with meme overlays."""
        try:
            video = VideoFileClip(str(request.video_path))

            video = video.resize(newsize=self.TARGET_SIZE)

            clips = [video]

            for meme in memes[:3]:
                meme_clip = ImageClip(meme.url, duration=3.0)
                meme_clip = meme_clip.resize(height=300)
                meme_clip = meme_clip.set_position(("right", "bottom"))
                clips.append(meme_clip)

            final = CompositeVideoClip(clips)

            final.write_videofile(
                str(request.output_path),
                codec="libx264",
                audio_codec="aac",
                fps=30,
                verbose=False,
                logger=None,
            )

            video.close()
            final.close()

            return RemixResult(
                success=True,
                output_path=request.output_path,
            )

        except Exception as e:
            return RemixResult(
                success=False,
                error=str(e),
            )
