"""SLA engine tools."""

from __future__ import annotations

from collections.abc import Callable

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_sla_register(
        agent_id: str, latency_ms: float, uptime_pct: float, error_rate: float, bond_usdc: float
    ) -> str:
        """Commit to an SLA with bond deposit. $0.080/call."""
        return _fmt(
            await get_client().post(
                "/v1/sla/register",
                {
                    "agent_id": agent_id,
                    "latency_ms": latency_ms,
                    "uptime_pct": uptime_pct,
                    "error_rate": error_rate,
                    "bond_usdc": bond_usdc,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_sla_report(sla_id: str, metric: str, value: float) -> str:
        """Report an SLA metric — auto-detects breaches. $0.020/call."""
        return _fmt(
            await get_client().post(
                "/v1/sla/report", {"sla_id": sla_id, "metric": metric, "value": value}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_sla_status(sla_id: str) -> str:
        """Get SLA compliance score and bond remaining. $0.008/call."""
        return _fmt(await get_client().get(f"/v1/sla/status/{sla_id}"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_sla_breach(sla_id: str, severity: str) -> str:
        """Report SLA breach and calculate penalty. $0.040/call."""
        return _fmt(
            await get_client().post("/v1/sla/breach", {"sla_id": sla_id, "severity": severity})
        )
