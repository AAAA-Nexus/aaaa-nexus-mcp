"""AI inference and text analysis tools."""

from __future__ import annotations

from collections.abc import Callable

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_inference(prompt: str) -> str:
        """Run AI inference. $0.060/call."""
        return _fmt(await get_client().post("/v1/inference", {"prompt": prompt}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_embed(values: list[float]) -> str:
        """Generate HELIX compressed embedding from float values. $0.040/call."""
        return _fmt(await get_client().post("/v1/embed", {"values": values}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_text_summarize(text: str) -> str:
        """Generate 1-3 sentence extractive summary. $0.040/call."""
        return _fmt(await get_client().post("/v1/text/summarize", {"text": text}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_text_keywords(text: str, top_k: int = 10) -> str:
        """Extract keywords using TF-IDF. $0.020/call."""
        return _fmt(await get_client().post("/v1/text/keywords", {"text": text, "top_k": top_k}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_text_sentiment(text: str) -> str:
        """Analyze sentiment -- positive, negative, or neutral. $0.020/call."""
        return _fmt(await get_client().post("/v1/text/sentiment", {"text": text}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_routing_think(query: str) -> str:
        """Classify query complexity and recommend model tier (POP-1207). $0.040/call."""
        return _fmt(await get_client().post("/v1/routing/think", {"query": query}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_routing_recommend(task: str) -> str:
        """Map task to optimal model and routing tier. $0.020/call."""
        return _fmt(await get_client().post("/v1/routing/recommend", {"task": task}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_memory_trim(context: list[dict], target_tokens: int) -> str:
        """Prune context window for cost efficiency (INF-815). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/memory/trim", {"context": context, "target_tokens": target_tokens}
            )
        )
