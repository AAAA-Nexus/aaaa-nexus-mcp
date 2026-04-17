#!/usr/bin/env python3
"""Agent self-gating — an agent that refuses to ship code that fails trust + lint.

Pattern: before commit, the agent POSTs its diff to /v1/sys/lint_gate. Only
a PASS verdict allows the commit to proceed. Receipts are recorded in the
tamper-evident lineage vault automatically.

Run:
    export AAAA_NEXUS_API_KEY="an_your_key_here"
    python examples/agent_self_gate.py
"""

import asyncio
import os
import sys

from aaaa_nexus_mcp.client import NexusAPIClient

DIFF = """
-def divide(a, b): return a / b
+def divide(a, b):
+    if b == 0:
+        raise ValueError("division by zero")
+    return a / b
"""


async def main() -> None:
    async with NexusAPIClient(api_key=os.environ.get("AAAA_NEXUS_API_KEY")) as c:
        gate = await c.post(
            "/v1/sys/lint_gate",
            {
                "diff": DIFF,
                "language": "python",
                "trust_threshold": 0.75,
                "lint_threshold": 0.95,
            },
        )
        verdict = gate.get("verdict", "UNKNOWN")
        print("lint gate verdict:", verdict)
        print("receipt:", gate.get("receipt_hash"))

        if verdict != "PASS":
            print("Refusing to commit — gate did not pass.")
            sys.exit(1)

        print("Safe to commit.")


if __name__ == "__main__":
    asyncio.run(main())
