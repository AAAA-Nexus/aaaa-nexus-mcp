"""Control plane tools — authorization, spending, lineage, contracts, federation."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_authorize_action(agent_id: str, action: str, delegation_depth: int = 0) -> str:
        """Pre-action authorization gateway (OAP-100). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/authorize/action",
                {
                    "agent_id": agent_id,
                    "action": action,
                    "delegation_depth": delegation_depth,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_spending_authorize(agent_id: str, amount_usdc: float, epoch: int = 0) -> str:
        """Trust-decay spending bound authorization (SPG-100). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/spending/authorize",
                {
                    "agent_id": agent_id,
                    "amount_usdc": amount_usdc,
                    "epoch": epoch,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_spending_budget(chain: list[dict[str, Any]], total_usdc: float = 0.0) -> str:
        """Multi-hop chain budget calculation (SPG-101). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/spending/budget", {"chain": chain, "total_usdc": total_usdc}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_lineage_record(intent: str, constraints: list[str], outcome: str) -> str:
        """Record a hash-chained decision in the lineage vault (DLV-100). $0.060/call."""
        return _fmt(
            await get_client().post(
                "/v1/lineage/record",
                {
                    "intent": intent,
                    "constraints": constraints,
                    "outcome": outcome,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_lineage_trace(record_id: str) -> str:
        """Retrieve and verify a lineage chain (DLV-101). $0.020/call."""
        return _fmt(await get_client().get(f"/v1/lineage/trace/{record_id}"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_contract_verify(contract: dict[str, Any]) -> str:
        """Validate a behavioral contract against Codex formal bounds (BCV-100). $0.060/call."""
        return _fmt(await get_client().post("/v1/contract/verify", {"contract": contract}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_contract_attestation(contract_id: str) -> str:
        """Fetch Nexus-Certified attestation for a contract (BCV-101). $0.020/call."""
        return _fmt(await get_client().get(f"/v1/contract/attestation/{contract_id}"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_federation_mint(identity: dict[str, Any], platforms: list[str]) -> str:
        """Mint cross-platform nxf_ identity token (AIF-100). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/federation/mint", {"identity": identity, "platforms": platforms}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_federation_verify(token: str) -> str:
        """Verify an nxf_ identity token (AIF-101). $0.020/call."""
        return _fmt(await get_client().post("/v1/federation/verify", {"token": token}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_federation_portability(from_platform: str, to_platform: str) -> str:
        """Check cross-platform capability portability (AIF-102). $0.020/call."""
        return _fmt(
            await get_client().post(
                "/v1/federation/portability",
                {
                    "from_platform": from_platform,
                    "to_platform": to_platform,
                },
            )
        )
