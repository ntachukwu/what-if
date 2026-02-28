"""Tests for TenorMemeFinder."""

from unittest.mock import Mock, patch


from adapters.tenor_meme_finder import TenorMemeFinder
from domain.models import Meme


class TestTenorMemeFinder:
    """Tests for TenorMemeFinder."""

    @patch("adapters.tenor_meme_finder.requests")
    def test_search_returns_memes(self, mock_requests) -> None:
        """Verify memes are returned from Tenor API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "media_formats": {
                        "tinygif": {
                            "url": "https://example.com/1.gif",
                            "dims": [200, 200],
                        },
                    },
                    "content_description": "funny cat",
                },
                {
                    "media_formats": {
                        "tinygif": {
                            "url": "https://example.com/2.gif",
                            "dims": [300, 300],
                        },
                    },
                    "content_description": "lol",
                },
            ]
        }
        mock_requests.get.return_value = mock_response

        finder = TenorMemeFinder(api_key="test-key")
        results = finder.search("funny cat", limit=2)

        assert len(results) == 2
        assert all(isinstance(m, Meme) for m in results)
