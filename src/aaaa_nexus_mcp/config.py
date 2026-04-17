"""Configuration from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class NexusConfig:
    base_url: str
    api_key: str | None
    timeout: float
    autoguard: bool  # Run hallucination + drift check on every response


def get_config() -> NexusConfig:
    return NexusConfig(
        base_url=os.environ.get("AAAA_NEXUS_BASE_URL", "https://atomadic.tech"),
        api_key=os.environ.get("AAAA_NEXUS_API_KEY") or None,
        timeout=float(os.environ.get("AAAA_NEXUS_TIMEOUT", "20.0")),
        autoguard=os.environ.get("AAAA_NEXUS_AUTOGUARD", "true").lower() not in ("0", "false", "no"),
    )
