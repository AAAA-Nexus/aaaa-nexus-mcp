"""Reputation ledger tools."""

from __future__ import annotations

from collections.abc import Callable

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_reputation_record(
        agent_id: str, success: bool, quality: float, latency_ms: float
    ) -> str:
        """Record an interaction outcome in the reputation ledger. $0.020/call."""
        return _fmt(
            await get_client().post(
                "/v1/reputation/record",
                {
                    "agent_id": agent_id,
                    "success": success,
                    "quality": quality,
                    "latency_ms": latency_ms,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_reputation_score(agent_id: str) -> str:
        """Get an agent's reputation tier and fee multiplier. $0.008/call."""
        return _fmt(await get_client().get(f"/v1/reputation/score/{agent_id}"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_reputation_history(agent_id: str) -> str:
        """Get exponential-decay weighted reputation history. $0.012/call."""
        return _fmt(await get_client().get(f"/v1/reputation/history/{agent_id}"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_reputation_dispute(entry_id: str, reason: str) -> str:
        """Challenge a reputation entry. $0.080/call."""
        return _fmt(
            await get_client().post(
                "/v1/reputation/dispute", {"entry_id": entry_id, "reason": reason}
            )
        )
