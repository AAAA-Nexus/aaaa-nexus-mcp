"""UEP orchestration wrappers.

These tools expose the Rust Worker orchestration layer as ergonomic MCP tools.
Policy stays in the Worker: the MCP client only forwards explicit inputs and
formats the structured response envelope.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from aaaa_nexus_mcp.tools import _fmt, handle_errors


def register(mcp: Any, get_client: Callable) -> None:
    @mcp.tool()
    @handle_errors
    async def nexus_uep_preflight(
        task_description: str,
        agent_id: str = "anonymous",
        delegation_depth: int = 0,
        budget_id: str = "",
        max_budget_usdc: float = 0.0,
        language: str = "unknown",
        context_manifest: dict[str, Any] | None = None,
    ) -> str:
        """Run Phase 0 UEP readiness checks before orchestration work."""
        client = get_client()
        return _fmt(await client.post(
            "/v1/uep/preflight",
            {
                "task_description": task_description,
                "agent_id": agent_id,
                "delegation_depth": delegation_depth,
                "budget_id": budget_id,
                "max_budget_usdc": max_budget_usdc,
                "language": language,
                "context_manifest": context_manifest or {},
            },
        ))

    @mcp.tool()
    @handle_errors
    async def nexus_trusted_rag_augment(
        query: str,
        max_results: int = 5,
        required_domains: list[str] | None = None,
        freshness_hours: int = 720,
        source_policy: str = "trusted_only",
    ) -> str:
        """Retrieve public-safe trusted context through the Worker RAG gate."""
        client = get_client()
        return _fmt(await client.post(
            "/v1/rag/augment",
            {
                "query": query,
                "max_results": max_results,
                "required_domains": required_domains or [],
                "freshness_hours": freshness_hours,
                "source_policy": source_policy,
            },
        ))

    @mcp.tool()
    @handle_errors
    async def nexus_synthesis_guard(
        artifact_kind: str,
        language: str,
        artifact_hash: str,
        redacted_source_summary: str = "",
        lint_score: float = 1.0,
        security_score: float = 1.0,
        trust_score: float = 1.0,
        provenance_hashes: list[str] | None = None,
    ) -> str:
        """Run Phase 3 synthesis gates without sending raw source by default."""
        client = get_client()
        return _fmt(await client.post(
            "/v1/uep/synthesis-guard",
            {
                "artifact_kind": artifact_kind,
                "language": language,
                "artifact_hash": artifact_hash,
                "redacted_source_summary": redacted_source_summary,
                "lint_score": lint_score,
                "security_score": security_score,
                "trust_score": trust_score,
                "provenance_hashes": provenance_hashes or [],
            },
        ))

    @mcp.tool()
    @handle_errors
    async def nexus_aha_detect(
        novelty_delta: float = 0.0,
        buffer_quality_score: float = 0.0,
        eligible_sample_count: int = 0,
        delegation_depth: int = 0,
        friction_score: float = 0.0,
        fuel_efficiency_gain: float = 0.0,
        agent_id: str = "anonymous",
        baseline_hashes: list[str] | None = None,
        gate_verdicts: list[str] | None = None,
    ) -> str:
        """Compute the Phase 4 Breakthrough Probability Score in the Worker."""
        client = get_client()
        return _fmt(await client.post(
            "/v1/uep/aha-detect",
            {
                "novelty_delta": novelty_delta,
                "buffer_quality_score": buffer_quality_score,
                "eligible_sample_count": eligible_sample_count,
                "delegation_depth": delegation_depth,
                "friction_score": friction_score,
                "fuel_efficiency_gain": fuel_efficiency_gain,
                "agent_id": agent_id,
                "baseline_hashes": baseline_hashes or [],
                "gate_verdicts": gate_verdicts or [],
            },
        ))

    @mcp.tool()
    @handle_errors
    async def nexus_autopoiesis_plan(
        current_phase: int = 4,
        verdict: str = "REFINE",
        bps: float = 0.0,
        buffer_size: int = 0,
        autocontribute_enabled: bool = False,
        phase_state: dict[str, Any] | None = None,
    ) -> str:
        """Ask the Worker for a side-effect-free Phase 5 evolution plan."""
        client = get_client()
        return _fmt(await client.post(
            "/v1/uep/autopoiesis-plan",
            {
                "current_phase": current_phase,
                "verdict": verdict,
                "bps": bps,
                "buffer_size": buffer_size,
                "autocontribute_enabled": autocontribute_enabled,
                "phase_state": phase_state or {},
            },
        ))

    @mcp.tool()
    @handle_errors
    async def nexus_uep_trace_certify(
        final_verdict: str,
        gate_results: list[dict[str, Any]],
        evidence_hashes: list[str],
        bps: float = 0.0,
        agent_id: str = "anonymous",
        public_safe_summary: str = "",
        public_safe: bool = True,
    ) -> str:
        """Generate a public-safe UEP trace certificate via the Worker."""
        client = get_client()
        return _fmt(await client.post(
            "/v1/uep/trace-certify",
            {
                "final_verdict": final_verdict,
                "gate_results": gate_results,
                "evidence_hashes": evidence_hashes,
                "bps": bps,
                "agent_id": agent_id,
                "public_safe_summary": public_safe_summary,
                "public_safe": public_safe,
            },
        ))
