"""UEP orchestration tools.

The MAP = TERRAIN gate enforces the axiom:
if the technology needed for the task does not exist, halt and invent it.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from aaaa_nexus_mcp.tools import _fmt, handle_errors

_CAPABILITY_TYPES = ("agents", "hooks", "skills", "tools", "harnesses")

_BASE_INVENTORY: dict[str, set[str]] = {
    "agents": {
        "dada_prime",
        "build_captain",
        "review_tribunal",
        "safety_sentinel",
        "quota_quartermaster",
        "ledger_scribe",
        "memory_fence_keeper",
    },
    "hooks": {
        "nexus_trust_gate",
        "nexus_lint_gate",
        "nexus_chain_parity",
        "nexus_hallucination_oracle",
        "nexus_aegis_mcp_proxy",
        "nexus_map_terrain",
    },
    "skills": {
        "mcp_discovery",
        "trusted_rag_design",
        "lora_capture",
        "prompt_boundary_review",
        "capability_gap_analysis",
    },
    "tools": set(),
    "harnesses": {
        "cloudflare_worker_mcp",
        "fastmcp_stdio",
        "redacted_admin_probe",
        "pytest",
    },
}

_CREATION_TOOL_BY_TYPE = {
    "agents": "nexus_spawn_agent",
    "hooks": "nexus_synthesize_verified_code",
    "skills": "nexus_synthesize_verified_code",
    "tools": "nexus_synthesize_verified_code",
    "harnesses": "nexus_secure_handoff",
}

_FUEL_BY_TYPE = {
    "agents": 0.08,
    "hooks": 0.04,
    "skills": 0.03,
    "tools": 0.05,
    "harnesses": 0.10,
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower()).strip("_")


def _capability_type(raw_type: str) -> str | None:
    normalized = raw_type.strip().lower().replace("-", "_")
    aliases = {
        "agent": "agents",
        "agents": "agents",
        "hook": "hooks",
        "hooks": "hooks",
        "skill": "skills",
        "skills": "skills",
        "tool": "tools",
        "tools": "tools",
        "harness": "harnesses",
        "harnesses": "harnesses",
    }
    return aliases.get(normalized)


def discover_mcp_tool_names() -> set[str]:
    """Discover locally registered Nexus MCP tool function names from source."""
    tools_dir = Path(__file__).resolve().parent
    names: set[str] = {"nexus_map_terrain"}
    pattern = re.compile(r"async\s+def\s+(nexus_[a-zA-Z0-9_]+)\s*\(")
    for path in tools_dir.glob("*.py"):
        if path.name.startswith("__"):
            continue
        try:
            names.update(pattern.findall(path.read_text(encoding="utf-8")))
        except OSError:
            continue
    return names


def map_terrain_payload(
    *,
    task_description: str,
    required_capabilities: dict[str, list[str]],
    agent_id: str = "aaaa-nexus-agent",
    max_development_budget_usdc: float = 1.0,
    auto_invent_if_missing: bool = False,
    invention_constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a MAP = TERRAIN verdict and invention plan."""
    constraints = invention_constraints or {}
    inventory = {key: set(value) for key, value in _BASE_INVENTORY.items()}
    inventory["tools"].update(discover_mcp_tool_names())

    inventory_check: dict[str, dict[str, str]] = {key: {} for key in _CAPABILITY_TYPES}
    missing: list[dict[str, Any]] = []

    for raw_type, names in required_capabilities.items():
        cap_type = _capability_type(raw_type)
        if cap_type is None:
            continue
        for name in names or []:
            normalized = _slug(str(name))
            exists = normalized in inventory[cap_type]
            if not exists and cap_type == "tools" and not normalized.startswith("nexus_"):
                exists = f"nexus_{normalized}" in inventory[cap_type]
            inventory_check[cap_type][str(name)] = "exists" if exists else "missing"
            if exists:
                continue
            cc = constraints.get("max_cyclomatic_complexity", 7)
            sandbox = constraints.get("sandbox_test_required", True)
            cap_label = cap_type[:-1].title()
            missing.append({
                "name": str(name),
                "type": cap_label,
                "specification": (
                    f"{cap_label} '{name}' is required before executing: "
                    f"{task_description}. Provide a stable JSON-compatible interface, "
                    f"cyclomatic complexity <= {cc}, sandbox_test_required={sandbox}."
                ),
                "recommended_creation_tool": _CREATION_TOOL_BY_TYPE[cap_type],
                "estimated_fuel_cost": _FUEL_BY_TYPE[cap_type],
                "verification_criteria": [
                    "Specification is explicit and testable.",
                    "Passes positive and negative fixture tests.",
                    f"Cyclomatic complexity <= {cc}.",
                    "Passes sandbox execution test.",
                ],
                "human_approval_required": cap_type in {"agents", "harnesses"},
            })

    if not missing:
        return {
            "verdict": "PROCEED",
            "missing_capabilities": [],
            "inventory_check": inventory_check,
            "next_action": "Continue to Phase 3 synthesis.",
        }

    total_cost = sum(item["estimated_fuel_cost"] for item in missing)
    auto_allowed = (
        auto_invent_if_missing
        and total_cost <= max_development_budget_usdc
        and all(item["type"].lower() in {"tool", "skill"} for item in missing)
    )
    return {
        "verdict": "HALT_AND_INVENT",
        "agent_id": agent_id,
        "missing_capabilities": missing,
        "inventory_check": inventory_check,
        "development_plan": {
            "steps": [
                "1. Synthesize capability specification.",
                "2. Generate implementation candidate.",
                "3. Verify in sandbox.",
                "4. Register in Asset Memory.",
                "5. Retry original task.",
            ],
            "total_estimated_time_seconds": max(30, len(missing) * 60),
            "auto_invent_triggered": auto_allowed,
        },
        "next_action": "Execute development plan before retrying original task.",
    }


def register(mcp: Any, get_client: Callable) -> None:
    @mcp.tool()
    @handle_errors
    async def nexus_map_terrain(
        task_description: str,
        required_capabilities: dict[str, list[str]],
        agent_id: str = "aaaa-nexus-agent",
        max_development_budget_usdc: float = 1.0,
        auto_invent_if_missing: bool = False,
        invention_constraints: dict[str, Any] | None = None,
    ) -> str:
        """MAP = TERRAIN gate: halt and invent missing agents, hooks, skills, tools, or harnesses."""
        return _fmt(map_terrain_payload(
            task_description=task_description,
            required_capabilities=required_capabilities,
            agent_id=agent_id,
            max_development_budget_usdc=max_development_budget_usdc,
            auto_invent_if_missing=auto_invent_if_missing,
            invention_constraints=invention_constraints,
        ))
