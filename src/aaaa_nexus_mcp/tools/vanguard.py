"""NEXUS VANGUARD risk governance tools."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_vanguard_redteam(agent_id: str, target: str) -> str:
        """Run continuous red-team audit against a target. $0.100/call."""
        return _fmt(
            await get_client().post(
                "/v1/vanguard/continuous-redteam", {"agent_id": agent_id, "target": target}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_vanguard_mev_route(agent_id: str, intent: dict[str, Any] | None = None) -> str:
        """Route an intent through MEV governance. $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/vanguard/mev/route-intent", {"agent_id": agent_id, "intent": intent or {}}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_vanguard_govern_session(agent_id: str, session_key: str = "") -> str:
        """UCAN wallet session governance control. $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/vanguard/wallet/govern-session",
                {"agent_id": agent_id, "session_key": session_key},
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_vanguard_lock_verify(
        payer_agent_id: str, payee_agent_id: str, amount_micro_usdc: int
    ) -> str:
        """Lock USDC in escrow and verify both parties (Vanguard). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/vanguard/escrow/lock-and-verify",
                {
                    "payer_agent_id": payer_agent_id,
                    "payee_agent_id": payee_agent_id,
                    "amount_micro_usdc": amount_micro_usdc,
                },
            )
        )
