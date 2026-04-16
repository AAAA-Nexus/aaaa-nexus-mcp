"""Tool registration dispatcher."""

from __future__ import annotations

import functools
import json
from collections.abc import Callable
from typing import Any

from aaaa_nexus_mcp.errors import (
    NexusAuthError,
    NexusError,
    NexusPaymentRequired,
    NexusRateLimited,
)


def handle_errors(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: catch NexusError subtypes and return structured JSON."""

    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> str:
        try:
            return await fn(*args, **kwargs)
        except NexusAuthError:
            return json.dumps({"error": "Authentication failed. Set AAAA_NEXUS_API_KEY."})
        except NexusPaymentRequired as e:
            return json.dumps({"error": "Payment required", "detail": e.detail})
        except NexusRateLimited as e:
            return json.dumps({"error": "Rate limited", "retry_after": e.retry_after})
        except NexusError as e:
            return json.dumps({"error": e.detail, "status_code": e.status_code})

    return wrapper


def _fmt(result: dict) -> str:
    return json.dumps(result, indent=2)


def register_all_tools(mcp: Any, get_client: Callable) -> None:
    from aaaa_nexus_mcp.tools.aegis import register as r_aegis
    from aaaa_nexus_mcp.tools.compliance import register as r_compliance
    from aaaa_nexus_mcp.tools.control_plane import register as r_control
    from aaaa_nexus_mcp.tools.discovery import register as r_discovery
    from aaaa_nexus_mcp.tools.ecosystem import register as r_ecosystem
    from aaaa_nexus_mcp.tools.escrow import register as r_escrow
    from aaaa_nexus_mcp.tools.inference import register as r_inference
    from aaaa_nexus_mcp.tools.ratchetgate import register as r_ratchet
    from aaaa_nexus_mcp.tools.reputation import register as r_reputation
    from aaaa_nexus_mcp.tools.security import register as r_security
    from aaaa_nexus_mcp.tools.sla import register as r_sla
    from aaaa_nexus_mcp.tools.swarm import register as r_swarm
    from aaaa_nexus_mcp.tools.system import register as r_system
    from aaaa_nexus_mcp.tools.trust import register as r_trust
    from aaaa_nexus_mcp.tools.vanguard import register as r_vanguard
    from aaaa_nexus_mcp.tools.verirand import register as r_verirand

    for reg in (
        r_system,
        r_trust,
        r_security,
        r_compliance,
        r_ratchet,
        r_aegis,
        r_vanguard,
        r_swarm,
        r_discovery,
        r_reputation,
        r_sla,
        r_escrow,
        r_inference,
        r_control,
        r_ecosystem,
        r_verirand,
    ):
        reg(mcp, get_client)
