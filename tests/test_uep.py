"""Tests for UEP orchestration MCP wrappers."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable
from unittest.mock import AsyncMock

import pytest

from aaaa_nexus_mcp.errors import NexusAuthError
from aaaa_nexus_mcp.tools.uep import register


class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Callable] = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


@pytest.fixture
def mcp_and_client():
    fake_mcp = FakeMCP()
    client = AsyncMock()
    client.post = AsyncMock(return_value={
        "schema": "nexus.test.v1",
        "verdict": "PASS",
        "public_safe": True,
    })

    def get_client():
        return client

    register(fake_mcp, get_client)
    return fake_mcp, client


def test_uep_tools_register_with_prefix_and_async(mcp_and_client):
    mcp, _client = mcp_and_client
    expected = {
        "nexus_uep_preflight",
        "nexus_trusted_rag_augment",
        "nexus_synthesis_guard",
        "nexus_aha_detect",
        "nexus_autopoiesis_plan",
        "nexus_uep_trace_certify",
    }
    assert expected.issubset(mcp.tools)
    for name in expected:
        assert name.startswith("nexus_")
        assert asyncio.iscoroutinefunction(mcp.tools[name])


@pytest.mark.asyncio
async def test_preflight_posts_to_worker(mcp_and_client):
    mcp, client = mcp_and_client
    result = json.loads(await mcp.tools["nexus_uep_preflight"](
        task_description="implement uep",
        agent_id="agent-1",
        delegation_depth=2,
        max_budget_usdc=1.5,
        language="rust",
        context_manifest={"source": "trusted"},
    ))
    assert result["verdict"] == "PASS"
    client.post.assert_called_with(
        "/v1/uep/preflight",
        {
            "task_description": "implement uep",
            "agent_id": "agent-1",
            "delegation_depth": 2,
            "budget_id": "",
            "max_budget_usdc": 1.5,
            "language": "rust",
            "context_manifest": {"source": "trusted"},
        },
    )


@pytest.mark.asyncio
async def test_trusted_rag_posts_public_safe_request(mcp_and_client):
    mcp, client = mcp_and_client
    await mcp.tools["nexus_trusted_rag_augment"](
        query="Rust Worker AutoRAG",
        required_domains=["developers.cloudflare.com"],
    )
    client.post.assert_called_with(
        "/v1/rag/augment",
        {
            "query": "Rust Worker AutoRAG",
            "max_results": 5,
            "required_domains": ["developers.cloudflare.com"],
            "freshness_hours": 720,
            "source_policy": "trusted_only",
        },
    )


@pytest.mark.asyncio
async def test_synthesis_guard_excludes_raw_source(mcp_and_client):
    mcp, client = mcp_and_client
    await mcp.tools["nexus_synthesis_guard"](
        artifact_kind="rust_worker",
        language="rust",
        artifact_hash="a" * 64,
        redacted_source_summary="summary only",
    )
    _path, body = client.post.call_args.args
    assert "source_code" not in body
    assert body["redacted_source_summary"] == "summary only"


@pytest.mark.asyncio
async def test_aha_detect_posts_bps_inputs(mcp_and_client):
    mcp, client = mcp_and_client
    await mcp.tools["nexus_aha_detect"](
        novelty_delta=0.1,
        buffer_quality_score=0.999,
        eligible_sample_count=3,
        delegation_depth=1,
        friction_score=2.2,
        fuel_efficiency_gain=0.3,
        baseline_hashes=["h1"],
        gate_verdicts=["PASS"],
    )
    client.post.assert_called_with(
        "/v1/uep/aha-detect",
        {
            "novelty_delta": 0.1,
            "buffer_quality_score": 0.999,
            "eligible_sample_count": 3,
            "delegation_depth": 1,
            "friction_score": 2.2,
            "fuel_efficiency_gain": 0.3,
            "agent_id": "anonymous",
            "baseline_hashes": ["h1"],
            "gate_verdicts": ["PASS"],
        },
    )


@pytest.mark.asyncio
async def test_autopoiesis_plan_is_side_effect_free_wrapper(mcp_and_client):
    mcp, client = mcp_and_client
    await mcp.tools["nexus_autopoiesis_plan"](
        current_phase=5,
        verdict="PASS",
        bps=0.91,
        buffer_size=4,
    )
    client.post.assert_called_with(
        "/v1/uep/autopoiesis-plan",
        {
            "current_phase": 5,
            "verdict": "PASS",
            "bps": 0.91,
            "buffer_size": 4,
            "autocontribute_enabled": False,
            "phase_state": {},
        },
    )


@pytest.mark.asyncio
async def test_trace_certify_posts_public_envelope_inputs(mcp_and_client):
    mcp, client = mcp_and_client
    await mcp.tools["nexus_uep_trace_certify"](
        final_verdict="PASS",
        gate_results=[{"name": "trust", "verdict": "PASS"}],
        evidence_hashes=["abc"],
        bps=0.9,
        public_safe_summary="safe",
    )
    client.post.assert_called_with(
        "/v1/uep/trace-certify",
        {
            "final_verdict": "PASS",
            "gate_results": [{"name": "trust", "verdict": "PASS"}],
            "evidence_hashes": ["abc"],
            "bps": 0.9,
            "agent_id": "anonymous",
            "public_safe_summary": "safe",
            "public_safe": True,
        },
    )


@pytest.mark.asyncio
async def test_uep_wrappers_normalize_auth_errors(mcp_and_client):
    mcp, client = mcp_and_client
    client.post.side_effect = NexusAuthError("bad auth", endpoint="/v1/uep/preflight")
    result = json.loads(await mcp.tools["nexus_uep_preflight"]("task"))
    assert result["error"] == "Authentication failed. Set AAAA_NEXUS_API_KEY."
