"""Tests for MCP client, error handling, and representative tool coverage."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import httpx
import pytest

from aaaa_nexus_mcp.client import NexusAPIClient
from aaaa_nexus_mcp.config import get_config
from aaaa_nexus_mcp.errors import (
    NexusAuthError,
    NexusConnectionError,
    NexusPaymentRequired,
    NexusRateLimited,
    NexusServerError,
    NexusTimeoutError,
    raise_for_status,
)
from aaaa_nexus_mcp.tools import _fmt, handle_errors

# -- Config tests -------------------------------------------------------------


class TestConfig:
    def test_default_config(self):
        cfg = get_config()
        assert cfg.base_url == "https://atomadic.tech"
        assert cfg.timeout == 20.0
        assert cfg.autoguard is True  # on by default

    def test_config_from_env(self, monkeypatch):
        monkeypatch.setenv("AAAA_NEXUS_BASE_URL", "https://test.local")
        monkeypatch.setenv("AAAA_NEXUS_API_KEY", "test-key")
        monkeypatch.setenv("AAAA_NEXUS_TIMEOUT", "5.0")
        cfg = get_config()
        assert cfg.base_url == "https://test.local"
        assert cfg.api_key == "test-key"
        assert cfg.timeout == 5.0

    def test_autoguard_disabled_by_env(self, monkeypatch):
        monkeypatch.setenv("AAAA_NEXUS_AUTOGUARD", "false")
        cfg = get_config()
        assert cfg.autoguard is False

    def test_autoguard_enabled_by_env(self, monkeypatch):
        monkeypatch.setenv("AAAA_NEXUS_AUTOGUARD", "true")
        cfg = get_config()
        assert cfg.autoguard is True


# -- Error tests --------------------------------------------------------------


class TestErrors:
    def test_raise_for_status_2xx(self):
        raise_for_status(200)
        raise_for_status(201)

    def test_raise_for_status_401(self):
        with pytest.raises(NexusAuthError):
            raise_for_status(401, endpoint="/test")

    def test_raise_for_status_402(self):
        with pytest.raises(NexusPaymentRequired):
            raise_for_status(402)

    def test_raise_for_status_429(self):
        with pytest.raises(NexusRateLimited):
            raise_for_status(429)

    def test_raise_for_status_500(self):
        with pytest.raises(NexusServerError):
            raise_for_status(500)


# -- Client tests -------------------------------------------------------------


class TestClient:
    @pytest.fixture
    def mock_client(self):
        # autoguard=False in tests -- avoids guard API calls in unit tests
        return NexusAPIClient(base_url="https://test.local", api_key="key-123", autoguard=False)

    @pytest.mark.asyncio
    async def test_get_success(self, mock_client):
        mock_response = httpx.Response(
            200, json={"status": "ok"}, request=httpx.Request("GET", "https://test.local/health")
        )
        mock_client._client = AsyncMock()
        mock_client._client.get = AsyncMock(return_value=mock_response)
        result = await mock_client.get("/health")
        assert result == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_post_success(self, mock_client):
        mock_response = httpx.Response(
            200,
            json={"score": 0.95},
            request=httpx.Request("POST", "https://test.local/v1/trust/score"),
        )
        mock_client._client = AsyncMock()
        mock_client._client.post = AsyncMock(return_value=mock_response)
        result = await mock_client.post("/v1/trust/score", {"agent_id": "a1"})
        assert result["score"] == 0.95

    @pytest.mark.asyncio
    async def test_get_402_returns_payment_details(self, mock_client):
        mock_response = httpx.Response(
            402,
            json={"amount": 0.04, "network": "base", "address": "0xabc"},
            request=httpx.Request("GET", "https://test.local/v1/test"),
        )
        mock_client._client = AsyncMock()
        mock_client._client.get = AsyncMock(return_value=mock_response)
        result = await mock_client.get("/v1/test")
        assert result["payment_required"] is True
        assert result["amount_usdc"] == 0.04

    @pytest.mark.asyncio
    async def test_post_connection_error(self, mock_client):
        mock_client._client = AsyncMock()
        mock_client._client.post = AsyncMock(side_effect=httpx.ConnectError("refused"))
        with pytest.raises(NexusConnectionError):
            await mock_client.post("/v1/test")

    @pytest.mark.asyncio
    async def test_get_timeout_error(self, mock_client):
        mock_client._client = AsyncMock()
        mock_client._client.get = AsyncMock(side_effect=httpx.ReadTimeout("timeout"))
        with pytest.raises(NexusTimeoutError):
            await mock_client.get("/v1/test")

    @pytest.mark.asyncio
    async def test_autoguard_annotates_response(self):
        """autoguard=True attaches _guard block with hallucination + drift."""
        client = NexusAPIClient(base_url="https://test.local", api_key="k", autoguard=True)
        main_resp = httpx.Response(
            200, json={"score": 0.9}, request=httpx.Request("POST", "https://test.local/v1/trust/score")
        )
        guard_resp = httpx.Response(
            200,
            json={"verdict": "clean", "POLICY_EPSILON": 1e-6},
            request=httpx.Request("POST", "https://test.local/v1/oracle/hallucination"),
        )
        # Main call + both guard calls all return via the same mock
        client._client = AsyncMock()
        client._client.post = AsyncMock(side_effect=[main_resp, guard_resp, guard_resp])
        result = await client.post("/v1/trust/score", {"agent_id": "a1"})
        assert result["score"] == 0.9
        assert "_guard" in result
        assert "hallucination" in result["_guard"]
        assert "drift" in result["_guard"]
        assert "guarded_at" in result["_guard"]

    @pytest.mark.asyncio
    async def test_autoguard_skipped_for_guard_paths(self):
        """autoguard is NOT triggered for guard endpoints themselves."""
        client = NexusAPIClient(base_url="https://test.local", api_key="k", autoguard=True)
        guard_resp = httpx.Response(
            200,
            json={"verdict": "clean"},
            request=httpx.Request("POST", "https://test.local/v1/oracle/hallucination"),
        )
        client._client = AsyncMock()
        client._client.post = AsyncMock(return_value=guard_resp)
        result = await client.post("/v1/oracle/hallucination", {"text": "test"})
        assert "_guard" not in result  # no recursion
        assert client._client.post.call_count == 1  # exactly one call


# -- Tool decorator tests ----------------------------------------------------


class TestToolHelpers:
    def test_fmt_produces_json(self):
        result = _fmt({"status": "ok", "version": "2.0"})
        parsed = json.loads(result)
        assert parsed["status"] == "ok"

    @pytest.mark.asyncio
    async def test_handle_errors_auth(self):
        @handle_errors
        async def failing_tool():
            raise NexusAuthError("bad key", status_code=401)

        result = json.loads(await failing_tool())
        assert "Authentication failed" in result["error"]

    @pytest.mark.asyncio
    async def test_handle_errors_payment(self):
        @handle_errors
        async def failing_tool():
            raise NexusPaymentRequired("need payment", status_code=402)

        result = json.loads(await failing_tool())
        assert result["error"] == "Payment required"

    @pytest.mark.asyncio
    async def test_handle_errors_rate_limit(self):
        @handle_errors
        async def failing_tool():
            raise NexusRateLimited("slow down", status_code=429, retry_after=5.0)

        result = json.loads(await failing_tool())
        assert result["error"] == "Rate limited"
        assert result["retry_after"] == 5.0

    @pytest.mark.asyncio
    async def test_handle_errors_passes_through_on_success(self):
        @handle_errors
        async def ok_tool():
            return _fmt({"ok": True})

        result = json.loads(await ok_tool())
        assert result["ok"] is True

