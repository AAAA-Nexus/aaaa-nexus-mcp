#!/usr/bin/env python3
"""Python quickstart for AAAA-Nexus.

Install:
    pip install aaaa-nexus-mcp

Run:
    export AAAA_NEXUS_API_KEY="an_your_key_here"
    python examples/python_quickstart.py
"""

import asyncio
import os

from aaaa_nexus_mcp.client import NexusAPIClient


async def main() -> None:
    api_key = os.environ.get("AAAA_NEXUS_API_KEY")

    async with NexusAPIClient(api_key=api_key) as c:
        # 1. Health (free — no key required)
        health = await c.get("/health")
        print("health:", health)

        # 2. Hallucination oracle
        verdict = await c.post(
            "/v1/oracle/hallucination",
            {"text": "The moon is made of Swiss cheese."},
        )
        print("hallucination verdict:", verdict)

        # 3. Quantum RNG (free, HMAC-proven)
        rng = await c.get("/v1/rng/quantum?count=8")
        print("quantum rng:", rng)

        # 4. Trust gate on a proposed output
        gate = await c.post(
            "/v1/sys/trust_gate",
            {"text": "The capital of France is Paris.", "threshold": 0.75},
        )
        print("trust gate:", gate)


if __name__ == "__main__":
    asyncio.run(main())
