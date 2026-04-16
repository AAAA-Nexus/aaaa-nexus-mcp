"""NEXUS AEGIS compliance suite tools."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_aegis_mcp_proxy(
        tool_name: str, tool_input: str = "", agent_id: str = ""
    ) -> str:
        """Execute an MCP tool call through the AEGIS firewall (AEG-100). $0.040/call."""
        body: dict[str, Any] = {"tool": tool_name, "tool_input": tool_input}
        if agent_id:
            body["agent_id"] = agent_id
        return _fmt(await get_client().post("/v1/aegis/mcp-proxy/execute", body))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_aegis_epistemic_route(
        prompt: str, max_tokens: int = 256, model: str = "auto"
    ) -> str:
        """Route a query with epistemic bounds awareness (AEG-101). Identifies knowledge gaps. $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/aegis/router/epistemic-bound",
                {"prompt": prompt, "max_tokens": max_tokens, "model": model},
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_aegis_certify_epoch(system_id: str) -> str:
        """Certify a 47-epoch compliance cycle with EU AI Act validation (AEG-102). $0.060/call."""
        return _fmt(await get_client().post("/v1/aegis/certify-epoch", {"system_id": system_id}))
