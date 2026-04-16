"""Agent swarm tools — registration, topology, messaging, planning."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_agent_register(
        agent_id: int, name: str, capabilities: list[str], endpoint: str
    ) -> str:
        """Register an agent in the swarm. agent_id must be multiple of 324 (G_18). Free."""
        return _fmt(
            await get_client().post(
                "/v1/agents/register",
                {
                    "agent_id": agent_id,
                    "name": name,
                    "capabilities": capabilities,
                    "endpoint": endpoint,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_agent_topology() -> str:
        """Get the global swarm topology — all registered agents and connections. $0.008/call."""
        return _fmt(await get_client().get("/v1/agents/topology"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_agent_semantic_diff(base: str, current: str) -> str:
        """Detect knowledge drift between two text versions using Jaccard similarity. $0.040/call."""
        return _fmt(
            await get_client().post("/v1/agents/semantic-diff", {"base": base, "current": current})
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_agent_intent_classify(text: str) -> str:
        """Classify intent of text — returns top-3 intents with confidence scores. $0.020/call."""
        return _fmt(await get_client().post("/v1/agents/intent-classify", {"text": text}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_agent_reputation(agent_id: str) -> str:
        """Get A2A compliance and trust score for an agent. $0.040/call."""
        return _fmt(await get_client().post("/v1/agents/reputation", {"agent_id": agent_id}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_agent_token_budget(task: str, models: list[str] | None = None) -> str:
        """Estimate token cost across models for a task. $0.020/call."""
        return _fmt(
            await get_client().post(
                "/v1/agents/token-budget", {"task": task, "models": models or []}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_agent_contradiction(statement_a: str, statement_b: str) -> str:
        """NLI fact-checker — detect contradictions between two statements. $0.020/call."""
        return _fmt(
            await get_client().post(
                "/v1/agents/contradiction", {"statement_a": statement_a, "statement_b": statement_b}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_agent_plan(goal: str) -> str:
        """Decompose a goal into dependency-aware execution steps. $0.060/call."""
        return _fmt(await get_client().post("/v1/agents/plan", {"goal": goal}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_agent_capabilities_match(task: str) -> str:
        """Find agents in the swarm matching a task's requirements. $0.020/call."""
        return _fmt(await get_client().post("/v1/agents/capabilities/match", {"task": task}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_swarm_relay(
        from_id: str, to: str, message: dict[str, Any], ttl: int = 3600
    ) -> str:
        """Relay an A2A message across the swarm. $0.008/call."""
        return _fmt(
            await get_client().post(
                "/v1/swarm/relay", {"from": from_id, "to": to, "message": message, "ttl": ttl}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_swarm_inbox(agent_id: str) -> str:
        """Check an agent's swarm message inbox. $0.008/call."""
        return _fmt(await get_client().get("/v1/swarm/inbox", agent_id=agent_id))
