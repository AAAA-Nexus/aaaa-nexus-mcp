"""Lightweight async httpx wrapper for the AAAA-Nexus API.

Autoguard
---------
When ``autoguard=True`` (the default, controlled by ``AAAA_NEXUS_AUTOGUARD`` env
var), every non-guard POST response is annotated with a ``_guard`` block:

    "_guard": {
        "hallucination": { "POLICY_EPSILON": ..., "verdict": ... },
        "drift":         { "drift_detected": ..., "delta": ... },
        "guarded_at":    <unix timestamp>
    }

Both guard calls run concurrently via ``asyncio.gather`` -- zero serial latency.
Guard endpoints themselves are excluded from auto-guarding (no recursion).
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from aaaa_nexus_mcp.errors import (
    NexusConnectionError,
    NexusTimeoutError,
    raise_for_status,
)

# Paths that ARE guards -- never auto-guard these (prevents infinite recursion)
_GUARD_PATHS: frozenset[str] = frozenset({
    "/v1/oracle/hallucination",
    "/v1/aibom/drift",
    "/v1/trust/decay",
    "/health",
    "/v1/metrics",
})


class NexusAPIClient:
    """Async HTTP client for AAAA-Nexus endpoints.

    Auth is sent as dual headers: Authorization: Bearer + X-API-Key.
    Pass autoguard=True (default) to annotate every response with hallucination
    and drift verdicts via a parallel ``_guard`` block.
    """

    def __init__(
        self,
        *,
        base_url: str = "https://atomadic.tech",
        api_key: str | None = None,
        timeout: float = 20.0,
        autoguard: bool = True,
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
        self._autoguard = autoguard

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
        result: dict = resp.json()
        if self._autoguard and path not in _GUARD_PATHS:
            result = await self._annotate_with_guards(result)
        return result

    async def _annotate_with_guards(self, result: dict) -> dict:
        """Run hallucination + drift in parallel and attach as _guard metadata."""
        import json as _json

        payload_text = _json.dumps(result)

        async def _hallucination() -> dict:
            try:
                return await self.post("/v1/oracle/hallucination", {"text": payload_text})
            except Exception:  # noqa: BLE001
                return {"error": "guard_unavailable"}

        async def _drift() -> dict:
            try:
                return await self.post("/v1/aibom/drift", {"payload": payload_text})
            except Exception:  # noqa: BLE001
                return {"error": "guard_unavailable"}

        hallucination, drift = await asyncio.gather(_hallucination(), _drift())
        result["_guard"] = {
            "hallucination": hallucination,
            "drift": drift,
            "guarded_at": int(time.time()),
        }
        return result

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

