# Registry submission checklist

This document tracks submissions of `aaaa-nexus-mcp` to public MCP registries.

## 0. Prerequisites (do once)

- [ ] Push the repo to `https://github.com/AAAA-Nexus/aaaa-nexus-mcp` (public).
- [ ] Tag release `v0.1.0` and create a GitHub Release.
- [ ] Publish to PyPI: `python -m build && twine upload dist/*` (name: `aaaa-nexus-mcp`).
- [ ] Publish the Docker image: `docker build -t ghcr.io/aaaa-nexus/aaaa-nexus-mcp:0.1.0 . && docker push ...`

The files below are ready to go:
- `server.json` — official MCP registry manifest
- `smithery.yaml` + `Dockerfile` — Smithery config

## 1. Official MCP registry (registry.modelcontextprotocol.io)

Docs: https://github.com/modelcontextprotocol/registry

Install the publisher CLI and submit:

```powershell
# One-time install
winget install modelcontextprotocol.mcp-publisher
# or: go install github.com/modelcontextprotocol/registry/cmd/mcp-publisher@latest

mcp-publisher login github
mcp-publisher publish
```

The CLI reads `server.json` from the repo root and validates the PyPI package exists.

## 2. Community servers list (github.com/modelcontextprotocol/servers)

File a PR adding a row to the README's "Community Servers" table:

```markdown
| [AAAA-Nexus](https://github.com/AAAA-Nexus/aaaa-nexus-mcp) | AI trust, safety, compliance, agent swarm, escrow, and verifiable randomness via the atomadic.tech API (113 tools). |
```

Open: https://github.com/modelcontextprotocol/servers/edit/main/README.md

## 3. Smithery (smithery.ai)

Docs: https://smithery.ai/docs/build/project-config

1. Go to https://smithery.ai/new
2. Connect GitHub → select `AAAA-Nexus/aaaa-nexus-mcp`
3. Smithery auto-detects `smithery.yaml` + `Dockerfile` and builds the image.

## 4. mcp.so

https://mcp.so/submit — submit via the web form with the GitHub URL.

## 5. Glama.ai

https://glama.ai/mcp/servers — submit via the Glama portal with the GitHub URL; Glama auto-ingests `server.json`.

## 6. PulseMCP

https://www.pulsemcp.com/submit — submit via web form.

## 7. Awesome MCP lists

PRs to add a line in:
- https://github.com/punkpeye/awesome-mcp-servers
- https://github.com/appcypher/awesome-mcp-servers

Suggested entry:

```markdown
- [AAAA-Nexus](https://github.com/AAAA-Nexus/aaaa-nexus-mcp) — 113 AI trust, safety, compliance, escrow, swarm and verifiable-randomness tools over the atomadic.tech API. `python` `stdio`
```
