# AAAA-Nexus

**The trustless agent economy stack.** 146 endpoints. Eight capabilities you cannot get anywhere else. One HTTP surface — callable from MCP, Python, TypeScript, curl, or any language that speaks JSON.

```
pip install aaaa-nexus-mcp           # Python + Claude / Cursor / Codex MCP
npm  install aaaa-nexus-sdk  # TypeScript / Node / Deno / Bun
curl https://atomadic.tech/health    # or skip the SDK entirely
```

No key needed for the free tier. Grab one at [atomadic.tech/pay](https://atomadic.tech/pay) when you want the paid surface.

---

## Why agents call AAAA-Nexus directly

Your agent is already writing code, making decisions, and spending tokens. What it **cannot** do on its own:

1. Prove its outputs aren't hallucinated.
2. Detect drift before it compounds.
3. Share a LoRA adapter with the rest of the swarm.
4. Earn rewards when its fixes train the next model.
5. Pull trusted RAG context with provenance receipts.
6. Gate its own commits on a tamper-evident lint + trust score.
7. Escrow a payment on outcome-based delivery.
8. Certify its trace for EU AI Act Annex IV, GDPR Art. 22, and NIST AI-RMF.

AAAA-Nexus does all eight. At the HTTP layer. In one call.

---

## The two flywheels that matter

### 1. Shared LoRA — *earn while you code*

Every `(buggy_code → fix)` pair your agent produces is a training sample. Contribute it to the shared pool and you get back:

- **Discounted or free API calls** (reputation-tier pricing)
- **Prize draws** on accepted sample milestones
- **Leaderboard placement** (visible on [atomadic.tech](https://atomadic.tech))
- **Access to the community-trained adapter** for your language

The loop is four calls:

```python
from aaaa_nexus_mcp.client import NexusAPIClient

async with NexusAPIClient(api_key="an_...") as c:
    # 1. Capture locally (free, PII-scrubbed, hash-chained)
    await c.post("/v1/lora/capture", {"bad": bad, "good": good, "language": "python"})

    # 2. Contribute the buffered batch (micro-rebate per accepted sample)
    await c.post("/v1/lora/contribute", {"min_quality": 0.6})

    # 3. Pull the current community adapter
    adapter = await c.get("/v1/lora/adapter/python")

    # 4. Claim your reputation reward
    await c.post("/v1/lora/reward/claim", {"agent_id": "my-agent-001"})
```

See [examples/lora_flywheel.py](examples/lora_flywheel.py) for the end-to-end script.

### 2. Trusted RAG cycle — *provenance or it didn't happen*

Ordinary RAG pulls whatever the vector index returns. Trusted RAG gates each chunk on:

- Source domain allowlist
- Freshness window
- Hallucination oracle verdict on the retrieved text
- Drift score against the live knowledge graph
- Tamper-evident receipt (SHA-256 chained to the lineage vault)

```python
ctx = await c.post("/v1/rag/augment", {
    "query": "latest EU AI Act Annex IV requirements",
    "max_results": 5,
    "freshness_hours": 168,
    "source_policy": "trusted_only",
    "required_domains": ["europa.eu", "nist.gov"],
})
# ctx["results"][i] includes: text, source_url, trust_score, receipt_hash
```

Every response ships with a `_guard` block: `{hallucination, drift, guarded_at}`. You never have to run those checks yourself.

See [examples/trusted_rag.py](examples/trusted_rag.py) for the full cycle including certificate emission.

---

## The eight capabilities

| # | Capability | Representative endpoints | What it solves |
|---|---|---|---|
| 1 | **Trust oracles** | `/v1/oracle/hallucination`, `/v1/trust/decay` | Hallucination + drift verdicts on any text |
| 2 | **Shared LoRA loop** | `/v1/lora/contribute`, `/v1/lora/reward/claim` | Earn rewards contributing fixes; pull the community adapter |
| 3 | **Trusted RAG** | `/v1/rag/augment`, `/v1/aibom/drift` | Provenance-gated retrieval with receipts |
| 4 | **Sys primitives** | `/v1/sys/trust_gate`, `/v1/sys/lint_gate`, `/v1/sys/chain_parity` | Numerical invariants for agent self-governance |
| 5 | **Compliance certs** | `/v1/compliance/eu-ai-act`, `/v1/compliance/explain` | EU AI Act, GDPR Art. 22, NIST conformance |
| 6 | **Escrow + SLA** | `/v1/escrow/create`, `/v1/sla/report` | Outcome-based USDC billing with arbitration |
| 7 | **VeriRand** | `/v1/rng/quantum`, `/v1/vrf/draw` | HMAC-proven randomness, on-chain VRF draws |

Tools per category:

| Category | Tools | Category | Tools |
|---|---|---|---|
| System | 4 | Security | 8 |
| Sys Primitives | 14 | Compliance | 14 |
| LoRA Training | 7 | RatchetGate | 4 |
| Trusted RAG | 2 | AEGIS / VANGUARD | 7 |
| Trust Oracles | 6 | Agent Swarm | 11 |
| Discovery | 3 | Reputation | 4 |
| SLA | 4 | Escrow | 5 |
| Inference | 8 | Control Plane | 10 |
| Ecosystem | 21 | VeriRand | 4 |

**Total: 134 tools across 18 categories.** Full list: [docs/TOOLS.md](docs/TOOLS.md).

---

## Infrastructure that agents call directly

One base URL. Bearer auth. JSON in / JSON out. Every response is already guarded.

```
POST https://atomadic.tech/v1/<category>/<verb>
Authorization: Bearer an_your_key
Content-Type: application/json
```

The MCP plugin, the Python SDK, the npm package, and your own curl calls all hit the same surface. No SDK lock-in, no proprietary wire format, no required ceremony beyond a Bearer header.

---

## Enhancement Architect System Prompts

AAAA-Nexus ships curated system prompts that turn any LLM into a **self-improving agent** wired to the trust + LoRA + RAG stack:

- `dada.system.md` — Delegator Atomadic Developer Agent (routes tasks, verifies in a separate lane)
- `atomadic.system.md` — Intent interpreter & prompt refiner
- `autopoetic.system.md` — Self-healing feedback loop

See [prompts/](prompts/) for the full catalogue. Drop any of them into your `CLAUDE.md`, `.cursorrules`, or system prompt field and the agent starts calling `nexus_*` tools automatically.

---

## Quickstarts — pick your lane

### 1. Claude Code / Cursor / VS Code (MCP)

Install once:

```bash
pip install aaaa-nexus-mcp
```

Add to `~/.claude/settings.json` or project `.mcp.json`:

```json
{
  "mcpServers": {
    "aaaa-nexus": {
      "command": "python",
      "args": ["-m", "aaaa_nexus_mcp"],
      "env": { "AAAA_NEXUS_API_KEY": "an_your_key_here" }
    }
  }
}
```

Restart the editor. All 146 endpoints are now available as `nexus_*` in your chat. See [examples/mcp_configs/](examples/mcp_configs/) for Cursor, Claude Desktop, VS Code, Zed, and Windsurf.

### 2. Python

```bash
pip install aaaa-nexus-mcp
```

```python
import asyncio
from aaaa_nexus_mcp.client import NexusAPIClient

async def main():
    async with NexusAPIClient(api_key="an_...") as c:
        verdict = await c.post("/v1/oracle/hallucination",
                               {"text": "The moon is made of Swiss cheese."})
        print(verdict)  # {"verdict": "FAIL", "POLICY_EPSILON": 0.93, "_guard": {...}}

asyncio.run(main())
```

Full script: [examples/python_quickstart.py](examples/python_quickstart.py).

### 3. TypeScript / Node / Deno / Bun

```bash
npm install aaaa-nexus-sdk
```

```ts
import { NexusClient } from "aaaa-nexus-sdk";

const nexus = new NexusClient({ apiKey: process.env.AAAA_NEXUS_API_KEY });
const verdict = await nexus.oracle.hallucination({ text: "The moon is made of Swiss cheese." });
console.log(verdict);
```

Full script: [examples/typescript_quickstart.ts](examples/typescript_quickstart.ts). Package source: [clients/typescript/](clients/typescript/).

### 4. curl (any language)

```bash
curl -sS https://atomadic.tech/v1/oracle/hallucination \
  -H "Authorization: Bearer $AAAA_NEXUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text":"The moon is made of Swiss cheese."}'
```

Full script: [examples/curl_quickstart.sh](examples/curl_quickstart.sh).

---

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `AAAA_NEXUS_API_KEY` | *(none)* | Bearer token for paid tools |
| `AAAA_NEXUS_BASE_URL` | `https://atomadic.tech` | API base URL |
| `AAAA_NEXUS_TIMEOUT` | `20.0` | Request timeout (seconds) |
| `AAAA_NEXUS_AUTOGUARD` | `1` | Annotate every response with hallucination + drift verdicts |

Free tier endpoints that work without a key: `/health`, `/v1/rng/quantum`, `/v1/agent/card`, `/v1/metrics`.

---

## Documentation

- [docs/INTEGRATION.md](docs/INTEGRATION.md) — language-by-language integration guide
- [docs/TOOLS.md](docs/TOOLS.md) — full 140-tool catalogue with pricing
- [docs/LORA_REWARDS.md](docs/LORA_REWARDS.md) — rewards program, leaderboard, prize mechanics
- [docs/TRUSTED_RAG.md](docs/TRUSTED_RAG.md) — RAG cycle, provenance, receipt format
- [docs/MCP_CLIENTS.md](docs/MCP_CLIENTS.md) — editor-by-editor setup (Claude, Cursor, VS Code, Zed, Windsurf)

## Examples

- [examples/python_quickstart.py](examples/python_quickstart.py)
- [examples/typescript_quickstart.ts](examples/typescript_quickstart.ts)
- [examples/curl_quickstart.sh](examples/curl_quickstart.sh)
- [examples/lora_flywheel.py](examples/lora_flywheel.py) — earn rewards loop
- [examples/trusted_rag.py](examples/trusted_rag.py) — provenance-gated retrieval
- [examples/agent_self_gate.py](examples/agent_self_gate.py) — agent that gates its own commits
- [examples/mcp_configs/](examples/mcp_configs/) — drop-in configs for every MCP editor

## License
Source: Business Source License 1.1 (see LICENSE in main repo). Generated OpenAPI schema: CC BY-ND 4.0.
# AAAA-Nexus MCP Plugin for Claude Code

Claude Code MCP plugin providing access to the [AAAA-Nexus](https://atomadic.tech) trust, security, compliance, and agent infrastructure API.

## Features

**134 tools** across 18 categories:

| Category | Tools | Highlights |
|---|---|---|
| System | 4 | Health, metrics, pricing, agent card |
| Sys Primitives | 14 | Trust/lint gates, VQ memory, novelty & parity checks, budgets |
| LoRA Training | 7 | Federated fix-capture, contribute, adapter pull, rewards |
| Trusted RAG | 2 | Provenance-gated retrieval, AIBOM drift |
| Trust Oracles | 6 | Hallucination detection, trust scoring, entropy |
| Security | 8 | Prompt injection scan, threat scoring, PQC signatures |
| Compliance | 14 | EU AI Act, NIST, fairness, audit, drift detection |
| RatchetGate | 4 | Session security with 47-epoch cycle |
| AEGIS | 3 | MCP firewall, epistemic routing, epoch certification |
| VANGUARD | 4 | Red-teaming, MEV governance, escrow lock |
| Agent Swarm | 11 | Registration, topology, planning, contradiction check |
| Discovery | 3 | Capability search, recommendations, registry |
| Reputation | 4 | Score, history, record, dispute |
| SLA | 4 | Register, report, status, breach |
| Escrow | 5 | Create, release, dispute, arbitrate |
| Inference | 8 | AI inference, embeddings, text analysis, routing |
| Control Plane | 10 | Authorization, spending, lineage, federation |
| Ecosystem | 21 | Consensus, quota, sagas, memory fence, governance |
| VeriRand | 4 | Quantum RNG, VRF draws with on-chain proof |

## Setup

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Install dependencies

```bash
pip install aaaa-nexus-mcp
```

Or from source:

```bash
git clone https://github.com/AAAA-Nexus/aaaa-nexus-mcp
cd aaaa-nexus-mcp
pip install -e .
```

### Configure API key

Free-tier endpoints (`nexus_health`, `nexus_rng_quantum`, `nexus_agent_card`, `nexus_metrics`) work without a key. For paid tools, get a key at https://atomadic.tech/pay.

Set the environment variable:

```bash
export AAAA_NEXUS_API_KEY="an_your_key_here"
```

Or pass it via your client's MCP config (see below). **Never commit keys to source control.**

### Add to Claude Code

Add to your Claude Code settings (`~/.claude/settings.json` or project `.mcp.json`):

```json
{
  "mcpServers": {
    "aaaa-nexus": {
      "command": "python",
      "args": ["-m", "aaaa_nexus_mcp"],
      "env": {
        "AAAA_NEXUS_API_KEY": "an_your_key_here"
      }
    }
  }
}
```

### Test

```bash
# Verify server starts (Ctrl+C to exit)
python -m aaaa_nexus_mcp

# Quick Python test
python -c "
import asyncio
from aaaa_nexus_mcp.client import NexusAPIClient
async def t():
    async with NexusAPIClient() as c:
        print(await c.get('/health'))
asyncio.run(t())
"
```

## Tool naming

All tools are prefixed with `nexus_` to avoid collisions in Claude Code's flat tool namespace. Examples:

- `nexus_health` — API health check
- `nexus_hallucination_oracle` — check text for confabulation
- `nexus_prompt_inject_scan` — scan for adversarial injection
- `nexus_ratchet_register` — start a secure session
- `nexus_agent_plan` — decompose a goal into steps

Use primitive tools such as `nexus_trust_gate`, `nexus_friction_score`, and `nexus_lora_contribute` when you need one exact backend capability. Compose them with your own agent logic to build phase-gated pipelines.

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `AAAA_NEXUS_API_KEY` | *(none)* | API key for paid endpoints |
| `AAAA_NEXUS_BASE_URL` | `https://atomadic.tech` | API base URL |
| `AAAA_NEXUS_TIMEOUT` | `20.0` | Request timeout in seconds |

## License
Source: Business Source License 1.1 (see LICENSE in main repo). Generated OpenAPI schema: CC BY-ND 4.0.


