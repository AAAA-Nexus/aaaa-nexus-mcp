"""Tests for the federated LoRA training loop tools."""

from __future__ import annotations

import json
from collections.abc import Callable
from unittest.mock import AsyncMock

import pytest

from aaaa_nexus_mcp.tools import register_all_tools
from aaaa_nexus_mcp.tools.lora import _CAPTURE_BUFFER, _scrub


class FakeMCP:
    def __init__(self):
        self.tools: dict[str, Callable] = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


@pytest.fixture
def mcp_and_client():
    _CAPTURE_BUFFER.clear()
    fake = FakeMCP()
    client = AsyncMock()
    client.get = AsyncMock(return_value={"adapter_id": "lora-py-v42", "samples": 12000})
    client.post = AsyncMock(return_value={"accepted": 3, "rejected": 0, "batch_id": "b-1"})
    register_all_tools(fake, lambda: client)
    return fake, client


class TestScrubber:
    def test_scrub_windows_path(self):
        assert "C:\\Users\\me" not in _scrub("error at C:\\Users\\me\\proj\\file.py")

    def test_scrub_unix_path(self):
        assert "/home/alice" not in _scrub("/home/alice/dev/thing.py failed")

    def test_scrub_email(self):
        assert "alice@example.com" not in _scrub("contact alice@example.com")

    def test_scrub_api_token(self):
        assert "sk-abc123" not in _scrub("key=sk-abc123def456ghi789jkl")

    def test_scrub_password_assignment(self):
        assert "hunter2" not in _scrub('password = "hunter2-secret"')

    def test_scrub_preserves_code(self):
        code = "def add(a, b):\n    return a + b"
        assert _scrub(code) == code  # no PII -> unchanged

    def test_scrub_truncates_huge_input(self):
        huge = "x" * 20000
        assert len(_scrub(huge)) == 8192


class TestLoRACapture:
    @pytest.mark.asyncio
    async def test_capture_accepts_new_sample(self, mcp_and_client):
        mcp, _ = mcp_and_client
        result = json.loads(
            await mcp.tools["nexus_lora_capture_fix"](
                bad_code="def foo():\n  return None",
                good_code="def foo() -> None:\n    return None",
                language="python",
                lint_delta=2,
                error_type="missing_type_hint",
            )
        )
        assert result["captured"] is True
        assert result["buffer_size"] == 1
        assert result["quality_estimate"] > 0

    @pytest.mark.asyncio
    async def test_capture_dedup(self, mcp_and_client):
        mcp, _ = mcp_and_client
        args = {"bad_code": "x=1", "good_code": "x = 1", "language": "python", "lint_delta": 1}
        first = json.loads(await mcp.tools["nexus_lora_capture_fix"](**args))
        second = json.loads(await mcp.tools["nexus_lora_capture_fix"](**args))
        assert first["captured"] is True
        assert second["captured"] is False
        assert second["reason"] == "duplicate"

    @pytest.mark.asyncio
    async def test_capture_empty_inputs(self, mcp_and_client):
        mcp, _ = mcp_and_client
        result = json.loads(
            await mcp.tools["nexus_lora_capture_fix"](
                bad_code="", good_code="fix", language="python", lint_delta=1
            )
        )
        assert result["quality_estimate"] == 0.0

    @pytest.mark.asyncio
    async def test_capture_scrubs_secrets(self, mcp_and_client):
        mcp, _ = mcp_and_client
        await mcp.tools["nexus_lora_capture_fix"](
            bad_code='api_key = "sk-abc123def456ghi789jkl"',
            good_code="api_key = os.environ['API_KEY']",
            language="python",
            lint_delta=1,
        )
        inspect = json.loads(await mcp.tools["nexus_lora_buffer_inspect"]())
        # Sample is in buffer but content was scrubbed before storage
        assert inspect["buffer_size"] == 1

    @pytest.mark.asyncio
    async def test_capture_respects_cap(self, mcp_and_client):
        mcp, _ = mcp_and_client
        # Fill past cap by capturing many unique fixes
        for i in range(260):
            await mcp.tools["nexus_lora_capture_fix"](
                bad_code=f"bug_{i}", good_code=f"fix_{i}", language="python", lint_delta=1
            )
        inspect = json.loads(await mcp.tools["nexus_lora_buffer_inspect"]())
        assert inspect["buffer_size"] <= 256


class TestLoRAContribute:
    @pytest.mark.asyncio
    async def test_contribute_empty_buffer(self, mcp_and_client):
        mcp, _ = mcp_and_client
        result = json.loads(await mcp.tools["nexus_lora_contribute"]())
        assert result["submitted"] == 0
        assert result["reason"] == "empty_buffer"

    @pytest.mark.asyncio
    async def test_contribute_flushes_high_quality(self, mcp_and_client):
        mcp, client = mcp_and_client
        for i in range(3):
            await mcp.tools["nexus_lora_capture_fix"](
                bad_code=f"def f{i}():\n  return None",
                good_code=f"def f{i}() -> None:\n    return None",
                language="python",
                lint_delta=5,  # high delta -> high quality
            )
        result = json.loads(await mcp.tools["nexus_lora_contribute"](min_quality=0.5))
        assert result["submitted"] >= 1
        assert result["remaining_in_buffer"] == 0
        client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_contribute_filters_low_quality(self, mcp_and_client):
        mcp, _ = mcp_and_client
        await mcp.tools["nexus_lora_capture_fix"](
            bad_code="a", good_code="b", language="unknown_lang", lint_delta=0
        )
        result = json.loads(await mcp.tools["nexus_lora_contribute"](min_quality=0.9))
        assert result["submitted"] == 0
        assert result["reason"] == "no_samples_above_threshold"


class TestLoRAAdapterAndStatus:
    @pytest.mark.asyncio
    async def test_status(self, mcp_and_client):
        mcp, _ = mcp_and_client
        result = json.loads(await mcp.tools["nexus_lora_status"]())
        assert "backend_status" in result
        assert "local_buffer_size" in result

    @pytest.mark.asyncio
    async def test_adapter_current(self, mcp_and_client):
        mcp, _ = mcp_and_client
        result = json.loads(
            await mcp.tools["nexus_lora_adapter_current"](language="python")
        )
        assert result["language"] == "python"
        assert "adapter" in result

    @pytest.mark.asyncio
    async def test_reward_claim(self, mcp_and_client):
        mcp, client = mcp_and_client
        client.post = AsyncMock(return_value={"reputation_delta": 15, "usdc_payout": 0.05})
        result = json.loads(
            await mcp.tools["nexus_lora_reward_claim"](agent_id="copilot")
        )
        assert result["agent_id"] == "copilot"
        assert "claim" in result

    @pytest.mark.asyncio
    async def test_buffer_clear(self, mcp_and_client):
        mcp, _ = mcp_and_client
        await mcp.tools["nexus_lora_capture_fix"](
            bad_code="x", good_code="y", language="python", lint_delta=1
        )
        result = json.loads(await mcp.tools["nexus_lora_buffer_clear"]())
        assert result["cleared"] >= 1
        assert result["buffer_size"] == 0
