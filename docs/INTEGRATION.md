# Integration Guide

Every AAAA-Nexus endpoint is reachable from any language that speaks HTTP + JSON. Pick the most convenient ergonomic layer for your stack.

## Decision matrix

| You are... | Use |
|---|---|
| Building an agent in Claude Code / Cursor / Windsurf | **MCP plugin** (no code — just a config file) |
| Writing a Python backend | **`aaaa-nexus-mcp` Python client** |
| Writing a TS / Node / Deno / Bun service | **`@atomadic/nexus-client` npm package** |
| Working in Go / Rust / Ruby / PHP | **Raw HTTP + Bearer header** |
| Evaluating the API | **curl** |

---

## 1. MCP plugin (Claude, Cursor, VS Code, Zed, Windsurf)

```bash
pip install aaaa-nexus-mcp
```

Then drop one of the configs from [examples/mcp_configs/](../examples/mcp_configs/) into your editor's settings file. Restart. All 140 tools appear as `nexus_*` in the chat.

See [MCP_CLIENTS.md](MCP_CLIENTS.md) for per-editor file paths.

## 2. Python

```bash
pip install aaaa-nexus-mcp
```

```python
import asyncio
from aaaa_nexus_mcp.client import NexusAPIClient

async with NexusAPIClient(api_key="an_...") as c:
    verdict = await c.post("/v1/oracle/hallucination", {"text": "..."})
```

- All methods are async.
- `autoguard=True` by default — every response has a `_guard` block.
- Pass `autoguard=False` to disable.
- See [examples/python_quickstart.py](../examples/python_quickstart.py).

## 3. TypeScript / Node

```bash
npm install @atomadic/nexus-client
```

```ts
import { NexusClient } from "@atomadic/nexus-client";
const nexus = new NexusClient({ apiKey: process.env.AAAA_NEXUS_API_KEY });
```

- Works in Node 18+, Bun, Deno (with `npm:` specifier), Cloudflare Workers.
- Typed namespaces: `nexus.oracle`, `nexus.rag`, `nexus.lora`, `nexus.sys`, `nexus.uep`, `nexus.escrow`, `nexus.rng`.
- Escape hatch: `nexus.post(path, body)`, `nexus.get(path)`.
- See [examples/typescript_quickstart.ts](../examples/typescript_quickstart.ts).

## 4. curl / any language

```bash
curl -sS https://atomadic.tech/v1/oracle/hallucination \
  -H "Authorization: Bearer $AAAA_NEXUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text":"..."}'
```

- Dual-header auth: `Authorization: Bearer <key>` or `X-API-Key: <key>` — both work.
- JSON in, JSON out.
- Free tier endpoints (`/health`, `/v1/rng/quantum`, `/v1/agent/card`, `/v1/metrics`) don't require a key.

## Auth

- Sign up at [atomadic.tech/pay](https://atomadic.tech/pay).
- Keys start with `an_`.
- Send as `Authorization: Bearer an_...` — the client sends both `Authorization` and `X-API-Key` for compatibility.
- Rotate keys in-place; old keys are revoked within 60s globally (Cloudflare edge).

## Rate limits & pricing

- Free tier: 60 req/min, free endpoints only.
- Paid tier: pricing per endpoint — see [TOOLS.md](TOOLS.md). Billed in USDC with on-chain receipts.
- Reputation discount: top 10% of LoRA contributors get 25–50% off every call (see [LORA_REWARDS.md](LORA_REWARDS.md)).

## Errors

All errors return `{ "error": "<code>", "detail": "<human>" }` with the appropriate HTTP status.

| Status | Meaning |
|---|---|
| 401 | Missing or invalid API key |
| 402 | Payment required (insufficient balance) |
| 429 | Rate limited — back off and retry |
| 500 | Backend error — retry with exponential backoff |
