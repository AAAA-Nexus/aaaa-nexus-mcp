#!/usr/bin/env python3
"""End-to-end Shared LoRA flywheel — capture, contribute, pull adapter, claim reward.

This is the loop that earns you discounted / free API calls, leaderboard
placement, and prize-draw entries.

Run:
    export AAAA_NEXUS_API_KEY="an_your_key_here"
    python examples/lora_flywheel.py
"""

import asyncio
import os

from aaaa_nexus_mcp.client import NexusAPIClient

AGENT_ID = os.environ.get("AAAA_NEXUS_AGENT_ID", "my-agent-001")

# Imagine your agent just fixed this bug in its own output.
BAD_CODE = """
def divide(a, b):
    return a / b
"""

GOOD_CODE = """
def divide(a, b):
    if b == 0:
        raise ValueError("division by zero")
    return a / b
"""


async def main() -> None:
    async with NexusAPIClient(api_key=os.environ.get("AAAA_NEXUS_API_KEY")) as c:
        # 1. Capture — free, PII-scrubbed, hash-chained, held in local buffer.
        capture = await c.post(
            "/v1/lora/capture",
            {
                "bad": BAD_CODE,
                "good": GOOD_CODE,
                "language": "python",
                "lint_delta": 1,
                "error_type": "ZeroDivisionError",
            },
        )
        print("capture:", capture)

        # 2. Contribute the buffered batch to the shared pool.
        #    Server tau-gates each sample; only passes accrue rewards.
        contribute = await c.post(
            "/v1/lora/contribute",
            {"min_quality": 0.6, "agent_id": AGENT_ID},
        )
        print("contribute:", contribute)

        # 3. Check training run status + your leaderboard position.
        status = await c.get("/v1/lora/status")
        print("status:", status)

        # 4. Pull the current community-trained adapter for your language.
        adapter = await c.get("/v1/lora/adapter/python")
        print("current adapter:", adapter)

        # 5. Claim your accumulated reputation reward.
        #    Rewards include: discounted calls, prize-draw entries,
        #    leaderboard placement, bonus credits.
        reward = await c.post(
            "/v1/lora/reward/claim",
            {"agent_id": AGENT_ID},
        )
        print("reward:", reward)


if __name__ == "__main__":
    asyncio.run(main())
