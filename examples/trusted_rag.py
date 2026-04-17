#!/usr/bin/env python3
"""Trusted RAG cycle — provenance-gated retrieval with tamper-evident receipts.

Ordinary RAG: vector index returns whatever matches. You trust it. You lose.

Trusted RAG: every chunk is gated on source allowlist, freshness, hallucination
verdict, and drift score. Each result ships with a SHA-256 receipt chained to
the lineage vault.

Run:
    export AAAA_NEXUS_API_KEY="an_your_key_here"
    python examples/trusted_rag.py
"""

import asyncio
import os

from aaaa_nexus_mcp.client import NexusAPIClient


async def main() -> None:
    async with NexusAPIClient(api_key=os.environ.get("AAAA_NEXUS_API_KEY")) as c:
        # 1. Pull trusted context.
        ctx = await c.post(
            "/v1/rag/augment",
            {
                "query": "latest EU AI Act Annex IV requirements for foundation models",
                "max_results": 5,
                "freshness_hours": 168,  # one week
                "source_policy": "trusted_only",
                "required_domains": ["europa.eu", "nist.gov", "iso.org"],
            },
        )
        print("retrieved", len(ctx.get("results", [])), "trusted chunks")
        for r in ctx.get("results", []):
            print(f"  - {r.get('source_url')} trust={r.get('trust_score')}")

        # 2. Every response is auto-guarded — verify the _guard block.
        guard = ctx.get("_guard", {})
        print("hallucination verdict:", guard.get("hallucination", {}).get("verdict"))
        print("drift detected:", guard.get("drift", {}).get("drift_detected"))

        # 3. Optional — emit a trace certificate for audit trail.
        cert = await c.post(
            "/v1/uep/trace-certify",
            {
                "final_verdict": "PASS",
                "gate_results": [
                    {"gate": "rag_freshness", "verdict": "PASS"},
                    {"gate": "hallucination", "verdict": guard.get("hallucination", {}).get("verdict", "UNKNOWN")},
                    {"gate": "drift", "verdict": "PASS" if not guard.get("drift", {}).get("drift_detected") else "FAIL"},
                ],
                "evidence_hashes": [r.get("receipt_hash", "") for r in ctx.get("results", [])],
                "public_safe": True,
                "public_safe_summary": "EU AI Act Annex IV retrieval, 5 trusted chunks",
            },
        )
        print("trace certificate:", cert.get("cert_id"))


if __name__ == "__main__":
    asyncio.run(main())
