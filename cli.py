#!/usr/bin/env python3
"""
CLI entry point for what-if video remix.
"""

import os
from pathlib import Path

import click  # type: ignore[import-untyped]
from dotenv import load_dotenv

from adapters.moviepy_compositor import MoviePyCompositor
from adapters.ollama_script_generator import OllamaScriptGenerator
from adapters.ollama_video_analyzer import OllamaVideoAnalyzer
from adapters.tenor_meme_finder import TenorMemeFinder
from app.use_cases import RemixVideo
from domain.models import RemixRequest


@click.command()
@click.argument("input_video", type=click.Path(exists=True, path_type=Path))
@click.argument("output_video", type=click.Path(path_type=Path))
@click.option(
    "--vision-model",
    default="llava:7b",
    help="Ollama vision model (default: llava:7b)",
)
@click.option(
    "--llm-model",
    default="llama3.2",
    help="Ollama LLM model for script generation (default: llama3.2)",
)
@click.option(
    "--tenor-key",
    envvar="TENOR_API_KEY",
    help="Tenor API key (optional, for higher rate limits)",
)
@click.option("--skip-memes", is_flag=True, help="Skip meme search")
def main(
    input_video: Path,
    output_video: Path,
    vision_model: str,
    llm_model: str,
    tenor_key: str | None,
    skip_memes: bool,
) -> None:
    """Remix INPUT_VIDEO to OUTPUT_VIDEO with AI-generated content."""
    load_dotenv()

    tenor_key = tenor_key or os.environ.get("TENOR_API_KEY", "")

    click.echo(f"📹 Analyzing: {input_video}")

    analyzer = OllamaVideoAnalyzer(model=vision_model)
    script_gen = OllamaScriptGenerator(model=llm_model)
    meme_finder = TenorMemeFinder(api_key=tenor_key) if not skip_memes else None
    compositor = MoviePyCompositor()

    remix = RemixVideo(
        analyzer=analyzer,
        script_gen=script_gen,
        meme_finder=meme_finder,  # type: ignore[arg-type]
        compositor=compositor,
    )

    request = RemixRequest(
        video_path=input_video,
        output_path=output_video,
    )

    click.echo(f"🤖 Analyzing with {vision_model}...")
    result = remix.execute(request)

    if result.success:
        click.echo(f"✅ Done! Output: {result.output_path}")
    else:
        raise click.ClickException(f"Failed: {result.error}")


if __name__ == "__main__":
    main()
