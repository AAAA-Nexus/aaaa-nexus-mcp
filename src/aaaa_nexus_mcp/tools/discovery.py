"""Agent discovery tools -- search, recommend, registry."""

from __future__ import annotations

from collections.abc import Callable

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_discovery_search(capability: str) -> str:
        """Search for agents by capability, reputation-ranked. $0.060/call."""
        return _fmt(await get_client().post("/v1/discovery/search", {"capability": capability}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_discovery_recommend(task: str) -> str:
        """Get AI-ranked agent recommendations from a task description. $0.040/call."""
        return _fmt(await get_client().post("/v1/discovery/recommend", {"task": task}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_discovery_registry() -> str:
        """Browse all registered agents in the registry. $0.020/call."""
        return _fmt(await get_client().get("/v1/discovery/registry"))
