/**
 * TypeScript quickstart for AAAA-Nexus.
 *
 * Install:
 *   npm install @atomadic/nexus-client
 *
 * Run (Node 20+ or Bun):
 *   export AAAA_NEXUS_API_KEY="an_your_key_here"
 *   npx tsx examples/typescript_quickstart.ts
 */

import { NexusClient } from "@atomadic/nexus-client";

async function main() {
  const nexus = new NexusClient({
    apiKey: process.env.AAAA_NEXUS_API_KEY,
  });

  // 1. Health (free)
  console.log("health:", await nexus.health());

  // 2. Hallucination oracle
  const verdict = await nexus.oracle.hallucination({
    text: "The moon is made of Swiss cheese.",
  });
  console.log("hallucination verdict:", verdict);

  // 3. Quantum RNG (free, HMAC-proven)
  console.log("quantum rng:", await nexus.rng.quantum({ count: 8 }));

  // 4. Trusted RAG augment
  const ctx = await nexus.rag.augment({
    query: "latest EU AI Act Annex IV requirements",
    maxResults: 3,
    freshnessHours: 720,
    sourcePolicy: "trusted_only",
  });
  console.log("trusted rag results:", ctx);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
