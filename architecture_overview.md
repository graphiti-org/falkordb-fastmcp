# Repository Architecture Documentation

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture Summary](#architecture-summary)
- [Component Overview](#component-overview)
- [Development Guide](#development-guide)

---

## Overview

### Project Description

The FalkorDB FastMCP Server is a production-ready Python application that implements the Model Context Protocol (MCP) using FastMCP to provide AI models and applications with standardized access to FalkorDB graph databases. It acts as a bridge between MCP clients and FalkorDB instances, exposing tools and resources that translate MCP requests into FalkorDB operations.

The system enables AI models to:
- Execute Cypher queries against graph databases
- Discover available graphs and server capabilities
- Retrieve graph metadata and structure information
- Perform graph database operations through a standardized interface

**Primary Users**: AI applications, LLM tools, graph database clients, and developers building graph-based AI solutions.

### Key Features

- **MCP Protocol Compliance**: Full implementation of Model Context Protocol using Python FastMCP
- **Cypher Query Support**: Execute Cypher queries with parameter support for secure, performant querying
- **Graph Discovery**: List and enumerate available graphs in FalkorDB instances
- **Resource Management**: Expose graphs and server status as MCP resources
- **Clean Architecture**: Follows graphiti-org architectural patterns
- **Python Type Safety**: Comprehensive type hints for better IDE support
- **Minimal Dependencies**: Small, focused dependency tree

### Technology Stack

- **Runtime**: Python 3.11+
- **Framework**: FastMCP 2.13+ (Python MCP framework)
- **Database**: FalkorDB 1.2+ (Graph database)
- **Configuration**: python-dotenv for environment-based configuration
- **Build System**: uv for dependency management
- **Transport**: STDIO (standard MCP transport)

### Architecture Highlights

- **Layered Architecture**: Clean separation between configuration, service layer, and server
- **Singleton Service Pattern**: Single database connection shared across all tool invocations
- **Declarative MCP Tools**: Tools and resources defined using FastMCP decorators
- **Type-Safe Design**: Python type hints throughout for better tooling support
- **Configuration Injection**: Environment-driven configuration with dataclasses
- **Graceful Degradation**: Service continues operating with database reconnection logic

**Key Architectural Decisions**:
1. **Python FastMCP**: Chosen for stability and proven track record (vs TypeScript FastMCP)
2. **STDIO Transport**: Standard MCP transport for maximum compatibility
3. **Minimal Dependencies**: Keep dependency tree small for reliability
4. **dataclass Configuration**: Type-safe configuration management
5. **Singleton Service**: Single database connection for efficiency

---

## Quick Start

### For New Developers

#### Understanding the Codebase

1. **Start here**: Read this README to understand the overall architecture
2. **Explore**: Follow this path through the code:
   - `main.py` - Application entry point
   - `src/falkordb_mcp/server.py` - MCP tools and resources
   - `src/falkordb_mcp/service.py` - Database operations
   - `src/falkordb_mcp/config.py` - Configuration management

#### Running the Project

```bash
# Install dependencies
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your FalkorDB connection details

# Run the server
uv run python main.py

# Or directly
python main.py
```

---

## Architecture Summary

### System Architecture

The FalkorDB FastMCP Server follows a simple layered architecture:

```
┌─────────────────────────────────────┐
│         MCP Clients                 │
│    (Claude Code, Claude Desktop)    │
└──────────────┬──────────────────────┘
               │ STDIO Transport
               ↓
┌─────────────────────────────────────┐
│      FastMCP Server Layer           │
│                                     │
│  ┌────────────────────────────────┐ │
│  │  MCP Tools (@mcp.tool())       │ │
│  │  - execute_query               │ │
│  │  - list_graphs                 │ │
│  │  - get_graph_metadata          │ │
│  └────────────────────────────────┘ │
│                                     │
│  ┌────────────────────────────────┐ │
│  │  MCP Resources                 │ │
│  │  (@mcp.resource())             │ │
│  │  - falkordb://graphs           │ │
│  │  - falkordb://status           │ │
│  └────────────────────────────────┘ │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│       Service Layer                 │
│                                     │
│  ┌────────────────────────────────┐ │
│  │  FalkorDBService (Singleton)   │ │
│  │  - execute_query()             │ │
│  │  - list_graphs()               │ │
│  │  - get_graph_metadata()        │ │
│  └────────────────────────────────┘ │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│        FalkorDB Database            │
└─────────────────────────────────────┘
```

### Architectural Layers

#### 1. Configuration Layer (`config.py`)
- **Purpose**: Centralized configuration management
- **Components**: `FalkorDBConfig` dataclass
- **Responsibilities**:
  - Load environment variables
  - Provide type-safe configuration access
  - Set sensible defaults

#### 2. Service Layer (`service.py`)
- **Purpose**: Database interaction and business logic
- **Components**: `FalkorDBService` class
- **Pattern**: Singleton
- **Responsibilities**:
  - Manage FalkorDB connection
  - Execute Cypher queries
  - List available graphs
  - Retrieve graph metadata
  - Handle database errors

#### 3. Server Layer (`server.py`)
- **Purpose**: MCP protocol implementation
- **Framework**: FastMCP
- **Responsibilities**:
  - Define MCP tools using `@mcp.tool()`
  - Define MCP resources using `@mcp.resource()`
  - Handle tool invocations
  - Format responses for AI consumption
  - Run the MCP server

---

## Component Overview

### Core Components

#### 1. `main.py`
**Purpose**: Application entry point

**Key Functions**:
- Import and execute server's main function
- Ensure proper module resolution

#### 2. `config.py`
**Purpose**: Configuration management

**Key Classes**:
- `FalkorDBConfig`: Connection configuration dataclass

**Environment Variables**:
- `FALKORDB_HOST`: Database host
- `FALKORDB_PORT`: Database port
- `FALKORDB_USERNAME`: Optional username
- `FALKORDB_PASSWORD`: Optional password

#### 3. `service.py`
**Purpose**: Database service layer

**Key Classes**:
- `FalkorDBService`: Singleton service for database operations

**Key Methods**:
- `execute_query(graph_name, query, params)`: Execute Cypher query
- `list_graphs()`: Get all available graphs
- `get_graph_metadata(graph_name)`: Get graph metadata
- `close()`: Clean up database connection

**Patterns**:
- Singleton pattern for connection management
- Error handling with logging
- Lazy initialization

#### 4. `server.py`
**Purpose**: FastMCP server implementation

**MCP Tools**:
- `execute_query`: Execute Cypher queries
- `list_graphs`: List all graphs
- `get_graph_metadata`: Get graph metadata

**MCP Resources**:
- `falkordb://graphs`: Available graphs list
- `falkordb://status`: Server status

**Key Features**:
- JSON response formatting
- Comprehensive error handling
- Timestamp metadata
- Success/failure indicators

---

## Development Guide

### Project Structure

```
falkordb-fastmcp/
├── src/
│   └── falkordb_mcp/
│       ├── __init__.py       # Package initialization
│       ├── config.py          # Configuration
│       ├── service.py         # Database service
│       └── server.py          # MCP server
├── architecture/
│   ├── README.md             # This file
│   ├── docs/                 # Detailed docs
│   └── diagrams/             # Architecture diagrams
├── main.py                    # Entry point
├── pyproject.toml            # Dependencies
├── .env.example              # Config template
└── README.md                 # User documentation
```

### Adding New Tools

To add a new MCP tool:

1. Add the tool function in `server.py`:
```python
@mcp.tool()
def my_new_tool(param1: str, param2: int) -> str:
    """
    Tool description for the AI.

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2

    Returns:
        JSON string with results
    """
    # Implementation
    pass
```

2. If needed, add service layer method in `service.py`

### Adding New Resources

To add a new MCP resource:

```python
@mcp.resource("myresource://uri")
def get_my_resource() -> str:
    """Resource description."""
    return json.dumps({"data": "value"}, indent=2)
```

### Error Handling Pattern

All tools should follow this pattern:

```python
try:
    # Operation
    result = service.operation()

    return json.dumps({
        "success": True,
        "data": result,
        "timestamp": datetime.utcnow().isoformat(),
    }, indent=2)
except Exception as e:
    return json.dumps({
        "success": False,
        "error": str(e),
    }, indent=2)
```

### Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/falkordb_mcp

# Lint code
uv run ruff check .

# Format code
uv run ruff format .
```

### Comparison with TypeScript Version

| Aspect | TypeScript Version | Python Version (This) |
|--------|-------------------|----------------------|
| Framework | Express.js | FastMCP |
| Transport | Custom REST | STDIO (standard MCP) |
| Lines of Code | ~500 | ~200 |
| Dependencies | 40+ | 3 core |
| Deployment | Docker | Simple script |
| Complexity | High | Low |
| MCP Compliance | Partial | Full |

---

## References

- [FastMCP Python Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FalkorDB Documentation](https://www.falkordb.com/)
- [graphiti-org GitHub](https://github.com/graphiti-org)
