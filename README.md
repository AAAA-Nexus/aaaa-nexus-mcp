# AAAA-Nexus MCP Plugin for Claude Code

Claude Code MCP plugin providing access to the [AAAA-Nexus](https://atomadic.tech) trust, security, compliance, and agent infrastructure API.

## Features

**113 tools** across 16 categories:

| Category | Tools | Highlights |
|---|---|---|
| System | 4 | Health, metrics, pricing, agent card |
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

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `AAAA_NEXUS_API_KEY` | *(none)* | API key for paid endpoints |
| `AAAA_NEXUS_BASE_URL` | `https://atomadic.tech` | API base URL |
| `AAAA_NEXUS_TIMEOUT` | `20.0` | Request timeout in seconds |

## License

MIT
