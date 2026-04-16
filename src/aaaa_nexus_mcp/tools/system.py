"""System & discovery tools (free endpoints)."""

from __future__ import annotations

from collections.abc import Callable

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_health() -> str:
        """Check AAAA-Nexus API health status. Free."""
        return _fmt(await get_client().get("/health"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_metrics() -> str:
        """Get aggregated platform telemetry metrics. Free."""
        return _fmt(await get_client().get("/v1/metrics"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_pricing() -> str:
        """Get machine-readable pricing manifest for all endpoints. Free."""
        return _fmt(await get_client().get("/.well-known/pricing.json"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_agent_card() -> str:
        """Get the A2A agent capability manifest. Free."""
        return _fmt(await get_client().get("/.well-known/agent.json"))
