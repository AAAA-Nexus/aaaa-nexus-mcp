from __future__ import annotations

from aaaa_nexus_mcp.tools.orchestration import discover_mcp_tool_names, map_terrain_payload


def test_discover_mcp_tool_names_includes_map_terrain() -> None:
    names = discover_mcp_tool_names()
    assert "nexus_map_terrain" in names
    assert "nexus_health" in names


def test_map_terrain_proceeds_for_existing_tool() -> None:
    result = map_terrain_payload(
        task_description="Check API health.",
        required_capabilities={"tools": ["nexus_health"]},
    )
    assert result["verdict"] == "PROCEED"
    assert result["inventory_check"]["tools"]["nexus_health"] == "exists"


def test_map_terrain_halts_for_missing_agent() -> None:
    result = map_terrain_payload(
        task_description="Scan Python code for OWASP findings.",
        required_capabilities={"agents": ["security_scanner"]},
    )
    assert result["verdict"] == "HALT_AND_INVENT"
    assert result["missing_capabilities"][0]["name"] == "security_scanner"
    assert result["missing_capabilities"][0]["recommended_creation_tool"] == "nexus_spawn_agent"


def test_map_terrain_auto_invent_only_for_tool_or_skill() -> None:
    result = map_terrain_payload(
        task_description="Run missing scanner.",
        required_capabilities={"tools": ["nexus_semgrep_scan"]},
        auto_invent_if_missing=True,
    )
    assert result["verdict"] == "HALT_AND_INVENT"
    assert result["development_plan"]["auto_invent_triggered"] is True
