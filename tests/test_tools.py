"""Tests for MCP tool modules -- registration, dispatch, and error handling.

Tests a representative sample of all 16 tool categories by mocking
the NexusAPIClient and verifying that registered tool functions:
  1. Call the correct HTTP method + endpoint
  2. Format the response as JSON
  3. Handle errors via the handle_errors decorator
"""

from __future__ import annotations

import json
from collections.abc import Callable
from unittest.mock import AsyncMock

import pytest

from aaaa_nexus_mcp.errors import NexusAuthError, NexusServerError
from aaaa_nexus_mcp.tools import register_all_tools

# -- Fixtures -----------------------------------------------------------------


class FakeMCP:
    """Minimal MCP stub that captures registered tools."""

    def __init__(self):
        self.tools: dict[str, Callable] = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


def _mock_client(get_response: dict | None = None, post_response: dict | None = None):
    """Create a mock NexusAPIClient with canned responses."""
    client = AsyncMock()
    client.get = AsyncMock(return_value=get_response or {"status": "ok"})
    client.post = AsyncMock(return_value=post_response or {"status": "ok"})
    return client


@pytest.fixture
def mcp_and_client():
    """Register all tools on a fake MCP with a mock client."""
    fake_mcp = FakeMCP()
    client = _mock_client()

    def get_client():
        return client

    register_all_tools(fake_mcp, get_client)
    return fake_mcp, client


# -- Registration tests -------------------------------------------------------


class TestToolRegistration:
    def test_all_tools_registered(self, mcp_and_client):
        fake_mcp, _ = mcp_and_client
        # All 113 tools should be registered
        assert len(fake_mcp.tools) >= 100, f"Expected 100+ tools, got {len(fake_mcp.tools)}"

    def test_all_tools_prefixed_with_nexus(self, mcp_and_client):
        fake_mcp, _ = mcp_and_client
        for name in fake_mcp.tools:
            assert name.startswith("nexus_"), f"Tool {name!r} missing nexus_ prefix"

    def test_all_tools_are_async(self, mcp_and_client):
        fake_mcp, _ = mcp_and_client
        import asyncio

        for name, fn in fake_mcp.tools.items():
            assert asyncio.iscoroutinefunction(fn), f"{name} is not async"


# -- System tools -------------------------------------------------------------


class TestSystemTools:
    @pytest.mark.asyncio
    async def test_nexus_health(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.get.return_value = {"status": "ok", "version": "2.0.0"}
        result = json.loads(await mcp.tools["nexus_health"]())
        assert result["status"] == "ok"
        client.get.assert_called_with("/health")

    @pytest.mark.asyncio
    async def test_nexus_metrics(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.get.return_value = {"request_volume": 5000}
        result = json.loads(await mcp.tools["nexus_metrics"]())
        assert result["request_volume"] == 5000

    @pytest.mark.asyncio
    async def test_nexus_agent_card(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.get.return_value = {"name": "nexus", "version": "2.0"}
        result = json.loads(await mcp.tools["nexus_agent_card"]())
        assert result["name"] == "nexus"


# -- Trust tools --------------------------------------------------------------


class TestTrustTools:
    @pytest.mark.asyncio
    async def test_hallucination_oracle(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"score": 0.05, "verdict": "clean"}
        result = json.loads(await mcp.tools["nexus_hallucination_oracle"](text="test"))
        assert result["score"] == 0.05
        client.post.assert_called_with("/v1/oracle/hallucination", {"text": "test"})

    @pytest.mark.asyncio
    async def test_trust_score(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"score": 0.95, "certified": True}
        result = json.loads(await mcp.tools["nexus_trust_score"](agent_id="a1"))
        assert result["score"] == 0.95

    @pytest.mark.asyncio
    async def test_trust_phase(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"phase": 0.98}
        result = json.loads(await mcp.tools["nexus_trust_phase"](agent_id="a1"))
        assert result["phase"] == 0.98


# -- Security tools -----------------------------------------------------------


class TestSecurityTools:
    @pytest.mark.asyncio
    async def test_prompt_inject_scan(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"is_injection": False, "confidence": 0.99}
        result = json.loads(await mcp.tools["nexus_prompt_inject_scan"](prompt="hello"))
        assert result["is_injection"] is False

    @pytest.mark.asyncio
    async def test_threat_score(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"score": 0.1, "risk_level": "low"}
        result = json.loads(await mcp.tools["nexus_threat_score"](payload={"action": "read"}))
        assert result["risk_level"] == "low"

    @pytest.mark.asyncio
    async def test_pqc_sign(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"signature": "sig-abc", "algorithm": "ML-DSA"}
        result = json.loads(await mcp.tools["nexus_pqc_sign"](data="payload"))
        assert result["algorithm"] == "ML-DSA"


# -- Inference tools ----------------------------------------------------------


class TestInferenceTools:
    @pytest.mark.asyncio
    async def test_nexus_inference(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"text": "response", "model": "llama-3.1"}
        result = json.loads(await mcp.tools["nexus_inference"](prompt="test"))
        assert result["text"] == "response"

    @pytest.mark.asyncio
    async def test_nexus_embed(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"embedding": [0.1, 0.2, 0.3]}
        result = json.loads(await mcp.tools["nexus_embed"](values=[1.0, 2.0]))
        assert len(result["embedding"]) == 3

    @pytest.mark.asyncio
    async def test_text_summarize(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"summary": "Short."}
        result = json.loads(await mcp.tools["nexus_text_summarize"](text="Long text..."))
        assert result["summary"] == "Short."

    @pytest.mark.asyncio
    async def test_text_sentiment(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"sentiment": "positive", "confidence": 0.92}
        result = json.loads(await mcp.tools["nexus_text_sentiment"](text="I love this"))
        assert result["sentiment"] == "positive"


# -- Compliance tools ---------------------------------------------------------


class TestComplianceTools:
    @pytest.mark.asyncio
    async def test_compliance_check(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"compliant": True, "frameworks": ["EU AI Act"]}
        result = json.loads(await mcp.tools["nexus_compliance_check"](system_description="test AI"))
        assert result["compliant"] is True

    @pytest.mark.asyncio
    async def test_audit_log(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"logged": True, "entry_id": "al-1"}
        result = json.loads(await mcp.tools["nexus_audit_log"](event={"action": "deploy"}))
        assert result["logged"] is True


# -- Escrow tools -------------------------------------------------------------


class TestEscrowTools:
    @pytest.mark.asyncio
    async def test_escrow_create(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"escrow_id": "e1", "status": "locked"}
        result = json.loads(
            await mcp.tools["nexus_escrow_create"](amount_usdc=10.0, sender="s1", receiver="r1", conditions=["done"])
        )
        assert result["escrow_id"] == "e1"


# -- Swarm tools --------------------------------------------------------------


class TestSwarmTools:
    @pytest.mark.asyncio
    async def test_agent_register(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"agent_id": 324, "status": "registered"}
        result = json.loads(
            await mcp.tools["nexus_agent_register"](
                agent_id=324, name="test", capabilities=["search"], endpoint="http://a.local"
            )
        )
        assert result["status"] == "registered"

    @pytest.mark.asyncio
    async def test_agent_plan(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"steps": [{"id": 1}]}
        result = json.loads(await mcp.tools["nexus_agent_plan"](goal="find data"))
        assert len(result["steps"]) == 1


# -- RatchetGate tools --------------------------------------------------------


class TestRatchetGateTools:
    @pytest.mark.asyncio
    async def test_ratchet_register(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"session_id": "s1", "epoch": 0}
        result = json.loads(await mcp.tools["nexus_ratchet_register"](agent_id=324))
        assert result["session_id"] == "s1"


# -- AEGIS tools --------------------------------------------------------------


class TestAegisTools:
    @pytest.mark.asyncio
    async def test_aegis_mcp_proxy(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"allowed": True, "result": "ok"}
        result = json.loads(await mcp.tools["nexus_aegis_mcp_proxy"](tool_name="read_file"))
        assert result["allowed"] is True


# -- Vanguard tools -----------------------------------------------------------


class TestVanguardTools:
    @pytest.mark.asyncio
    async def test_vanguard_redteam(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"findings": [], "risk_score": 0.05}
        result = json.loads(
            await mcp.tools["nexus_vanguard_redteam"](agent_id="a1", target="http://t.local")
        )
        assert result["risk_score"] == 0.05


# -- Ecosystem tools ---------------------------------------------------------


class TestEcosystemTools:
    @pytest.mark.asyncio
    async def test_consensus_create(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"session_id": "cs1"}
        result = json.loads(
            await mcp.tools["nexus_consensus_create"](quorum_mode="majority", agents=["a1", "a2"])
        )
        assert result["session_id"] == "cs1"

    @pytest.mark.asyncio
    async def test_governance_vote(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post.return_value = {"vote_id": "v1", "recorded": True}
        result = json.loads(await mcp.tools["nexus_governance_vote"](agent_id="a1", proposal_id="p1", vote="approve"))
        assert result["recorded"] is True


# -- VeriRand tools -----------------------------------------------------------


class TestVeriRandTools:
    @pytest.mark.asyncio
    async def test_verirand_generate(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.get.return_value = {"random_value": 42, "proof": "abc"}
        result = json.loads(await mcp.tools["nexus_rng_quantum"](count=1))
        assert result["random_value"] == 42


# -- Error handling through tools ---------------------------------------------


class TestToolErrorHandling:
    @pytest.mark.asyncio
    async def test_auth_error_in_tool(self):
        fake_mcp = FakeMCP()
        client = AsyncMock()
        client.get.side_effect = NexusAuthError("bad key", status_code=401)

        def get_client():
            return client

        from aaaa_nexus_mcp.tools.system import register

        register(fake_mcp, get_client)

        result = json.loads(await fake_mcp.tools["nexus_health"]())
        assert "Authentication failed" in result["error"]

    @pytest.mark.asyncio
    async def test_server_error_in_tool(self):
        fake_mcp = FakeMCP()
        client = AsyncMock()
        client.post.side_effect = NexusServerError("internal error", status_code=500)

        def get_client():
            return client

        from aaaa_nexus_mcp.tools.trust import register

        register(fake_mcp, get_client)

        result = json.loads(await fake_mcp.tools["nexus_trust_score"](agent_id="a1"))
        assert result["status_code"] == 500
