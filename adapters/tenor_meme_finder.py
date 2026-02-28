"""
Adapter: TenorMemeFinder

Searches for memes/GIFs using the Tenor API.
"""

import os
from typing import Any

import requests

from domain.models import Meme


class TenorMemeFinder:
    """Find memes using Tenor API."""

    BASE_URL = "https://tenor.googleapis.com/v2"

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key or os.environ.get("TENOR_API_KEY", "")

    def search(self, query: str, limit: int = 5) -> list[Meme]:
        """Search for memes matching the query."""
        params: dict[str, Any] = {
            "q": query,
            "limit": limit,
            "media_filter": "gif,tinygif",
            "contentfilter": "medium",
        }

        if self._api_key:
            params["key"] = self._api_key

        response = requests.get(f"{self.BASE_URL}/search", params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        return self._parse_results(data)

    def _parse_results(self, data: dict[str, Any]) -> list[Meme]:
        """Parse Tenor response into Meme objects."""
        memes = []

        for result in data.get("results", []):
            media_formats = result.get("media_formats", {})

            gif_format = media_formats.get("tinygif") or media_formats.get("gif")
            if not gif_format:
                continue

            dims = gif_format.get("dims", [0, 0])

            memes.append(
                Meme(
                    url=gif_format.get("url", ""),
                    width=dims[0] if len(dims) > 0 else 0,
                    height=dims[1] if len(dims) > 1 else 0,
                    title=result.get("content_description"),
                )
            )

        return memes
