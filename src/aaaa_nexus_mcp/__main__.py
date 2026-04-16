"""Entry point: python -m aaaa_nexus_mcp"""

from aaaa_nexus_mcp.server import mcp

mcp.run(transport="stdio")
