"""Tests for codex constants and tier closure identities."""

# pylint: disable=import-error

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aaaa_nexus_mcp import codex
from aaaa_nexus_mcp.tools import register_all_tools


class FakeMCP:
    def __init__(self):
        self.tools: dict[str, Callable] = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


@pytest.fixture(name="mcp_and_client")
def _mcp_and_client_fixture():
    fake = FakeMCP()
    client = AsyncMock()
    client.get = AsyncMock(return_value={"ok": True})
    client.post = AsyncMock(return_value={"POLICY_EPSILON": 1e-7, "delta": 1e-5, "verdict": "clean"})
    register_all_tools(fake, lambda: client)
    return fake, client



class TestCodexConstants:
    def test_tier_closure_identity(self):
        assert codex.TIER_CLOSURE == 0
        assert codex.RESIDUAL_NORM_LIMIT - codex.TIER1_MIN_COUNT - codex.BLOCK_DIM == 0

    def test_tau_trust(self):
        assert codex.TRUST_FLOOR == 1820 / 1823
        assert 0.998 < codex.TRUST_FLOOR < 0.999

    def test_eps_kl(self):
        assert codex.POLICY_EPSILON == 1 / codex.RESIDUAL_NORM_LIMIT

    def test_d_max_from_safe_prime(self):
        assert 1823 % 24 == codex.DELEGATION_DEPTH_LIMIT == 23

    def test_rg_loop_identity(self):
        assert 24 + codex.RATCHET_PERIOD == codex.CFT_COUNT == 71

    def test_tier_sizes_positive(self):
        assert all(n > 0 for n in codex.TIER_SIZES)
        assert codex.TIER_SIZES[0] == codex.TIER1_MIN_COUNT


class TestLocalTools:
    @pytest.mark.asyncio
    async def test_constants_tool(self, mcp_and_client):
        mcp, _ = mcp_and_client
        result = json.loads(await mcp.tools["nexus_sys_constants"]())
        assert result["schema"] == "sys.constants/v1"
        assert result["session"]["delegation_depth_max"] == codex.DELEGATION_DEPTH_LIMIT
        assert result["session"]["ratchet_period"] == codex.RATCHET_PERIOD
        assert result["ecc"]["min_distance"] == 8

    @pytest.mark.asyncio
    async def test_tier_memory_roundtrip(self, mcp_and_client):
        mcp, _ = mcp_and_client
        store = mcp.tools["nexus_vq_memory_store"]
        query = mcp.tools["nexus_vq_memory_query"]
        r1 = json.loads(await store(entry_id="a", values=[0.1] * 24, payload="first"))
        r2 = json.loads(await store(entry_id="b", values=[0.9] * 24, payload="second"))
        assert r1["stored"] is True
        assert r2["stored"] is True
        # Query with vector close to entry 'a' -- should rank a first
        result = json.loads(await query(values=[0.1] * 24, top_k=2))
        assert result["results"][0]["entry_id"] == "a"
        assert result["results"][0]["distance"] <= result["results"][1]["distance"]

    @pytest.mark.asyncio
    async def test_tau_gate_passes_clean_text(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post = AsyncMock(return_value={"POLICY_EPSILON": 1e-9, "delta": 1e-6})
        result = json.loads(await mcp.tools["nexus_trust_gate"](text="2+2=4"))
        assert result["verdict"] == "PASS"

    @pytest.mark.asyncio
    async def test_tau_gate_fails_hallucinated_text(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post = AsyncMock(return_value={"POLICY_EPSILON": 1.0, "delta": 1.0})
        result = json.loads(await mcp.tools["nexus_trust_gate"](text="lies"))
        assert result["verdict"] == "FAIL"

    @pytest.mark.asyncio
    async def test_TIER_decompose_deterministic(self, mcp_and_client):
        mcp, _ = mcp_and_client
        r1 = json.loads(await mcp.tools["nexus_payload_decompose"](payload="hello"))
        r2 = json.loads(await mcp.tools["nexus_payload_decompose"](payload="hello"))
        assert r1 == r2
        assert "healthy" in r1

    @pytest.mark.asyncio
    async def test_delegation_proceeds_under_limit(self, mcp_and_client):
        mcp, _ = mcp_and_client
        result = json.loads(await mcp.tools["nexus_delegation_depth"](current_depth=5))
        assert result["verdict"] == "PROCEED"
        assert result["remaining_depth"] == 23 - 5 - 1

    @pytest.mark.asyncio
    async def test_delegation_halts_at_limit(self, mcp_and_client):
        mcp, _ = mcp_and_client
        result = json.loads(await mcp.tools["nexus_delegation_depth"](current_depth=23))
        assert result["verdict"] == "HALT"

    @pytest.mark.asyncio
    async def test_ratchet_rotates_every_47(self, mcp_and_client):
        mcp, _ = mcp_and_client
        tool = mcp.tools["nexus_session_ratchet"]
        # Reset counter by calling 47 times
        rotated_count = 0
        for _ in range(47):
            r = json.loads(await tool())
            if r["rotated_this_call"]:
                rotated_count += 1
        # At least one rotation should occur in 47 calls
        assert rotated_count >= 1

    @pytest.mark.asyncio
    async def test_friction_score_ranges(self, mcp_and_client):
        mcp, _ = mcp_and_client
        # Low entropy string
        low = json.loads(await mcp.tools["nexus_friction_score"](prompt="aaaaaa"))
        # High entropy string
        high = json.loads(
            await mcp.tools["nexus_friction_score"](prompt="a1!B2@c3#D4$e5%F6^g7&H8*")
        )
        assert high["friction"] > low["friction"]
        assert "action" in low


class TestPremiumCodexTools:
    @pytest.mark.asyncio
    async def test_variant_rotate_produces_three_variants(self, mcp_and_client):
        mcp, _ = mcp_and_client
        text = "alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu"
        result = json.loads(
            await mcp.tools["nexus_variant_rotate"](code_or_text=text, attested=False)
        )
        assert set(result["variants"].keys()) == {"primary", "secondary", "tertiary"}
        hashes = set(result["variant_hashes"].values())
        assert len(hashes) == 3  # all three are distinct
        assert result["variant_split"]["total"] == 264

    @pytest.mark.asyncio
    async def test_ecc_encode_decode_roundtrip(self, mcp_and_client):
        mcp, _ = mcp_and_client
        # Encode
        enc = json.loads(
            await mcp.tools["nexus_chain_parity"](data_12bit=0xABC, attested=False)
        )
        assert enc["mode"] == "encode"
        cw = enc["codeword_24bit"]
        # Verify same codeword has zero syndrome
        ver = json.loads(
            await mcp.tools["nexus_chain_parity"](codeword_24bit=cw, attested=False)
        )
        assert ver["valid"] is True
        assert ver["syndrome"] == 0
        # Corrupt one bit -> nonzero syndrome
        corrupted = cw ^ 0b1
        bad = json.loads(
            await mcp.tools["nexus_chain_parity"](codeword_24bit=corrupted, attested=False)
        )
        assert bad["valid"] is False
        assert bad["syndrome"] != 0

    @pytest.mark.asyncio
    async def test_tier_jump_detects_novelty(self, mcp_and_client):
        mcp, _ = mcp_and_client
        result = json.loads(
            await mcp.tools["nexus_novelty_jump"](
                before_values=[0.01] * 24,
                after_values=[0.01] * 24,
                attested=False,
            )
        )
        assert result["verdict"] in ("near_identical", "same_tier_refinement")
        assert result["novelty_score"] == 0

    @pytest.mark.asyncio
    async def test_tier_budget_lifecycle(self, mcp_and_client):
        mcp, _ = mcp_and_client
        create = json.loads(
            await mcp.tools["nexus_fuel_budget_create"](
                budget_id="test-budget-1", attested=False
            )
        )
        initial = create["fuel_remaining"]
        assert initial > 0
        # Spend at tier 0 (cost=1)
        spend = json.loads(
            await mcp.tools["nexus_fuel_budget_spend"](
                budget_id="test-budget-1", tier=0, description="tiny op", attested=False
            )
        )
        assert spend["verdict"] == "ALLOW"
        assert spend["fuel_remaining"] == initial - 1
        # Spend at tier 5 (cost=100000) -> still allowed
        spend2 = json.loads(
            await mcp.tools["nexus_fuel_budget_spend"](
                budget_id="test-budget-1", tier=5, description="expensive", attested=False
            )
        )
        assert spend2["verdict"] == "ALLOW"
        # Spend at tier 7 (cost=10M) -> DENIED (exceeds 1M default budget)
        spend3 = json.loads(
            await mcp.tools["nexus_fuel_budget_spend"](
                budget_id="test-budget-1", tier=7, description="too big", attested=False
            )
        )
        assert spend3["verdict"] == "DENIED"

    @pytest.mark.asyncio
    async def test_tier_budget_unknown_id(self, mcp_and_client):
        mcp, _ = mcp_and_client
        result = json.loads(
            await mcp.tools["nexus_fuel_budget_spend"](
                budget_id="does-not-exist", tier=0, attested=False
            )
        )
        assert "error" in result

    @pytest.mark.asyncio
    async def test_attestation_annotates_result(self, mcp_and_client):
        """When attested=True, result contains _attestation block with receipt."""
        mcp, client = mcp_and_client
        client.post = AsyncMock(
            return_value={"lineage_id": "ln-abc123", "sha256": "deadbeef"}
        )
        result = json.loads(
            await mcp.tools["nexus_variant_rotate"](code_or_text="one two three", attested=True)
        )
        assert "_attestation" in result
        assert result["_attestation"]["attested"] is True
        assert "sha256" in result["_attestation"]
        assert "receipt" in result["_attestation"]



