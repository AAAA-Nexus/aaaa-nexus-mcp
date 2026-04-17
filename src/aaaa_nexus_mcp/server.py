"""FastMCP server for AAAA-Nexus API tools."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from aaaa_nexus_mcp.client import NexusAPIClient
from aaaa_nexus_mcp.config import get_config
from aaaa_nexus_mcp.tools import register_all_tools

mcp = FastMCP(
    "aaaa-nexus",
    instructions=(
        "AAAA-Nexus API: trust oracles, security scanning, compliance, "
        "agent swarm coordination, escrow, inference, and more. "
        "All tools prefixed with nexus_. API at https://atomadic.tech"
    ),
)

_client: NexusAPIClient | None = None


def get_client() -> NexusAPIClient:
    global _client
    if _client is None:
        cfg = get_config()
        _client = NexusAPIClient(
            base_url=cfg.base_url,
            api_key=cfg.api_key,
            timeout=cfg.timeout,
            autoguard=cfg.autoguard,
        )
    return _client


register_all_tools(mcp, get_client)
