"""Trust oracle tools — hallucination, trust phase, entropy, decay, scoring."""

from __future__ import annotations

from collections.abc import Callable

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_hallucination_oracle(text: str) -> str:
        """Check text for hallucination risk. Returns eps_kl divergence, verdict, confidence. $0.040/call."""
        return _fmt(await get_client().post("/v1/oracle/hallucination", {"text": text}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_trust_phase(agent_id: str) -> str:
        """Get V_AI geometric trust phase for an agent. Returns phase value and certification. $0.020/call."""
        return _fmt(await get_client().post("/v1/oracle/v-ai", {"agent_id": agent_id}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_entropy_oracle() -> str:
        """Measure session entropy. $0.004/call."""
        return _fmt(await get_client().post("/v1/oracle/entropy", {}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_trust_decay(agent_id: str, epochs: int) -> str:
        """Calculate P2P trust decay over N epochs. $0.008/call."""
        return _fmt(
            await get_client().post("/v1/trust/decay", {"agent_id": agent_id, "epochs": epochs})
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_trust_score(agent_id: str) -> str:
        """Get formally bounded trust score in [0,1] for an agent (TCM-100). $0.040/call."""
        return _fmt(await get_client().post("/v1/trust/score", {"agent_id": agent_id}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_trust_history(agent_id: str) -> str:
        """Get up to 100 epochs of trust score trajectory (TCM-101). $0.040/call."""
        return _fmt(await get_client().post("/v1/trust/history", {"agent_id": agent_id}))
