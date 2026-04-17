# Tool Catalogue

140 tools across 19 categories. All are prefixed `nexus_` in MCP clients and map 1:1 to HTTP endpoints on `https://atomadic.tech`.

**Free-tier endpoints** (no key required): `nexus_health`, `nexus_rng_quantum`, `nexus_agent_card`, `nexus_metrics`.

---

## System (4)

| Tool | Endpoint | Price | Description |
|---|---|---|---|
| `nexus_health` | `GET /health` | free | API liveness |
| `nexus_metrics` | `GET /v1/metrics` | free | Platform telemetry |
| `nexus_pricing` | `GET /v1/pricing` | free | Machine-readable price manifest |
| `nexus_agent_card` | `GET /v1/agent/card` | free | A2A capability manifest |

## Sys Primitives (14)

Numerical invariants for agent self-governance. See [INTEGRATION.md](INTEGRATION.md).

| Tool | Endpoint | Price |
|---|---|---|
| `nexus_sys_constants` | *(local)* | free |
| `nexus_vq_memory_store` | `POST /v1/sys/vq/store` | $0.020 |
| `nexus_vq_memory_query` | `POST /v1/sys/vq/query` | $0.010 |
| `nexus_trust_gate` | `POST /v1/sys/trust_gate` | $0.060 |
| `nexus_lint_gate` | `POST /v1/sys/lint_gate` | $0.040 |
| `nexus_payload_decompose` | `POST /v1/sys/payload_decompose` | $0.020 |
| `nexus_delegation_depth` | `POST /v1/sys/delegation` | $0.005 |
| `nexus_session_ratchet` | `POST /v1/sys/session_ratchet` | $0.010 |
| `nexus_friction_score` | `POST /v1/sys/friction` | $0.010 |
| `nexus_variant_rotate` | `POST /v1/sys/variant_rotate` | $0.040 |
| `nexus_chain_parity` | `POST /v1/sys/chain_parity` | $0.020 |
| `nexus_novelty_jump` | `POST /v1/sys/novelty_jump` | $0.030 |
| `nexus_fuel_budget_create` | `POST /v1/sys/budget/create` | $0.040 |
| `nexus_fuel_budget_spend` | `POST /v1/sys/budget/spend` | $0.010 |

## LoRA Training (7)

The rewards flywheel. See [LORA_REWARDS.md](LORA_REWARDS.md).

| Tool | Endpoint | Price |
|---|---|---|
| `nexus_lora_capture_fix` | *(local)* | free |
| `nexus_lora_buffer_inspect` | *(local)* | free |
| `nexus_lora_buffer_clear` | *(local)* | free |
| `nexus_lora_contribute` | `POST /v1/lora/contribute` | $0.010 |
| `nexus_lora_status` | `GET /v1/lora/status` | $0.005 |
| `nexus_lora_adapter_current` | `GET /v1/lora/adapter/{lang}` | $0.010 |
| `nexus_lora_reward_claim` | `POST /v1/lora/reward/claim` | $0.020 |

## Trust Oracles (6), Security (8), Compliance (14), RatchetGate (4), AEGIS/VANGUARD (7), Agent Swarm (11), Discovery (3), Reputation (4), SLA (4), Escrow (5), Inference (8), Control Plane (10), Ecosystem (21), VeriRand (4)

See the in-code registration sites for the full list:

- [src/aaaa_nexus_mcp/tools/trust.py](../src/aaaa_nexus_mcp/tools/trust.py)
- [src/aaaa_nexus_mcp/tools/security.py](../src/aaaa_nexus_mcp/tools/security.py)
- [src/aaaa_nexus_mcp/tools/compliance.py](../src/aaaa_nexus_mcp/tools/compliance.py)
- [src/aaaa_nexus_mcp/tools/ratchetgate.py](../src/aaaa_nexus_mcp/tools/ratchetgate.py)
- [src/aaaa_nexus_mcp/tools/aegis.py](../src/aaaa_nexus_mcp/tools/aegis.py)
- [src/aaaa_nexus_mcp/tools/vanguard.py](../src/aaaa_nexus_mcp/tools/vanguard.py)
- [src/aaaa_nexus_mcp/tools/swarm.py](../src/aaaa_nexus_mcp/tools/swarm.py)
- [src/aaaa_nexus_mcp/tools/discovery.py](../src/aaaa_nexus_mcp/tools/discovery.py)
- [src/aaaa_nexus_mcp/tools/reputation.py](../src/aaaa_nexus_mcp/tools/reputation.py)
- [src/aaaa_nexus_mcp/tools/sla.py](../src/aaaa_nexus_mcp/tools/sla.py)
- [src/aaaa_nexus_mcp/tools/escrow.py](../src/aaaa_nexus_mcp/tools/escrow.py)
- [src/aaaa_nexus_mcp/tools/inference.py](../src/aaaa_nexus_mcp/tools/inference.py)
- [src/aaaa_nexus_mcp/tools/control_plane.py](../src/aaaa_nexus_mcp/tools/control_plane.py)
- [src/aaaa_nexus_mcp/tools/ecosystem.py](../src/aaaa_nexus_mcp/tools/ecosystem.py)
- [src/aaaa_nexus_mcp/tools/verirand.py](../src/aaaa_nexus_mcp/tools/verirand.py)

Or query live pricing:

```bash
curl https://atomadic.tech/v1/pricing | jq
```
