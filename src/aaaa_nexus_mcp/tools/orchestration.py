"""Public orchestration helpers for shipped repo assets.

The MAP = TERRAIN gate compares requested capabilities against assets that
actually ship in this repository. Unsupported capability types are rejected.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

from aaaa_nexus_mcp.tools import _fmt, handle_errors

_CAPABILITY_TYPES = ("tools",)

_REPO_PATH_BY_TYPE = {
    "tools": "src/aaaa_nexus_mcp/tools",
}

_FUEL_BY_TYPE = {
    "tools": 0.05,
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", value.strip().lower()).strip("_")


def _capability_type(raw_type: str) -> str | None:
    normalized = raw_type.strip().lower().replace("-", "_")
    aliases = {
        "tool": "tools",
        "tools": "tools",
    }
    return aliases.get(normalized)


def _discover_inventory() -> dict[str, set[str]]:
    return {
        "tools": discover_mcp_tool_names(),
    }


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
    inventory = _discover_inventory()

    inventory_check: dict[str, dict[str, str]] = {key: {} for key in _CAPABILITY_TYPES}
    missing: list[dict[str, Any]] = []
    invalid_types: list[str] = []

    for raw_type, names in required_capabilities.items():
        cap_type = _capability_type(raw_type)
        if cap_type is None:
            invalid_types.append(str(raw_type))
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
            recommended_path = _REPO_PATH_BY_TYPE[cap_type]
            missing.append({
                "name": str(name),
                "type": cap_label,
                "inventory_source": recommended_path,
                "specification": (
                    f"{cap_label} '{name}' is required before executing: "
                    f"{task_description}. Provide a stable JSON-compatible interface, "
                    f"cyclomatic complexity <= {cc}, sandbox_test_required={sandbox}."
                ),
                "recommended_path": recommended_path,
                "recommended_follow_up": (
                    f"Add the missing {cap_type[:-1]} under {recommended_path} and rerun "
                    "nexus_map_terrain."
                ),
                "estimated_fuel_cost": _FUEL_BY_TYPE[cap_type],
                "verification_criteria": [
                    "Specification is explicit and testable.",
                    "Passes positive and negative fixture tests.",
                    f"Cyclomatic complexity <= {cc}.",
                    "Passes sandbox execution test.",
                ],
                "human_approval_required": False,
            })

    if invalid_types:
        return {
            "verdict": "INVALID_INPUT",
            "error": "unsupported_capability_type",
            "supported_types": list(_CAPABILITY_TYPES),
            "unsupported_types": sorted(set(invalid_types)),
            "next_action": "Use only supported capability types and retry nexus_map_terrain.",
        }

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
        and all(item["type"].lower() == "tool" for item in missing)
    )
    return {
        "verdict": "HALT_AND_INVENT",
        "agent_id": agent_id,
        "missing_capabilities": missing,
        "inventory_check": inventory_check,
        "development_plan": {
            "steps": [
                "1. Add or update the missing repo asset in the recommended path.",
                "2. Add or update tests covering the new asset.",
                "3. Re-run the relevant verification commands.",
                "4. Retry the original task with nexus_map_terrain.",
            ],
            "total_estimated_time_seconds": max(30, len(missing) * 60),
            "auto_invent_eligible": auto_allowed,
        },
        "next_action": "Execute development plan before retrying original task.",
    }


def register(mcp: Any, _get_client: Callable) -> None:
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
        """MAP = TERRAIN gate for shipped MCP tools."""
        return _fmt(map_terrain_payload(
            task_description=task_description,
            required_capabilities=required_capabilities,
            agent_id=agent_id,
            max_development_budget_usdc=max_development_budget_usdc,
            auto_invent_if_missing=auto_invent_if_missing,
            invention_constraints=invention_constraints,
        ))
