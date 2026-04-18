"""Public release metadata and count-truthfulness checks."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable
from pathlib import Path

from aaaa_nexus_mcp.tools import register_all_tools

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PUBLIC_TOOL_COUNT = 135
COUNT_BEARING_RELEASE_FILES = (
    Path("README.md"),
    Path("docs/INTEGRATION.md"),
    Path("docs/MCP_CLIENTS.md"),
    Path("docs/TOOLS.md"),
    Path("examples/mcp_configs/README.md"),
    Path("plugin.json"),
    Path("server.json"),
    Path("REGISTRY_SUBMISSION.md"),
)
DISALLOWED_TRACKED_PUBLIC_HELPER_FILES = (
    Path("docs/HOMEPAGE_COPY.md"),
    Path("count_tools.py"),
    Path(".pylintrc"),
    Path("pyrightconfig.json"),
)
TOOL_COUNT_PATTERN = re.compile(r"\b(\d+)\b(?=[^\n]{0,32}\btools?\b)")


class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Callable[..., object]] = {}

    def tool(self, name: str | None = None):
        def decorator(fn: Callable[..., object]) -> Callable[..., object]:
            self.tools[name or fn.__name__] = fn
            return fn

        return decorator


def _registered_tool_count() -> int:
    fake_mcp = FakeMCP()
    register_all_tools(fake_mcp, lambda: None)
    return len(fake_mcp.tools)


def _extract_tool_counts(text: str) -> list[int]:
    return [int(match.group(1)) for match in TOOL_COUNT_PATTERN.finditer(text)]


def _status_entries(paths: tuple[Path, ...]) -> dict[str, str]:
    git_status = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all", "--", *[path.as_posix() for path in paths]],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    status_entries: dict[str, str] = {}

    for line in git_status.stdout.splitlines():
        if not line:
            continue

        status_entries[line[3:].strip()] = line[:2]

    return status_entries


def test_required_public_release_files_exist() -> None:
    license_path = ROOT / "LICENSE"
    agents_path = ROOT / "AGENTS.md"

    assert license_path.exists()
    assert agents_path.exists()
    assert "MIT License" in license_path.read_text(encoding="utf-8")


def test_gitignore_ignores_hive_state() -> None:
    gitignore_lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()

    assert ".hive/" in gitignore_lines


def test_agents_md_avoids_absolute_local_repo_paths() -> None:
    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

    assert ":\\!aaaa-" not in agents_text


def test_disallowed_public_helper_files_are_not_tracked() -> None:
    status_entries = _status_entries(DISALLOWED_TRACKED_PUBLIC_HELPER_FILES)
    unexpected_paths = []

    for relative_path in DISALLOWED_TRACKED_PUBLIC_HELPER_FILES:
        status = status_entries.get(relative_path.as_posix())
        if status == "??" or (status and "D" in status):
            continue
        if (ROOT / relative_path).exists():
            unexpected_paths.append(relative_path.as_posix())

    assert not unexpected_paths, f"unexpected tracked helper files: {sorted(unexpected_paths)}"


def test_registered_tool_count_matches_public_release_count() -> None:
    assert _registered_tool_count() == EXPECTED_PUBLIC_TOOL_COUNT


def test_shipped_public_release_files_use_exact_registered_tool_count() -> None:
    registered_tool_count = _registered_tool_count()

    assert registered_tool_count == EXPECTED_PUBLIC_TOOL_COUNT

    for relative_path in COUNT_BEARING_RELEASE_FILES:
        file_text = (ROOT / relative_path).read_text(encoding="utf-8")
        tool_counts = _extract_tool_counts(file_text)

        assert tool_counts, f"{relative_path} must declare the public tool count"
        assert set(tool_counts) == {registered_tool_count}, (
            f"{relative_path} has mismatched public tool counts: {tool_counts}"
        )