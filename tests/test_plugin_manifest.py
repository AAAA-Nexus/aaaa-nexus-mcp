"""Commercial metadata checks for the root plugin manifest."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_plugin_manifest_is_aaaa_nexus_branded() -> None:
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))

    assert manifest["name"] == "aaaa-nexus-mcp"
    assert manifest["version"] == "0.1.0"
    assert manifest["author"]["name"] == "Atomadic"
    assert manifest["repository"] == "https://github.com/AAAA-Nexus/aaaa-nexus-mcp"
    assert "agent-hive" not in json.dumps(manifest).lower()


def test_plugin_manifest_preserves_agent_skill_hook_wiring() -> None:
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))

    assert manifest["agents"] == [".github/agents"]
    assert manifest["skills"] == [".github/skills/*"]
    assert manifest["hooks"] == [".github/hooks/*"]
    assert manifest["instructions"] == [".github/instructions"]


def test_plugin_interface_has_commercial_discovery_metadata() -> None:
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    interface = manifest["interface"]

    assert interface["displayName"] == "AAAA-Nexus MCP"
    assert interface["category"] == "Developer Tools"
    assert interface["websiteURL"] == "https://atomadic.tech"
    assert interface["privacyPolicyURL"] == "https://atomadic.tech/legal"
    assert interface["termsOfServiceURL"] == "https://atomadic.tech/legal"
    assert len(interface["defaultPrompt"]) <= 3
    assert all(len(prompt) <= 128 for prompt in interface["defaultPrompt"])
