# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FalkorDB FastMCP Server - A Python MCP (Model Context Protocol) server for FalkorDB graph database using the FastMCP framework. Enables AI assistants to interact with FalkorDB through standardized tools and resources.

## Commands

```bash
# Install dependencies
uv sync

# Run the server (production)
uv run python main.py

# Run with FastMCP inspector (development)
uv run fastmcp dev server_dev.py

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/test_file.py::test_function

# Linting
uv run ruff check .

# Formatting
uv run ruff format .
```

## Architecture

Three-layer architecture with clear separation of concerns:

```
main.py                    → Entry point (production)
server_dev.py              → Standalone server for FastMCP inspector (no relative imports)
src/falkordb_mcp/
├── config.py              → FalkorDBConfig dataclass, env var loading
├── service.py             → FalkorDBService singleton, database operations
└── server.py              → FastMCP server, @mcp.tool() and @mcp.resource() definitions
```

**Initialization order:** config.py → service.py → server.py (clean dependency flow, no circular imports)

**Key patterns:**
- Singleton service pattern for database connection (`get_service()` in service.py:128-133)
- FastMCP decorators for MCP tools (`@mcp.tool()`) and resources (`@mcp.resource()`)
- All tool responses return JSON strings with `success`, `data`/`error`, and `timestamp` fields
- Configuration via dataclass with `from_env()` factory method
- Lazy service initialization (connection only on first tool call)

## Key Code Locations

| Component | File | Lines |
|-----------|------|-------|
| MCP tool `execute_query` | server.py | 30-72 |
| MCP tool `list_graphs` | server.py | 75-103 |
| MCP tool `get_graph_metadata` | server.py | 106-137 |
| Resource `falkordb://graphs` | server.py | 140-160 |
| Resource `falkordb://status` | server.py | 163-180 |
| `main()` entry point | server.py | 183-189 |
| `FalkorDBService` class | service.py | 13-122 |
| `get_service()` singleton | service.py | 128-133 |
| `FalkorDBConfig` dataclass | config.py | 13-30 |

## Existing MCP Interface

**Tools** (require parameters, perform actions):
- `execute_query(graph_name, query, params?)` - Execute Cypher query
- `list_graphs()` - List all graphs
- `get_graph_metadata(graph_name)` - Get graph labels/schema

**Resources** (read-only, URI-addressed):
- `falkordb://graphs` - Graph list with server info
- `falkordb://status` - Connection status

## Adding MCP Tools

```python
# In server.py
@mcp.tool()
def my_tool(param: str) -> str:
    """Tool description for AI."""
    try:
        service = get_service()
        result = service.operation(param)
        return json.dumps({"success": True, "data": result, "timestamp": datetime.utcnow().isoformat()}, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, indent=2)
```

## Adding MCP Resources

```python
# In server.py
@mcp.resource("falkordb://my-resource")
def get_my_resource() -> str:
    """Resource description."""
    return json.dumps({"data": "value", "timestamp": datetime.utcnow().isoformat()}, indent=2)
```

## Adding Service Layer Operations

When adding database operations, extend `FalkorDBService` in service.py:

```python
# In service.py, inside FalkorDBService class
def my_operation(self, graph_name: str) -> Any:
    """New database operation."""
    try:
        graph = self.client.select_graph(graph_name)
        result = graph.query("CYPHER QUERY")
        return result
    except Exception as e:
        sanitized = graph_name.replace("\n", "").replace("\r", "")  # Log injection prevention
        logger.error(f"Error in my_operation on graph '{sanitized}': {e}")
        raise
```

**Important:** If adding to service.py, also add to server_dev.py (standalone copy for FastMCP inspector).

## Error Handling

Tools catch exceptions and return error JSON (never raise):
```python
try:
    # ... operation
    return json.dumps({"success": True, "data": result, ...})
except Exception as e:
    return json.dumps({"success": False, "error": str(e), "context": "..."})
```

Service layer logs and re-raises (for tool layer to catch):
```python
except Exception as e:
    logger.error(f"Error: {e}")
    raise
```

## Configuration

Environment variables (loaded from `.env`):
- `FALKORDB_HOST` (default: localhost)
- `FALKORDB_PORT` (default: 6379)
- `FALKORDB_USERNAME` (optional)
- `FALKORDB_PASSWORD` (optional)

## Testing

```python
# Direct tool testing (without full MCP flow)
from src.falkordb_mcp.server import execute_query, list_graphs
import json

result = list_graphs()
response = json.loads(result)
assert response["success"] == True

# Direct service testing
from src.falkordb_mcp.service import get_service

service = get_service()
graphs = service.list_graphs()
```

## Architecture Documentation

See `architecture/` for detailed documentation:
- `architecture/README.md` - Overview with Mermaid diagrams
- `architecture/docs/01_component_inventory.md` - All components with line references
- `architecture/docs/03_data_flows.md` - Request/response flow diagrams
- `architecture/docs/04_api_reference.md` - Complete API documentation