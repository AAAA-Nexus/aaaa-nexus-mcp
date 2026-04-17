#!/usr/bin/env bash
# curl quickstart for AAAA-Nexus.
# Run with: bash examples/curl_quickstart.sh

set -euo pipefail

BASE="${AAAA_NEXUS_BASE_URL:-https://atomadic.tech}"
KEY="${AAAA_NEXUS_API_KEY:-}"
AUTH=()
if [[ -n "$KEY" ]]; then
  AUTH=(-H "Authorization: Bearer $KEY")
fi

echo "== health (free) =="
curl -sS "$BASE/health"
echo

echo "== quantum rng (free) =="
curl -sS "$BASE/v1/rng/quantum?count=4"
echo

echo "== hallucination oracle =="
curl -sS "$BASE/v1/oracle/hallucination" \
  "${AUTH[@]}" \
  -H "Content-Type: application/json" \
  -d '{"text":"The moon is made of Swiss cheese."}'
echo

echo "== trusted RAG augment =="
curl -sS "$BASE/v1/rag/augment" \
  "${AUTH[@]}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "latest EU AI Act Annex IV requirements",
    "max_results": 3,
    "freshness_hours": 720,
    "source_policy": "trusted_only"
  }'
echo
