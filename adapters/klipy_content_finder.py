"""
Adapter: KlipyContentFinder

Searches for GIFs, Stickers, and Clips using the Klipy API.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

import requests

from domain.models import Meme


class ContentType(Enum):
    """Types of content available in Klipy."""

    GIF = "gifs"
    STICKER = "stickers"
    CLIP = "clips"
    MEME = "memes"


@dataclass(frozen=True)
class KlipyContent:
    """A piece of content from Klipy."""

    url: str
    width: int
    height: int
    title: str | None = None
    content_type: ContentType = ContentType.GIF


class KlipyContentFinder:
    """Find GIFs, Stickers, and Clips using Klipy API."""

    BASE_URL = "https://api.klipy.com/v2"

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key

    def search_gifs(self, query: str, limit: int = 10) -> list[KlipyContent]:
        """Search for GIFs matching the query."""
        return self._search(query, ContentType.GIF, limit)

    def search_stickers(self, query: str, limit: int = 10) -> list[KlipyContent]:
        """Search for stickers matching the query."""
        return self._search(query, ContentType.STICKER, limit)

    def search_clips(self, query: str, limit: int = 10) -> list[KlipyContent]:
        """Search for clips matching the query."""
        return self._search(query, ContentType.CLIP, limit)

    def search_memes(self, query: str, limit: int = 10) -> list[KlipyContent]:
        """Search for memes matching the query."""
        return self._search(query, ContentType.MEME, limit)

    def trending_gifs(self, limit: int = 10) -> list[KlipyContent]:
        """Get trending GIFs."""
        return self._trending(ContentType.GIF, limit)

    def trending_stickers(self, limit: int = 10) -> list[KlipyContent]:
        """Get trending stickers."""
        return self._trending(ContentType.STICKER, limit)

    def trending_clips(self, limit: int = 10) -> list[KlipyContent]:
        """Get trending clips."""
        return self._trending(ContentType.CLIP, limit)

    def trending_memes(self, limit: int = 10) -> list[KlipyContent]:
        """Get trending memes."""
        return self._trending(ContentType.MEME, limit)

    def _search(
        self, query: str, content_type: ContentType, limit: int
    ) -> list[KlipyContent]:
        """Search for content."""
        params: dict[str, Any] = {
            "query": query,
            "limit": limit,
        }

        if self._api_key:
            params["key"] = self._api_key

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = requests.get(
            f"{self.BASE_URL}/{content_type.value}/search",
            params=params,
            headers=headers,
            timeout=10,
            allow_redirects=True,
        )
        response.raise_for_status()

        data = response.json()
        return self._parse_results(data, content_type)

    def _trending(self, content_type: ContentType, limit: int) -> list[KlipyContent]:
        """Get trending content."""
        params: dict[str, Any] = {
            "limit": limit,
        }

        if self._api_key:
            params["key"] = self._api_key

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = requests.get(
            f"{self.BASE_URL}/{content_type.value}/trending",
            params=params,
            headers=headers,
            timeout=10,
            allow_redirects=True,
        )
        response.raise_for_status()

        data = response.json()
        return self._parse_results(data, content_type)

    def _parse_results(
        self, data: dict[str, Any], content_type: ContentType
    ) -> list[KlipyContent]:
        """Parse Klipy v2 response into KlipyContent objects."""
        contents = []

        results = data.get("data", [])
        for item in results:
            images = item.get("images", {})

            img_format = (
                images.get("original")
                or images.get("fixed_height")
                or images.get("downsized_medium")
            )
            if not img_format:
                continue

            url = img_format.get("url", "")
            width = int(img_format.get("width", 0) or 0)
            height = int(img_format.get("height", 0) or 0)

            if not url:
                continue

            contents.append(
                KlipyContent(
                    url=url,
                    width=width,
                    height=height,
                    title=item.get("title"),
                    content_type=content_type,
                )
            )

        return contents

    def to_memes(self, contents: list[KlipyContent]) -> list[Meme]:
        """Convert KlipyContent to Meme objects for compatibility."""
        return [
            Meme(
                url=c.url,
                width=c.width,
                height=c.height,
                title=c.title,
            )
            for c in contents
        ]
