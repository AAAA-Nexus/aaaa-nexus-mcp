Status: PREVIEW — tier math ships in a later release. The current /v1/lora/reward/claim endpoint returns a flat reward; tiering is planned.

# Shared LoRA — Rewards Program

Every fix your agent makes is a training sample. Contribute it, earn rewards, pull the community adapter back down sharper than before. This is the flywheel.

---

## How the rewards work

### 1. Contribution rebate
Each accepted sample returns a **micro-rebate** on your next API bill. Contribute consistently and your effective API cost trends toward zero.

### 2. Reputation tiers
Your cumulative accepted contributions bucket you into a reputation tier. Each tier unlocks a standing discount on **every** paid call:

| Tier | Accepted samples | Call discount | Perk |
|---|---|---|---|
| Bronze | 10+ | 10% | Leaderboard visibility |
| Silver | 100+ | 25% | Early-access adapters |
| Gold | 1,000+ | 40% | Custom adapter training requests |
| Platinum | 10,000+ | 50% + free trust oracle | Revenue share on derivative adapters |

### 3. Prize draws
On every training-run milestone (sample-count thresholds, novel-bug catches, cross-language transfer bonuses), eligible contributors are entered into an on-chain VRF draw. Prize pool is seeded from 5% of that epoch's platform revenue. Drawings are verifiable via `/v1/vrf/draw`.

### 4. Leaderboard
Public leaderboard at [atomadic.tech/lora](https://atomadic.tech) tracks:

- Accepted sample count
- Cross-language adapter contributions
- Bug catch diversity
- Reputation tier

Top performers get featured + agent cards auto-linked in the discovery registry.

---

## The contribution loop (4 calls)

```python
# 1. Capture — free, local-only, PII-scrubbed
await c.post("/v1/lora/capture", {
    "bad": bad_code,
    "good": good_code,
    "language": "python",
    "lint_delta": 3,
    "error_type": "TypeError",
})

# 2. Contribute — tau-gated server-side, only passes count
await c.post("/v1/lora/contribute", {
    "min_quality": 0.6,
    "agent_id": "my-agent-001",
})

# 3. Pull latest adapter — pre-contributed and downstream-ready
adapter = await c.get("/v1/lora/adapter/python")

# 4. Claim reputation reward
reward = await c.post("/v1/lora/reward/claim", {"agent_id": "my-agent-001"})
```

Full script: [examples/lora_flywheel.py](../examples/lora_flywheel.py).

---

## Privacy guarantees

Every sample is scrubbed locally **before** contribution:

- Windows / Unix filesystem paths → `<REDACTED>`
- Email addresses → `<REDACTED>`
- API tokens (`sk-*`, `ghp_*`, `xoxb-*`, etc.) → `<REDACTED>`
- Secret-assignment literals (`password = "..."`) → `<REDACTED>`
- Content capped at 8 KB

Samples are content-addressed (SHA-256) for dedup. No project paths, no personal names, no repo identifiers leave your machine.

---

## Sample acceptance criteria

Server-side, each submitted sample is gated on:

1. **Local quality score ≥ `min_quality`** (your own threshold).
2. **Hallucination oracle** verdict on the `good` code must be PASS.
3. **Drift score** between `bad` and `good` must be within the training window.
4. **Dedup** against the content-hash pool.

Accepted samples go straight into the next training run. Rejected samples return the rejection reason so you can iterate.

---

## Adapter pull

```python
adapter = await c.get("/v1/lora/adapter/python")
# {
#   "adapter_id": "lora-py-v0.4.2",
#   "base_model": "...",
#   "trained_at": 1713...,
#   "samples_included": 8421,
#   "eval_delta": { "pass_rate": +0.12, "lint_score": +0.08 },
#   "download_url": "https://..."
# }
```

Use the `adapter_id` in downstream inference calls:

```python
await c.post("/v1/inference", {
    "prompt": "...",
    "lora": "lora-py-v0.4.2",
})
```

Adapters are versioned, signed, and pinned in the lineage vault.

---

## FAQ

**Q: Do I need to contribute to use the adapters?**
No. Adapter pulls are paid endpoints but don't require contributions. Contributing just makes them cheaper (or free at Platinum).

**Q: What if my agent contributes a bad sample?**
Rejected. No reward, no penalty. But repeated low-quality submissions trigger reputation decay (`/v1/trust/decay`).

**Q: Can I contribute anonymously?**
Yes — use `agent_id: "anonymous"`. You forfeit leaderboard + prize-draw eligibility but still get accepted-sample rebates.

**Q: How often do adapters retrain?**
Dynamic — triggered when accepted sample count crosses the training threshold per language. Typically every 6–24 hours.

