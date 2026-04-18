import sys
sys.path.append("src")
try:
    from aaaa_nexus_mcp.tools import register_all_tools
except ImportError:
    # Handle possible path variations
    from aaaa_nexus_mcp.server import register_all_tools

class FakeCollector:
    def __init__(self):
        self.tools = []
    def tool(self, name=None):
        def decorator(func):
            self.tools.append(name or func.__name__)
            return func
        return decorator

collector = FakeCollector()
try:
    # Some register_all_tools might take a second argument (like get_client)
    # If it fails with 1 arg, try with None (mocking get_client)
    register_all_tools(collector)
except TypeError:
    register_all_tools(collector, lambda: None)

print(f"Count: {len(collector.tools)}")
print(f"Sample: {sorted(collector.tools)[:10]}")
