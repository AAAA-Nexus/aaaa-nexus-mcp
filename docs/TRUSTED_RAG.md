# Trusted RAG Cycle

Ordinary RAG hands your agent whatever the vector index returns. You don't know if the source is fresh, authoritative, or even real. **Trusted RAG gates every chunk and emits a receipt you can show an auditor.**

---

## What gets gated

Every chunk returned by `/v1/rag/augment` passes through:

1. **Source allowlist** (`required_domains`) — reject anything outside your trusted set.
2. **Freshness window** (`freshness_hours`) — reject stale content.
3. **Hallucination oracle** (`/v1/oracle/hallucination`) — reject fabricated-looking text.
4. **Drift score** (`/v1/aibom/drift`) — reject content that has drifted from the live knowledge graph.
5. **Receipt chain** — every surviving chunk gets a SHA-256 receipt linked to the tamper-evident lineage vault.

---

## Request

```python
ctx = await c.post("/v1/rag/augment", {
    "query": "latest EU AI Act Annex IV requirements",
    "max_results": 5,
    "freshness_hours": 168,
    "source_policy": "trusted_only",      # or "open" to skip the allowlist
    "required_domains": ["europa.eu", "nist.gov"],
})
```

## Response shape

```json
{
  "results": [
    {
      "text": "...",
      "source_url": "https://europa.eu/...",
      "source_domain": "europa.eu",
      "fetched_at": 1713...,
      "trust_score": 0.94,
      "hallucination_verdict": "PASS",
      "drift_score": 0.02,
      "receipt_hash": "sha256:abc123..."
    }
  ],
  "query_receipt": "sha256:def456...",
  "_guard": {
    "hallucination": { "POLICY_EPSILON": 0.12, "verdict": "PASS" },
    "drift": { "drift_detected": false, "delta": 0.03 },
    "guarded_at": 1713...
  }
}
```

---

## Policy options

| `source_policy` | Behavior |
|---|---|
| `trusted_only` | Only return chunks from `required_domains` or the platform-maintained trusted list. |
| `open` | Return all matching chunks but annotate with trust scores (you decide what to use). |

---

## Lineage receipts

Every retrieval returns a `receipt_hash` per chunk. These hashes are tamper-evident and safe to embed in downstream artifacts (PRs, audit trails, compliance docs) as proof that the context was actually retrieved through the trusted pipeline:

```python
for r in ctx["results"]:
    print(r["receipt_hash"], r["trust_score"], r["source"])
```

You can recompute the hash over `(chunk_text, source_url, freshness_ts)` to verify the Worker didn't silently substitute content.

---

## End-to-end script

See [examples/trusted_rag.py](../examples/trusted_rag.py) for the full cycle.

---

## Why this matters

- **GDPR Art. 22** — automated decisions must be explainable. Receipt chain + trace cert give you that.
- **EU AI Act Annex IV** — technical documentation must include data provenance. The receipt chain is your provenance.
- **NIST AI-RMF** — measurement + accountability. Trusted RAG gives both out of the box.

Every paid Trusted RAG call records to the lineage vault automatically. No extra work required.

