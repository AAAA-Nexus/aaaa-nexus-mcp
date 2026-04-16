"""Lightweight async httpx wrapper for the AAAA-Nexus API."""

from __future__ import annotations

from typing import Any

import httpx

from aaaa_nexus_mcp.errors import (
    NexusConnectionError,
    NexusTimeoutError,
    raise_for_status,
)


class NexusAPIClient:
    """Async HTTP client for AAAA-Nexus endpoints.

    Auth is sent as dual headers: Authorization: Bearer + X-API-Key.
    """

    def __init__(
        self,
        *,
        base_url: str = "https://atomadic.tech",
        api_key: str | None = None,
        timeout: float = 20.0,
    ) -> None:
        headers: dict[str, str] = {"User-Agent": "aaaa-nexus-mcp/0.1.0"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-API-Key"] = api_key
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers=headers,
        )

    async def get(self, path: str, **params: Any) -> dict:
        try:
            resp = await self._client.get(path, params=params or None)
        except httpx.ConnectError as e:
            raise NexusConnectionError(str(e), endpoint=path) from e
        except httpx.TimeoutException as e:
            raise NexusTimeoutError(str(e), endpoint=path) from e
        if resp.status_code == 402:
            return self._handle_x402(resp, path)
        raise_for_status(resp.status_code, endpoint=path, detail=resp.text)
        return resp.json()

    async def post(self, path: str, body: dict | None = None) -> dict:
        try:
            resp = await self._client.post(path, json=body or {})
        except httpx.ConnectError as e:
            raise NexusConnectionError(str(e), endpoint=path) from e
        except httpx.TimeoutException as e:
            raise NexusTimeoutError(str(e), endpoint=path) from e
        if resp.status_code == 402:
            return self._handle_x402(resp, path)
        raise_for_status(resp.status_code, endpoint=path, detail=resp.text)
        return resp.json()

    @staticmethod
    def _handle_x402(resp: httpx.Response, path: str) -> dict:
        try:
            body = resp.json()
        except (ValueError, KeyError):
            body = {}
        return {
            "payment_required": True,
            "amount_usdc": body.get("amount") or body.get("price_usdc", 0),
            "network": body.get("network", "base"),
            "treasury": body.get("address") or body.get("treasury", ""),
            "endpoint": path,
            "detail": body.get("detail") or body.get("message", "Payment required"),
        }

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> NexusAPIClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()
