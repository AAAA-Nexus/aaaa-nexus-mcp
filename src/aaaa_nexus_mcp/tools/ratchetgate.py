"""RatchetGate session security tools."""

from __future__ import annotations

from collections.abc import Callable

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_ratchet_register(agent_id: int) -> str:
        """Start a new RatchetGate session with 47-epoch cycle. agent_id must be multiple of 324 (G_18). $0.008/call."""
        return _fmt(await get_client().post("/v1/ratchet/register", {"agent_id": agent_id}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_ratchet_advance(session_id: str) -> str:
        """Advance session epoch and re-key. $0.008/call."""
        return _fmt(await get_client().post("/v1/ratchet/advance", {"session_id": session_id}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_ratchet_probe(session_ids: list[str]) -> str:
        """Batch liveness check for up to 100 sessions. $0.008/call."""
        return _fmt(await get_client().post("/v1/ratchet/probe", {"session_ids": session_ids}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_ratchet_status(session_id: str) -> str:
        """Get session epoch + remaining calls. $0.004/call."""
        return _fmt(await get_client().get(f"/v1/ratchet/status/{session_id}"))
