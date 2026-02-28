#!/usr/bin/env python3
"""
CLI entry point for what-if video remix.
"""

import os
from pathlib import Path

import click
from dotenv import load_dotenv

from adapters.moviepy_compositor import MoviePyCompositor
from adapters.openai_script_generator import OpenAIScriptGenerator
from adapters.openai_video_analyzer import OpenAIVideoAnalyzer
from adapters.tenor_meme_finder import TenorMemeFinder
from app.use_cases import RemixVideo
from domain.models import RemixRequest


def get_api_key(env_var: str) -> str:
    """Get API key from env or fail."""
    key = os.environ.get(env_var, "")
    if not key:
        raise click.ClickException(f"Missing {env_var}. Set it in .env or export it.")
    return key


@click.command()
@click.argument("input_video", type=click.Path(exists=True, path_type=Path))
@click.argument("output_video", type=click.Path(path_type=Path))
@click.option(
    "--openai-key",
    env_var="OPENAI_API_KEY",
    help="OpenAI API key (or set OPENAI_API_KEY env var)",
)
@click.option(
    "--tenor-key",
    env_var="TENOR_API_KEY",
    help="Tenor API key (optional, for higher rate limits)",
)
@click.option("--skip-memes", is_flag=True, help="Skip meme search")
def main(
    input_video: Path,
    output_video: Path,
    openai_key: str | None,
    tenor_key: str | None,
    skip_memes: bool,
) -> None:
    """Remix INPUT_VIDEO to OUTPUT_VIDEO with AI-generated content."""
    load_dotenv()

    openai_key = openai_key or get_api_key("OPENAI_API_KEY")
    tenor_key = tenor_key or os.environ.get("TENOR_API_KEY", "")

    click.echo(f"📹 Analyzing: {input_video}")

    analyzer = OpenAIVideoAnalyzer(api_key=openai_key)
    script_gen = OpenAIScriptGenerator(api_key=openai_key)
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

    click.echo("🤖 Analyzing video...")
    result = remix.execute(request)

    if result.success:
        click.echo(f"✅ Done! Output: {result.output_path}")
    else:
        raise click.ClickException(f"Failed: {result.error}")


if __name__ == "__main__":
    main()
