"""VeriRand / VRF randomness tools."""

from __future__ import annotations

from collections.abc import Callable

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_rng_quantum(count: int = 1) -> str:
        """Generate quantum-seeded random numbers with HMAC proof. $0.020/call."""
        return _fmt(await get_client().get("/v1/rng/quantum", count=count))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_rng_verify(seed_ts: str, numbers: str, proof: str) -> str:
        """Verify HMAC proof for previously generated random numbers. Free."""
        return _fmt(
            await get_client().get("/v1/rng/verify", seed_ts=seed_ts, numbers=numbers, proof=proof)
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_vrf_draw(range_min: int, range_max: int, count: int = 1) -> str:
        """VRF random draw with on-chain proof. $0.01 + 0.5% of pot."""
        return _fmt(
            await get_client().post(
                "/v1/vrf/draw",
                {
                    "range_min": range_min,
                    "range_max": range_max,
                    "count": count,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_vrf_verify_draw(draw_id: str) -> str:
        """Verify a prior VRF draw. Included with draw cost."""
        return _fmt(await get_client().post("/v1/vrf/verify-draw", {"draw_id": draw_id}))
