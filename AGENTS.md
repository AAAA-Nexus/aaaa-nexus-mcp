# AAAA-Nexus MCP

## Build & Test Commands

- Run `python -m pytest -q --no-header -p pytest_asyncio -W always` from the repo root for the full test suite.
- Run `python -m pytest tests/test_plugin_manifest.py tests/test_public_release.py tests/test_tools.py -q --no-header -p pytest_asyncio -W always` before changing public release metadata or tool-count copy.
- Run `python -m pytest tests/test_public_release.py -q --no-header -p pytest_asyncio -W always` before updating any public tool-count claim.

## Public Surface Guardrails

- The registered MCP tool count is the only source of truth for public release counts.
- Keep these shipped MCP-surface files in exact count parity with the registered tool count: `README.md`, `docs/INTEGRATION.md`, `docs/MCP_CLIENTS.md`, `docs/TOOLS.md`, `examples/mcp_configs/README.md`, `plugin.json`, `server.json`, and `REGISTRY_SUBMISSION.md`.
- Draft storefront copy and local editor/dev helpers should not ship in the public repo when equivalent public docs or tests already exist.

## Storefront Boundary

- Do not edit storefront prompt-pack files from this repo.
- Storefront prompt packs are maintained in the storefront project and handled in separate work.
