"""Security tools — prompt scanning, threat scoring, shield, signatures."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_prompt_inject_scan(prompt: str) -> str:
        """Scan a prompt for adversarial injection patterns. $0.040/call."""
        return _fmt(await get_client().post("/v1/prompts/inject-scan", {"prompt": prompt}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_prompt_optimize(prompt: str) -> str:
        """Rewrite a prompt for clarity, safety, and lower cost. $0.040/call."""
        return _fmt(await get_client().post("/v1/prompts/optimize", {"prompt": prompt}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_security_prompt_scan(prompt: str) -> str:
        """Deep security scan to detect and block adversarial inputs. $0.040/call."""
        return _fmt(await get_client().post("/v1/security/prompt-scan", {"prompt": prompt}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_threat_score(payload: dict[str, Any]) -> str:
        """Multi-vector threat scoring (SEC-303). Pass any payload to assess threat level. $0.040/call."""
        return _fmt(await get_client().post("/v1/threat/score", {"payload": payload}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_security_shield(payload: dict[str, Any]) -> str:
        """Sanitize a payload for safe agentic tool calls. $0.040/call."""
        return _fmt(await get_client().post("/v1/security/shield", {"payload": payload}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_pqc_sign(data: str) -> str:
        """Generate a post-quantum ML-DSA (Dilithium) signature. $0.020/call."""
        return _fmt(await get_client().post("/v1/security/pqc-sign", {"data": data}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_zero_day_scan(payload: dict[str, Any]) -> str:
        """Scan agent payload for zero-day attack patterns. $0.040/call."""
        return _fmt(await get_client().post("/v1/security/zero-day", {"payload": payload}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_ethics_check(text: str) -> str:
        """Prime Axiom ethical oracle screening (DCM-1017). $0.040/call."""
        return _fmt(await get_client().post("/v1/ethics/check", {"text": text}))
