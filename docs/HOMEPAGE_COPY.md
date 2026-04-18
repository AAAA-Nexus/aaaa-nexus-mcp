# Homepage Copy — Refactored Sections

> Draft only. For atomadic.tech storefront refresh. **Do not push to public surfaces until backend is production-green.**

---

## Hero

**Developer infrastructure for trustworthy agents.**
135 tools across 7 capability areas. One HTTP surface.

`pip install aaaa-nexus-mcp` · `npm install @atomadic/nexus-client` · `curl atomadic.tech/health`

[Get started → /docs](https://atomadic.tech/docs/mcp) · [Get a key → /pay](https://atomadic.tech/pay)

---

## Section 1 — Infrastructure that agents call directly

Your agent already writes code, makes decisions, and spends tokens. It can't:

- Prove its output isn't hallucinated.
- Detect drift before it compounds.
- Earn rewards when its fixes train the next adapter.
- Pull RAG context with tamper-evident provenance.
- Gate its own commits on lint + trust score.
- Escrow a payment on outcome-based delivery.
- Certify its trace for EU AI Act, GDPR, and NIST.

AAAA-Nexus does all of that at the HTTP layer. Bearer auth. JSON in, JSON out. Every response auto-guarded.

---

## Section 2 — Agent Workflow Patterns

Three operating patterns you can use to turn any LLM into a self-improving agent:

- **DADA** — Delegator Atomadic Developer Agent. Routes, verifies, ships.
- **Atomadic** — Intent interpreter that sharpens any user prompt into an actionable form.
- **Autopoetic** — Self-healing feedback loop for drift-resistant agents.

Use them as starting points in `CLAUDE.md`, `.cursorrules`, or your system prompt when you want the agent to use `nexus_*` tools on the first turn.

---

## Section 3 — Capability overview

One base URL. Seven capabilities. Zero lock-in.

| Capability | What it gives you |
| --- | --- |
| Trust oracles | Hallucination + drift verdicts on any text |
| **Shared LoRA loop** | Earn rewards contributing fixes; pull the community adapter |
| **Trusted RAG** | Provenance-gated retrieval with SHA-256 receipts |
| Sys primitives | Numerical invariants for agent self-governance |
| Compliance certs | EU AI Act, GDPR Art. 22, NIST AI-RMF |
| Escrow + SLA | Outcome-based USDC billing with arbitration |
| VeriRand | HMAC-proven randomness, on-chain VRF draws |

---

## Section 4 — Seven capability areas

### 1. Trust oracles

Hallucination verdict in one call. `/v1/oracle/hallucination` returns `POLICY_EPSILON` + `verdict`. No other API gives you this.

### 2. Shared LoRA with rewards

Contribute a `(bad → good)` code fix. Get paid in:

- Discounted / free API calls (reputation tier pricing)
- Prize-draw entries on training milestones
- Leaderboard placement
- Access to the community-trained adapter

The only federated LoRA loop that pays you to improve it.

### 3. Trusted RAG cycle

Every chunk gated on source allowlist, freshness, hallucination verdict, drift score. Every result ships with a tamper-evident receipt. RAG you can actually audit.

### 4. Sys primitives

`trust_gate`, `lint_gate`, `chain_parity`, `friction_score`, `novelty_jump` — numerical invariants your agent uses to govern itself between calls.

### 5. Compliance as a primitive

EU AI Act Annex IV conformity, GDPR Art. 22 explainability, NIST AI-RMF. One call each. Certificates chained to the lineage vault.

### 6. Escrow + SLA

Lock USDC, release on outcome proof, arbitrate disputes. Pay for what actually worked.

### 7. VeriRand

Quantum-seeded RNG with HMAC proofs. VRF draws with on-chain verification. Your random numbers are actually random, and you can prove it.

---

## Section 5 — Install in 30 seconds

Three tabs. Pick your stack.

### Python

```bash
pip install aaaa-nexus-mcp
```

```python
import asyncio

from aaaa_nexus_mcp.client import NexusAPIClient


async def main() -> None:
  async with NexusAPIClient(api_key="an_...") as client:
    verdict = await client.post("/v1/oracle/hallucination", {"text": "..."})
    print(verdict)


asyncio.run(main())
```

### TypeScript

```bash
npm install @atomadic/nexus-client
```

```ts
import { NexusClient } from "@atomadic/nexus-client";
const nexus = new NexusClient({ apiKey: process.env.AAAA_NEXUS_API_KEY });
const verdict = await nexus.oracle.hallucination({ text: "..." });
```

### MCP (Claude, Cursor, VS Code, Zed, Windsurf)

```json
{
  "mcpServers": {
    "aaaa-nexus": {
      "command": "python",
      "args": ["-m", "aaaa_nexus_mcp"],
      "env": { "AAAA_NEXUS_API_KEY": "an_..." }
    }
  }
}
```

---

## Section 6 — Footer CTAs

**Start free** · No key needed for `/health`, `/v1/rng/quantum`, `/v1/agent/card`, `/v1/metrics`.
**Go paid** · [atomadic.tech/pay](https://atomadic.tech/pay) · Pay per call in USDC · Top LoRA contributors get 25–50% off every call.
