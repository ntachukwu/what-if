"""
Application layer — use cases that orchestrate the domain.

These coordinate the ports (adapters) to fulfill user requests.
"""


from domain.models import RemixRequest, RemixResult
from domain.ports import VideoAnalyzer, ScriptGenerator, MemeFinder, VideoCompositor


class RemixVideo:
    """Orchestrate the video remix pipeline."""

    def __init__(
        self,
        analyzer: VideoAnalyzer,
        script_gen: ScriptGenerator,
        meme_finder: MemeFinder,
        compositor: VideoCompositor,
    ) -> None:
        self._analyzer = analyzer
        self._script_gen = script_gen
        self._meme_finder = meme_finder
        self._compositor = compositor

    def execute(self, request: RemixRequest) -> RemixResult:
        """Run the full remix pipeline."""
        analysis = self._analyzer.analyze(request.video_path)

        script = self._script_gen.generate(analysis)

        memes = self._meme_finder.search(analysis.topic, limit=5)

        return self._compositor.compose(request, script, memes)
