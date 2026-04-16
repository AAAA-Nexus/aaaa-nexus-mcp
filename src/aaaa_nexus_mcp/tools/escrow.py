"""Agent escrow tools."""

from __future__ import annotations

from collections.abc import Callable

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_escrow_create(
        amount_usdc: float, sender: str, receiver: str, conditions: list[str]
    ) -> str:
        """Lock USDC in escrow with release conditions. $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/escrow/create",
                {
                    "amount_usdc": amount_usdc,
                    "sender": sender,
                    "receiver": receiver,
                    "conditions": conditions,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_escrow_release(escrow_id: str, proof: str) -> str:
        """Release escrow funds with completion proof. $0.020/call."""
        return _fmt(
            await get_client().post("/v1/escrow/release", {"escrow_id": escrow_id, "proof": proof})
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_escrow_status(escrow_id: str) -> str:
        """Check escrow state. $0.008/call."""
        return _fmt(await get_client().get(f"/v1/escrow/status/{escrow_id}"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_escrow_dispute(escrow_id: str, evidence: str) -> str:
        """Open escrow dispute with evidence. $0.060/call."""
        return _fmt(
            await get_client().post(
                "/v1/escrow/dispute", {"escrow_id": escrow_id, "evidence": evidence}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_escrow_arbitrate(escrow_id: str, vote: str) -> str:
        """Cast arbiter vote in escrow dispute (3-vote majority). $0.020/call."""
        return _fmt(
            await get_client().post("/v1/escrow/arbitrate", {"escrow_id": escrow_id, "vote": vote})
        )
