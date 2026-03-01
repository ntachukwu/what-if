"""Tests for KlipyContentFinder."""

from unittest.mock import Mock, patch

from adapters.klipy_content_finder import KlipyContentFinder, ContentType
from domain.models import Meme


class TestKlipyContentFinder:
    """Tests for KlipyContentFinder."""

    @patch("adapters.klipy_content_finder.requests")
    def test_search_gifs_returns_content(self, mock_requests) -> None:
        """Verify GIFs are returned from Klipy API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "images": {
                        "original": {
                            "url": "https://example.com/1.gif",
                            "width": "200",
                            "height": "200",
                        },
                    },
                    "title": "funny cat",
                },
                {
                    "images": {
                        "original": {
                            "url": "https://example.com/2.gif",
                            "width": "300",
                            "height": "300",
                        },
                    },
                    "title": "lol",
                },
            ]
        }
        mock_requests.get.return_value = mock_response

        finder = KlipyContentFinder(api_key="test-key")
        results = finder.search_gifs("funny cat", limit=2)

        assert len(results) == 2
        assert results[0].content_type == ContentType.GIF

    @patch("adapters.klipy_content_finder.requests")
    def test_search_stickers_returns_content(self, mock_requests) -> None:
        """Verify stickers are returned from Klipy API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "images": {
                        "fixed_height": {
                            "url": "https://example.com/sticker.webp",
                            "width": "100",
                            "height": "100",
                        },
                    },
                    "title": "happy sticker",
                },
            ]
        }
        mock_requests.get.return_value = mock_response

        finder = KlipyContentFinder(api_key="test-key")
        results = finder.search_stickers("happy", limit=1)

        assert len(results) == 1
        assert results[0].content_type == ContentType.STICKER

    @patch("adapters.klipy_content_finder.requests")
    def test_search_clips_returns_content(self, mock_requests) -> None:
        """Verify clips are returned from Klipy API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "images": {
                        "original": {
                            "url": "https://example.com/clip.webm",
                            "width": "480",
                            "height": "270",
                        },
                    },
                    "title": "funny clip",
                },
            ]
        }
        mock_requests.get.return_value = mock_response

        finder = KlipyContentFinder(api_key="test-key")
        results = finder.search_clips("funny", limit=1)

        assert len(results) == 1
        assert results[0].content_type == ContentType.CLIP

    @patch("adapters.klipy_content_finder.requests")
    def test_to_memes_converts_content(self, mock_requests) -> None:
        """Verify KlipyContent can be converted to Meme."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "images": {
                        "original": {
                            "url": "https://example.com/1.gif",
                            "width": "200",
                            "height": "200",
                        },
                    },
                    "title": "test",
                },
            ]
        }
        mock_requests.get.return_value = mock_response

        finder = KlipyContentFinder()
        contents = finder.search_gifs("test", limit=1)
        memes = finder.to_memes(contents)

        assert len(memes) == 1
        assert isinstance(memes[0], Meme)
        assert memes[0].url == "https://example.com/1.gif"

    @patch("adapters.klipy_content_finder.requests")
    def test_trending_gifs(self, mock_requests) -> None:
        """Verify trending GIFs are returned."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "images": {
                        "original": {
                            "url": "https://example.com/trending.gif",
                            "width": "250",
                            "height": "250",
                        },
                    },
                    "title": "trending",
                },
            ]
        }
        mock_requests.get.return_value = mock_response

        finder = KlipyContentFinder()
        results = finder.trending_gifs(limit=1)

        assert len(results) == 1
        mock_requests.get.assert_called_once()
