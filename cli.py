#!/usr/bin/env python3
"""
CLI entry point for what-if video remix.
"""

import os
from pathlib import Path

import click  # type: ignore[import-untyped]
from dotenv import load_dotenv

from adapters.frame_extractor import OllamaFrameExtractor
from adapters.klipy_content_finder import KlipyContentFinder
from adapters.ollama_script_generator import OllamaScriptGenerator
from adapters.ollama_video_analyzer import OllamaVideoAnalyzer
from app.use_cases import RemixVideo
from domain.models import RemixRequest


@click.command()
@click.argument("input_video", type=click.Path(exists=True, path_type=Path))
@click.argument("output_video", type=click.Path(path_type=Path))
@click.option(
    "--vision-model",
    default="llava:7b",
    help="Ollama vision model for frame extraction (default: llava:7b)",
)
@click.option(
    "--llm-model",
    default="llama3.2",
    help="Ollama LLM model for script generation (default: llama3.2)",
)
@click.option(
    "--klipy-key",
    envvar="KLIPY_API_KEY",
    help="Klipy API key (get from partner.klipy.com)",
)
@click.option(
    "--content-type",
    type=click.Choice(["gif", "sticker", "clip", "meme"], case_sensitive=False),
    default="gif",
    help="Type of content to search (default: gif)",
)
@click.option(
    "--tts-provider",
    type=click.Choice(["gtts", "ollama"], case_sensitive=False),
    default="gtts",
    help="TTS provider (default: gtts)",
)
@click.option(
    "--segments",
    default=12,
    help="Number of segments in output video (default: 12)",
)
@click.option(
    "--background",
    default="#0a0a0a",
    help="Background color (default: #0a0a0a)",
)
@click.option(
    "--skip-content",
    is_flag=True,
    help="Skip meme/GIF search",
)
def main(
    input_video: Path,
    output_video: Path,
    vision_model: str,
    llm_model: str,
    klipy_key: str | None,
    content_type: str,
    tts_provider: str,
    segments: int,
    background: str,
    skip_content: bool,
) -> None:
    """Remix INPUT_VIDEO to OUTPUT_VIDEO Fireship-style."""
    load_dotenv()

    klipy_key = klipy_key or os.environ.get("KLIPY_API_KEY", "")

    click.echo(f"📹 Remixing: {input_video}")

    analyzer = OllamaVideoAnalyzer(model=vision_model)
    script_gen = OllamaScriptGenerator(model=llm_model, num_segments=segments)
    frame_extractor = OllamaFrameExtractor(model=vision_model, num_selected=segments)

    content_finder: KlipyContentFinder | None = None
    if not skip_content:
        content_finder = KlipyContentFinder(api_key=klipy_key)

    remix = RemixVideo(
        analyzer=analyzer,
        script_gen=script_gen,
        content_finder=content_finder,
        content_type=content_type,
        frame_extractor=frame_extractor,
        tts_provider=tts_provider,
    )

    request = RemixRequest(
        video_path=input_video,
        output_path=output_video,
        num_segments=segments,
        tts_provider=tts_provider,
        background_color=background,
    )

    result = remix.execute(request)

    if result.success:
        click.echo(f"✅ Done! Output: {result.output_path}")
    else:
        raise click.ClickException(f"Failed: {result.error}")


if __name__ == "__main__":
    main()
