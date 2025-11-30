# Component Inventory

## Overview

The FalkorDB FastMCP codebase is a Model Context Protocol (MCP) server that provides an interface for interacting with FalkorDB graph databases. The architecture follows a clean three-layer design pattern:

- **Entry Points**: Application launchers (`main.py`, `server_dev.py`)
- **Public API Layer**: MCP server interface (`server.py`) exposing tools and resources
- **Service Layer**: Database operations abstraction (`service.py`)
- **Configuration Layer**: Environment-based configuration (`config.py`)

The codebase is organized as a Python package under `src/falkordb_mcp/` with additional entry point scripts at the root level. It implements the FastMCP framework to expose FalkorDB graph database capabilities through the Model Context Protocol.

## Public API

### Modules

| Module | Path | Description |
|--------|------|-------------|
| `falkordb_mcp` | `src/falkordb_mcp/__init__.py` | Package root with version information |
| `falkordb_mcp.server` | `src/falkordb_mcp/server.py` | MCP server implementation with tools and resources |
| `falkordb_mcp.service` | `src/falkordb_mcp/service.py` | FalkorDB service layer for database operations |
| `falkordb_mcp.config` | `src/falkordb_mcp/config.py` | Configuration management |

### MCP Tools (Public API Surface)

These are the primary public API methods exposed through the MCP protocol:

| Tool | Location | Description |
|------|----------|-------------|
| `execute_query()` | `src/falkordb_mcp/server.py:31-72` | Execute Cypher queries against FalkorDB graphs |
| `list_graphs()` | `src/falkordb_mcp/server.py:75-103` | List all available graphs in the FalkorDB instance |
| `get_graph_metadata()` | `src/falkordb_mcp/server.py:106-137` | Get metadata and labels for a specific graph |

### MCP Resources (Public API Surface)

| Resource | URI | Location | Description |
|----------|-----|----------|-------------|
| `get_available_graphs()` | `falkordb://graphs` | `src/falkordb_mcp/server.py:140-160` | Resource providing list of all available graphs |
| `get_server_status()` | `falkordb://status` | `src/falkordb_mcp/server.py:163-180` | Resource providing FalkorDB connection status |

### Classes

| Class | Path | Lines | Description |
|-------|------|-------|-------------|
| `FalkorDBConfig` | `src/falkordb_mcp/config.py:14-30` | Configuration dataclass for FalkorDB connection parameters |
| `FalkorDBService` | `src/falkordb_mcp/service.py:13-121` | Service class encapsulating FalkorDB database operations |

### Functions

| Function | Path | Lines | Visibility | Description |
|----------|------|-------|------------|-------------|
| `main()` | `src/falkordb_mcp/server.py:183-189` | Public | Main entry point for MCP server execution |
| `get_service()` | `src/falkordb_mcp/service.py:128-133` | Public | Factory function for singleton service instance |

## Internal Implementation

### Core Modules

| Module | Path | Role |
|--------|------|------|
| `service.py` | `src/falkordb_mcp/service.py` | Core database abstraction layer; manages FalkorDB client lifecycle and query execution |
| `config.py` | `src/falkordb_mcp/config.py` | Configuration management; loads and validates environment variables |
| `server.py` | `src/falkordb_mcp/server.py` | MCP protocol implementation; exposes tools and resources |

### Internal Classes and Methods

#### FalkorDBConfig

**Location**: `src/falkordb_mcp/config.py:14-30`

**Attributes**:
- `host: str` - FalkorDB server hostname (line 17)
- `port: int` - FalkorDB server port (line 18)
- `username: Optional[str]` - Authentication username (line 19)
- `password: Optional[str]` - Authentication password (line 20)

**Methods**:
- `from_env()` (lines 22-30) - Class method to create config from environment variables

#### FalkorDBService

**Location**: `src/falkordb_mcp/service.py:13-121`

**Private Attributes**:
- `_client: Optional[FalkorDB]` - Internal FalkorDB client instance (line 18)

**Private Methods**:
- `_initialize()` (lines 21-37) - Initialize database connection with error handling

**Public Properties**:
- `client` (lines 39-44) - Property providing access to FalkorDB client with validation

**Public Methods**:
- `execute_query()` (lines 46-72) - Execute Cypher query with parameter support
- `list_graphs()` (lines 74-88) - Retrieve list of all graphs from database
- `get_graph_metadata()` (lines 90-114) - Get graph metadata including labels
- `close()` (lines 116-121) - Clean up database connection

### Helper/Utility Modules

| Component | Path | Purpose |
|-----------|------|---------|
| Global config instance | `src/falkordb_mcp/config.py:34` | Singleton configuration object initialized from environment |
| Global service instance | `src/falkordb_mcp/service.py:125` | Singleton service object for database operations |
| MCP server instance | `src/falkordb_mcp/server.py:27` | FastMCP server instance named "FalkorDB" |
| Logger instances | Multiple locations | Standard Python logging configured in server.py:19-24 and service.py:10 |

### Standalone Development Module

| Module | Path | Purpose |
|--------|------|---------|
| `server_dev.py` | `server_dev.py` | Standalone version with no relative imports for FastMCP inspector compatibility |

**Note**: `server_dev.py` is a self-contained version duplicating all functionality from the main package for development and testing purposes. It contains inline implementations of `FalkorDBConfig`, `FalkorDBService`, and all MCP tools/resources (289 lines).

## Entry Points

### Primary Entry Point

| File | Path | Description | Usage |
|------|------|-------------|-------|
| `main.py` | `main.py:1-7` | Production entry point | Imports and calls `main()` from `src.falkordb_mcp.server` |

**Entry flow**:
```
main.py:7 (__main__)
  -> src.falkordb_mcp.server.main():184
    -> mcp.run():189
```

### Development Entry Point

| File | Path | Description | Usage |
|------|------|-------------|-------|
| `server_dev.py` | `server_dev.py:1-289` | Development/inspector entry point | Self-contained server for FastMCP dev tools |

**Purpose**: Provides a standalone server without relative imports for compatibility with `fastmcp dev` command and MCP inspector tools.

### Module Entry Point

The `server.py` module can also be run directly:

| Entry | Path | Description |
|-------|------|-------------|
| `server.py __main__` | `src/falkordb_mcp/server.py:192-193` | Direct module execution | Calls `main()` when run as script |

## Dependencies Between Components

### Internal Dependencies

```
main.py
  └─> server.py (imports main function)
        ├─> config.py (imports config)
        └─> service.py (imports get_service)
              └─> config.py (imports config)

server_dev.py (standalone, no internal dependencies)
```

### Detailed Dependency Graph

#### server.py Dependencies

**Location**: `src/falkordb_mcp/server.py`

- **Line 16**: `from .config import config` - Uses global config for server information in resources
- **Line 17**: `from .service import get_service` - Uses service factory for all tool implementations
- **Line 14**: `from fastmcp import FastMCP` - External dependency on FastMCP framework

**Usage**:
- `get_service()` called in all MCP tool implementations (lines 48, 84, 118, 148)
- `config` accessed in MCP resources (lines 155, 156, 174, 175)

#### service.py Dependencies

**Location**: `src/falkordb_mcp/service.py`

- **Line 6**: `from falkordb import FalkorDB` - External dependency on FalkorDB client library
- **Line 8**: `from .config import config` - Uses global config for database connection parameters

**Usage**:
- `config` accessed in `_initialize()` method (lines 24-28)
- `FalkorDB` class instantiated (line 24)

#### config.py Dependencies

**Location**: `src/falkordb_mcp/config.py`

- **Line 7**: `from dotenv import load_dotenv` - External dependency for environment variable loading
- **Line 10**: `load_dotenv()` - Loads environment variables at module import time

**No internal dependencies** - This is the foundation layer.

### External Dependencies

From `pyproject.toml`:

| Dependency | Version | Purpose | Used In |
|------------|---------|---------|---------|
| `fastmcp` | >=0.3.0 | MCP protocol framework | server.py:14, server_dev.py:16 |
| `falkordb` | >=1.2.0 | FalkorDB Python client | service.py:6, server_dev.py:15 |
| `python-dotenv` | >=1.0.0 | Environment variable management | config.py:7, server_dev.py:14 |
| `claude-agent-sdk` | >=0.1.10 | Claude agent development (optional) | Not directly imported in main code |

### Dependency Flow Pattern

The codebase follows a clean layered architecture:

```
Layer 1: Configuration (config.py)
  ├─ Loads environment variables
  └─ No internal dependencies

Layer 2: Service (service.py)
  ├─ Depends on: config.py
  └─ Provides: FalkorDB operations abstraction

Layer 3: Server (server.py)
  ├─ Depends on: config.py, service.py
  └─ Provides: MCP protocol interface

Layer 4: Entry Points (main.py)
  ├─ Depends on: server.py
  └─ Provides: Application launcher
```

### Singleton Pattern Usage

The codebase uses the singleton pattern in two locations:

1. **Service Singleton**:
   - Implementation: `src/falkordb_mcp/service.py:125-133`
   - Module-level variable `_service` ensures single FalkorDB connection
   - Factory function `get_service()` provides thread-safe access

2. **Config Singleton**:
   - Implementation: `src/falkordb_mcp/config.py:34`
   - Module-level `config` instance initialized once at import time
   - Used across all modules requiring configuration

### Initialization Order

1. `config.py` loads environment variables and creates config instance
2. `service.py` imports config and defines service class/factory
3. `server.py` imports config and service, creates MCP server and registers tools
4. `main.py` imports server and calls main() to start server

This order ensures proper dependency initialization and prevents circular imports.

## Version Information

- **Package Version**: 1.0.0 (defined in `__init__.py:3` and `pyproject.toml:3`)
- **Python Requirement**: >= 3.11 (from `pyproject.toml:6`)

## Package Metadata

- **Package Name**: `falkordb-fastmcp`
- **Build System**: Hatchling
- **Package Location**: `src/falkordb_mcp/` (wheel target from `pyproject.toml:26`)
- **Description**: FastMCP-based Model Context Protocol server for FalkorDB graph database
