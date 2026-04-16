"""Ecosystem coordination tools — consensus, quota, certification, saga, memory fence."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: object, get_client: Callable) -> None:
    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_consensus_create(quorum_mode: str, participants: list[str]) -> str:
        """Create a multi-agent consensus session (CSN-100). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/consensus/session",
                {
                    "quorum_mode": quorum_mode,
                    "participants": participants,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_consensus_vote(
        session_id: str, agent_id: str, output_hash: str, confidence: float
    ) -> str:
        """Cast a consensus vote. $0.020/call."""
        return _fmt(
            await get_client().post(
                f"/v1/consensus/session/{session_id}/vote",
                {
                    "agent_id": agent_id,
                    "output_hash": output_hash,
                    "confidence": confidence,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_consensus_result(session_id: str) -> str:
        """Get certified winning output from consensus. $0.020/call."""
        return _fmt(await get_client().get(f"/v1/consensus/session/{session_id}/result"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_quota_create(total_budget: int, children: list[dict[str, Any]]) -> str:
        """Create hierarchical token budget tree (QTA-100). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/quota/tree", {"total_budget": total_budget, "children": children}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_quota_draw(
        tree_id: str, child_id: str, tokens: int, idempotency_key: str
    ) -> str:
        """Deduct tokens from quota tree with idempotency. $0.020/call."""
        return _fmt(
            await get_client().post(
                f"/v1/quota/tree/{tree_id}/draw",
                {
                    "child_id": child_id,
                    "tokens": tokens,
                    "idempotency_key": idempotency_key,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_quota_status(tree_id: str) -> str:
        """Check remaining budget and alerts for a quota tree. $0.020/call."""
        return _fmt(await get_client().get(f"/v1/quota/tree/{tree_id}/status"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_certify_output(output: str, rubric: list[str]) -> str:
        """Issue a 30-day output certificate (OCN-100). $0.060/call."""
        return _fmt(
            await get_client().post("/v1/certify/output", {"output": output, "rubric": rubric})
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_certify_output_verify(certificate_id: str) -> str:
        """Verify an output certificate. $0.020/call."""
        return _fmt(await get_client().get(f"/v1/certify/output/{certificate_id}/verify"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_saga_create(name: str, steps: list[str], compensations: dict[str, str]) -> str:
        """Register a multi-step saga workflow with compensation actions (RBK-100). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/rollback/saga",
                {
                    "name": name,
                    "steps": steps,
                    "compensations": compensations,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_saga_checkpoint(saga_id: str, step: str) -> str:
        """Mark a saga step as completed. $0.020/call."""
        return _fmt(
            await get_client().post(f"/v1/rollback/saga/{saga_id}/checkpoint", {"step": step})
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_saga_compensate(saga_id: str) -> str:
        """Trigger LIFO rollback for a saga. $0.040/call."""
        return _fmt(await get_client().post(f"/v1/rollback/saga/{saga_id}/compensate", {}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_memory_fence_create(namespace: str) -> str:
        """Create HMAC namespace boundary for cross-tenant isolation (MFN-100). $0.040/call."""
        return _fmt(await get_client().post("/v1/memory/fence", {"namespace": namespace}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_memory_fence_audit(fence_id: str) -> str:
        """Audit access log and entry count for a memory fence. $0.020/call."""
        return _fmt(await get_client().get(f"/v1/memory/fence/{fence_id}/audit"))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_governance_vote(
        agent_id: str, proposal_id: str, vote: str, weight: float = 1.0
    ) -> str:
        """Cast an on-chain governance vote (GOV-112). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/governance/vote",
                {
                    "agent_id": agent_id,
                    "proposal_id": proposal_id,
                    "vote": vote,
                    "weight": weight,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_data_validate_json(data: dict[str, Any], schema: dict[str, Any]) -> str:
        """Validate JSON data against a schema — returns error paths. $0.012/call."""
        return _fmt(
            await get_client().post("/v1/data/validate-json", {"data": data, "schema": schema})
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_data_format_convert(data: str, from_format: str, to_format: str) -> str:
        """Convert between JSON and CSV formats. $0.020/call."""
        return _fmt(
            await get_client().post(
                "/v1/data/format-convert",
                {
                    "data": data,
                    "from_format": from_format,
                    "to_format": to_format,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_crypto_toolkit(data: str) -> str:
        """Generate BLAKE3 hash, Merkle proof, and nonce (DCM-1018). $0.020/call."""
        return _fmt(await get_client().post("/v1/dcm/crypto-toolkit", {"data": data}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_dev_starter(project_name: str, language: str = "python") -> str:
        """Scaffold an agent project with x402 wiring (DEV-601). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/dev/starter", {"project_name": project_name, "language": language}
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_efficiency_capture(interactions: list[dict[str, Any]]) -> str:
        """Calculate ROI signal across agent interactions (PAY-506). $0.040/call."""
        return _fmt(await get_client().post("/v1/efficiency", {"interactions": interactions}))

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_billing_outcome(task_id: str, success: bool, metric_value: float) -> str:
        """Outcome-based billing — pay only for measurably successful tasks (PAY-509). $0.040/call."""
        return _fmt(
            await get_client().post(
                "/v1/billing/outcome",
                {
                    "task_id": task_id,
                    "success": success,
                    "metric_value": metric_value,
                },
            )
        )

    @mcp.tool()  # type: ignore[misc]
    @handle_errors
    async def nexus_costs_attribute(run_id: str) -> str:
        """Attribute token spend by agent, task, and model (DEV-603). $0.040/call."""
        return _fmt(await get_client().post("/v1/costs/attribute", {"run_id": run_id}))
