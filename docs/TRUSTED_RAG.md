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

## Emitting a trace certificate

Once you've used the retrieved context in a downstream output, certify the full chain:

```python
cert = await c.post("/v1/uep/trace-certify", {
    "final_verdict": "PASS",
    "gate_results": [
        {"gate": "rag_freshness", "verdict": "PASS"},
        {"gate": "hallucination", "verdict": "PASS"},
        {"gate": "drift", "verdict": "PASS"},
    ],
    "evidence_hashes": [r["receipt_hash"] for r in ctx["results"]],
    "public_safe": True,
    "public_safe_summary": "EU AI Act retrieval, 5 trusted chunks",
})
```

The returned `cert_id` is a public-safe reference you can cite in downstream artifacts (PRs, audit trails, compliance docs) without leaking source text.

---

## End-to-end script

See [examples/trusted_rag.py](../examples/trusted_rag.py) for the full cycle.

---

## Why this matters

- **GDPR Art. 22** — automated decisions must be explainable. Receipt chain + trace cert give you that.
- **EU AI Act Annex IV** — technical documentation must include data provenance. The receipt chain is your provenance.
- **NIST AI-RMF** — measurement + accountability. Trusted RAG gives both out of the box.

Every paid Trusted RAG call records to the lineage vault automatically. No extra work required.

