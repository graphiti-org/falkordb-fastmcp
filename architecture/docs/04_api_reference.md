# API Reference

## Overview

The FalkorDB FastMCP Server provides a Model Context Protocol (MCP) interface for interacting with FalkorDB graph databases. It exposes tools for executing Cypher queries, discovering graphs, and retrieving metadata through a standardized MCP API.

**Key Features:**
- Execute Cypher queries against FalkorDB graphs
- Discover and list available graphs
- Retrieve graph metadata and schema information
- Connection pooling and error handling
- Environment-based configuration
- Comprehensive logging and monitoring

**Architecture:**
- Built on FastMCP framework
- Service layer pattern for database operations
- Singleton service instance for connection management
- JSON-based request/response format

## Quick Start

```python
from src.falkordb_mcp.server import mcp

# The server automatically connects to FalkorDB on startup
# Configure connection via environment variables or .env file

# Run the MCP server
if __name__ == "__main__":
    mcp.run()
```

**Example Environment Setup:**

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_USERNAME=
FALKORDB_PASSWORD=
```

**Start Server:**

```bash
# Production mode
python main.py

# Development mode (standalone)
python server_dev.py
```

## Configuration

### FalkorDBConfig

Configuration class for FalkorDB connection settings. Automatically loads from environment variables.

**Source:** `src/falkordb_mcp/config.py` (lines 14-30)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `host` | `str` | `"localhost"` | FalkorDB server hostname or IP address |
| `port` | `int` | `6379` | FalkorDB server port number |
| `username` | `Optional[str]` | `None` | Username for authentication (optional) |
| `password` | `Optional[str]` | `None` | Password for authentication (optional) |

**Class Methods:**

#### `from_env() -> FalkorDBConfig`

Creates a configuration instance from environment variables.

```python
from src.falkordb_mcp.config import FalkorDBConfig

# Load configuration from environment
config = FalkorDBConfig.from_env()

print(f"Host: {config.host}")
print(f"Port: {config.port}")
```

**Environment Variable Mapping:**
- `FALKORDB_HOST` → `host`
- `FALKORDB_PORT` → `port`
- `FALKORDB_USERNAME` → `username`
- `FALKORDB_PASSWORD` → `password`

### Environment Variables

All configuration is managed through environment variables. Create a `.env` file in the project root:

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `FALKORDB_HOST` | string | No | `localhost` | FalkorDB server hostname |
| `FALKORDB_PORT` | integer | No | `6379` | FalkorDB server port |
| `FALKORDB_USERNAME` | string | No | `None` | Authentication username |
| `FALKORDB_PASSWORD` | string | No | `None` | Authentication password |
| `LOG_LEVEL` | string | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

**Example `.env` file:**

```bash
# FalkorDB Connection Configuration
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
FALKORDB_USERNAME=
FALKORDB_PASSWORD=

# Optional: For debugging and development
LOG_LEVEL=INFO
```

## Core Classes

### FalkorDBService

The main service class for interacting with FalkorDB. Manages database connections and provides methods for graph operations.

**Source:** `src/falkordb_mcp/service.py` (lines 13-122)

#### Constructor

```python
def __init__(self) -> None:
    """
    Initialize FalkorDB service.

    Automatically establishes connection to FalkorDB using configuration
    from FalkorDBConfig. Tests connection on initialization.

    Raises:
        Exception: If connection to FalkorDB fails
    """
```

**Example:**

```python
from src.falkordb_mcp.service import FalkorDBService

try:
    service = FalkorDBService()
    print("Connected to FalkorDB successfully")
except Exception as e:
    print(f"Connection failed: {e}")
```

#### Properties

##### `client -> FalkorDB`

Get the underlying FalkorDB client instance.

**Source:** Lines 39-44

```python
@property
def client(self) -> FalkorDB:
    """
    Get FalkorDB client instance.

    Returns:
        FalkorDB: The initialized client instance

    Raises:
        RuntimeError: If client not initialized
    """
```

**Example:**

```python
service = FalkorDBService()
client = service.client

# Use client directly for advanced operations
response = client.connection.ping()
```

#### Methods

##### `execute_query(graph_name: str, query: str, params: Optional[Dict[str, Any]] = None) -> Any`

Execute a Cypher query against a FalkorDB graph.

**Source:** Lines 46-72

**Parameters:**
- `graph_name` (str): Name of the graph to query
- `query` (str): Cypher query to execute
- `params` (Optional[Dict[str, Any]]): Query parameters for parameterized queries

**Returns:**
- `Any`: Query results from FalkorDB

**Raises:**
- `Exception`: If query execution fails

**Example:**

```python
from src.falkordb_mcp.service import get_service

service = get_service()

# Simple query
result = service.execute_query(
    graph_name="social_network",
    query="MATCH (n:Person) RETURN n LIMIT 10"
)

# Parameterized query
result = service.execute_query(
    graph_name="social_network",
    query="MATCH (n:Person {name: $name}) RETURN n",
    params={"name": "Alice"}
)

# Complex query with relationships
result = service.execute_query(
    graph_name="social_network",
    query="""
        MATCH (p:Person)-[r:KNOWS]->(friend:Person)
        WHERE p.name = $name
        RETURN p, r, friend
    """,
    params={"name": "Bob"}
)
```

##### `list_graphs() -> List[str]`

List all available graphs in FalkorDB.

**Source:** Lines 74-88

**Returns:**
- `List[str]`: List of graph names

**Raises:**
- `Exception`: If listing fails

**Example:**

```python
service = get_service()

graphs = service.list_graphs()
print(f"Available graphs: {graphs}")

# Output: Available graphs: ['social_network', 'knowledge_graph', 'movies']
```

##### `get_graph_metadata(graph_name: str) -> Dict[str, Any]`

Get metadata about a specific graph, including labels and statistics.

**Source:** Lines 90-114

**Parameters:**
- `graph_name` (str): Name of the graph

**Returns:**
- `Dict[str, Any]`: Dictionary containing:
  - `name`: Graph name
  - `labels`: Result of `db.labels()` procedure call

**Raises:**
- `Exception`: If metadata retrieval fails

**Example:**

```python
service = get_service()

metadata = service.get_graph_metadata("social_network")
print(f"Graph: {metadata['name']}")
print(f"Labels: {metadata['labels']}")

# Output:
# Graph: social_network
# Labels: <QueryResult with node labels>
```

##### `close() -> None`

Close connection to FalkorDB.

**Source:** Lines 116-121

**Example:**

```python
service = get_service()

# Use service...

# Clean up
service.close()
```

#### Global Service Instance

##### `get_service() -> FalkorDBService`

Get or create the global FalkorDB service instance (singleton pattern).

**Source:** Lines 128-133

**Returns:**
- `FalkorDBService`: The global service instance

**Example:**

```python
from src.falkordb_mcp.service import get_service

# Get singleton instance
service = get_service()

# Multiple calls return same instance
service2 = get_service()
assert service is service2  # True
```

## MCP Tools

The server exposes three MCP tools for graph operations. All tools return JSON strings with standardized response formats.

### execute_query

Execute a Cypher query against a FalkorDB graph.

**Source:** `src/falkordb_mcp/server.py` (lines 30-72)

**MCP Tool Signature:**

```python
@mcp.tool()
def execute_query(
    graph_name: str,
    query: str,
    params: Optional[Dict[str, Any]] = None
) -> str
```

**Parameters:**
- `graph_name` (str): Name of the graph to query
- `query` (str): Cypher query to execute (e.g., "MATCH (n:Person) RETURN n LIMIT 10")
- `params` (Optional[Dict[str, Any]]): Query parameters as key-value pairs

**Returns:**

JSON string with the following structure:

**Success Response:**
```json
{
  "success": true,
  "data": <query_results>,
  "metadata": {
    "graphName": "social_network",
    "query": "MATCH (n:Person) RETURN n LIMIT 10",
    "timestamp": "2025-11-29T20:53:12.123456"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "graphName": "social_network",
  "query": "INVALID QUERY"
}
```

**Examples:**

```python
# Simple node query
result = execute_query(
    graph_name="movies",
    query="MATCH (m:Movie) RETURN m.title, m.year LIMIT 5"
)

# Parameterized query
result = execute_query(
    graph_name="movies",
    query="MATCH (m:Movie {year: $year}) RETURN m",
    params={"year": 1999}
)

# Relationship traversal
result = execute_query(
    graph_name="movies",
    query="""
        MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)
        WHERE a.name = $actor_name
        RETURN m.title AS movie, m.year AS year
        ORDER BY m.year DESC
    """,
    params={"actor_name": "Keanu Reeves"}
)

# Aggregation query
result = execute_query(
    graph_name="social_network",
    query="""
        MATCH (p:Person)-[:KNOWS]->(friend)
        RETURN p.name, COUNT(friend) AS friend_count
        ORDER BY friend_count DESC
        LIMIT 10
    """
)
```

**Error Handling:**

```python
import json

result = execute_query(
    graph_name="test_graph",
    query="INVALID CYPHER QUERY"
)

response = json.loads(result)
if not response["success"]:
    print(f"Query failed: {response['error']}")
```

### list_graphs

List all available graphs in the FalkorDB instance.

**Source:** `src/falkordb_mcp/server.py` (lines 75-103)

**MCP Tool Signature:**

```python
@mcp.tool()
def list_graphs() -> str
```

**Parameters:**
None

**Returns:**

JSON string with the following structure:

**Success Response:**
```json
{
  "success": true,
  "graphs": ["social_network", "movies", "knowledge_graph"],
  "count": 3,
  "timestamp": "2025-11-29T20:53:12.123456"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message"
}
```

**Example:**

```python
import json

# List all graphs
result = list_graphs()
response = json.loads(result)

if response["success"]:
    print(f"Found {response['count']} graphs:")
    for graph in response["graphs"]:
        print(f"  - {graph}")
else:
    print(f"Error: {response['error']}")
```

**Use Cases:**
- Graph discovery and exploration
- Validating graph names before querying
- Building dynamic graph selection UIs
- Monitoring graph availability

### get_graph_metadata

Get metadata and labels for a specific FalkorDB graph.

**Source:** `src/falkordb_mcp/server.py` (lines 106-137)

**MCP Tool Signature:**

```python
@mcp.tool()
def get_graph_metadata(graph_name: str) -> str
```

**Parameters:**
- `graph_name` (str): Name of the graph

**Returns:**

JSON string with the following structure:

**Success Response:**
```json
{
  "success": true,
  "metadata": {
    "name": "social_network",
    "labels": <label_query_result>
  },
  "timestamp": "2025-11-29T20:53:12.123456"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error message",
  "graphName": "social_network"
}
```

**Example:**

```python
import json

# Get metadata for a graph
result = get_graph_metadata(graph_name="movies")
response = json.loads(result)

if response["success"]:
    metadata = response["metadata"]
    print(f"Graph: {metadata['name']}")
    print(f"Labels: {metadata['labels']}")
else:
    print(f"Error: {response['error']}")
```

**Use Cases:**
- Schema discovery
- Understanding graph structure
- Validating graph content
- Building query builders
- Documentation generation

## MCP Resources

Resources provide read-only access to server state and configuration.

### falkordb://graphs

Resource providing list of all available graphs in FalkorDB.

**Source:** `src/falkordb_mcp/server.py` (lines 140-160)

**MCP Resource Signature:**

```python
@mcp.resource("falkordb://graphs")
def get_available_graphs() -> str
```

**Returns:**

JSON string with the following structure:

```json
{
  "graphs": ["social_network", "movies", "knowledge_graph"],
  "count": 3,
  "host": "localhost",
  "port": 6379,
  "timestamp": "2025-11-29T20:53:12.123456"
}
```

**Example:**

```python
import json

# Access resource (exact usage depends on MCP client)
# Resource URI: falkordb://graphs

# Expected response:
response = {
    "graphs": ["social_network", "movies"],
    "count": 2,
    "host": "localhost",
    "port": 6379,
    "timestamp": "2025-11-29T20:53:12.123456"
}
```

**Use Cases:**
- Dynamic graph selection
- Health monitoring
- Configuration validation
- Dashboard displays

### falkordb://status

Resource providing FalkorDB connection status and server information.

**Source:** `src/falkordb_mcp/server.py` (lines 163-180)

**MCP Resource Signature:**

```python
@mcp.resource("falkordb://status")
def get_server_status() -> str
```

**Returns:**

JSON string with the following structure:

```json
{
  "status": "connected",
  "host": "localhost",
  "port": 6379,
  "version": "1.0.0",
  "timestamp": "2025-11-29T20:53:12.123456"
}
```

**Example:**

```python
import json

# Access resource (exact usage depends on MCP client)
# Resource URI: falkordb://status

# Expected response:
response = {
    "status": "connected",
    "host": "localhost",
    "port": 6379,
    "version": "1.0.0",
    "timestamp": "2025-11-29T20:53:12.123456"
}
```

**Use Cases:**
- Health checks
- Monitoring dashboards
- Connection validation
- Debug information

## Usage Patterns

### Pattern 1: Basic Query Execution

Execute simple queries against a FalkorDB graph.

```python
from src.falkordb_mcp.service import get_service
import json

# Get service instance
service = get_service()

# Execute a simple query
result = service.execute_query(
    graph_name="movies",
    query="MATCH (m:Movie) RETURN m.title AS title, m.year AS year LIMIT 10"
)

# Process results
for record in result.result_set:
    print(f"{record[0]} ({record[1]})")
```

**Via MCP Tool:**

```python
from src.falkordb_mcp.server import execute_query
import json

# Call MCP tool
result_json = execute_query(
    graph_name="movies",
    query="MATCH (m:Movie) RETURN m.title, m.year LIMIT 10"
)

# Parse response
response = json.loads(result_json)
if response["success"]:
    print(f"Query executed at: {response['metadata']['timestamp']}")
    print(f"Results: {response['data']}")
```

### Pattern 2: Graph Discovery

Discover and explore available graphs and their schemas.

```python
from src.falkordb_mcp.service import get_service
import json

service = get_service()

# Step 1: List all graphs
graphs = service.list_graphs()
print(f"Available graphs: {graphs}")

# Step 2: Get metadata for each graph
for graph_name in graphs:
    metadata = service.get_graph_metadata(graph_name)
    print(f"\nGraph: {metadata['name']}")
    print(f"Labels: {metadata['labels']}")

    # Step 3: Query graph schema
    schema_result = service.execute_query(
        graph_name=graph_name,
        query="CALL db.labels()"
    )
    print(f"Schema: {schema_result}")
```

**Via MCP Tools:**

```python
from src.falkordb_mcp.server import list_graphs, get_graph_metadata
import json

# List graphs
graphs_json = list_graphs()
graphs_data = json.loads(graphs_json)

if graphs_data["success"]:
    for graph_name in graphs_data["graphs"]:
        # Get metadata for each
        metadata_json = get_graph_metadata(graph_name)
        metadata = json.loads(metadata_json)

        if metadata["success"]:
            print(f"Graph: {graph_name}")
            print(f"Details: {metadata['metadata']}")
```

### Pattern 3: Parameterized Queries

Execute safe, parameterized queries to prevent injection attacks.

```python
from src.falkordb_mcp.service import get_service

service = get_service()

# User input (potentially unsafe)
user_name = "Alice"
min_age = 25

# Safe parameterized query
result = service.execute_query(
    graph_name="social_network",
    query="""
        MATCH (p:Person)
        WHERE p.name = $name AND p.age >= $min_age
        RETURN p.name, p.age, p.email
    """,
    params={
        "name": user_name,
        "min_age": min_age
    }
)

# Process results
for record in result.result_set:
    print(f"Name: {record[0]}, Age: {record[1]}, Email: {record[2]}")
```

### Pattern 4: Error Handling

Robust error handling for production applications.

```python
from src.falkordb_mcp.service import get_service
import logging

logger = logging.getLogger(__name__)
service = get_service()

def safe_query(graph_name: str, query: str, params=None):
    """Execute query with comprehensive error handling."""
    try:
        result = service.execute_query(graph_name, query, params)
        return {
            "success": True,
            "data": result,
            "error": None
        }
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        return {
            "success": False,
            "data": None,
            "error": f"Database connection failed: {e}"
        }
    except ValueError as e:
        logger.error(f"Invalid query: {e}")
        return {
            "success": False,
            "data": None,
            "error": f"Invalid query parameters: {e}"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "success": False,
            "data": None,
            "error": f"Query execution failed: {e}"
        }

# Use safe query wrapper
result = safe_query(
    graph_name="movies",
    query="MATCH (m:Movie) RETURN m LIMIT 10"
)

if result["success"]:
    print(f"Success: {result['data']}")
else:
    print(f"Error: {result['error']}")
```

**MCP Tool Error Handling:**

```python
from src.falkordb_mcp.server import execute_query
import json

result_json = execute_query(
    graph_name="test_graph",
    query="MATCH (n) RETURN n"
)

response = json.loads(result_json)

if response["success"]:
    # Process successful response
    data = response["data"]
    metadata = response["metadata"]
    print(f"Query succeeded: {metadata['query']}")
else:
    # Handle error
    error = response["error"]
    graph = response["graphName"]
    print(f"Query failed on graph '{graph}': {error}")
```

### Pattern 5: Connection Management

Manage database connections effectively.

```python
from src.falkordb_mcp.service import FalkorDBService

class GraphQueryManager:
    """Context manager for FalkorDB queries."""

    def __init__(self):
        self.service = None

    def __enter__(self):
        self.service = FalkorDBService()
        return self.service

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.service:
            self.service.close()
        return False

# Use context manager
with GraphQueryManager() as service:
    graphs = service.list_graphs()
    print(f"Graphs: {graphs}")

    for graph in graphs:
        result = service.execute_query(
            graph_name=graph,
            query="MATCH (n) RETURN COUNT(n) AS node_count"
        )
        print(f"{graph}: {result}")
# Service automatically closed
```

## Best Practices

### 1. Use Parameterized Queries

Always use parameterized queries to prevent Cypher injection:

```python
# BAD - Vulnerable to injection
query = f"MATCH (n:Person {{name: '{user_input}'}}) RETURN n"

# GOOD - Safe parameterized query
query = "MATCH (n:Person {name: $name}) RETURN n"
params = {"name": user_input}
```

### 2. Handle Errors Gracefully

Always check for errors in MCP tool responses:

```python
import json

result = execute_query(graph_name="test", query="MATCH (n) RETURN n")
response = json.loads(result)

if not response["success"]:
    # Handle error appropriately
    logger.error(f"Query failed: {response['error']}")
    return None
```

### 3. Use Singleton Service Instance

Use `get_service()` instead of creating new instances:

```python
# GOOD - Reuses connection
from src.falkordb_mcp.service import get_service

service = get_service()
service.execute_query(...)

# BAD - Creates new connection each time
from src.falkordb_mcp.service import FalkorDBService

service = FalkorDBService()  # Avoid this
```

### 4. Limit Query Results

Always use `LIMIT` clauses for exploratory queries:

```python
# Prevent returning too much data
query = "MATCH (n:Person) RETURN n LIMIT 100"
```

### 5. Validate Graph Names

Check if graph exists before querying:

```python
service = get_service()
graphs = service.list_graphs()

if "my_graph" in graphs:
    result = service.execute_query("my_graph", "MATCH (n) RETURN n LIMIT 10")
else:
    print("Graph 'my_graph' not found")
```

### 6. Use Environment Variables

Never hardcode connection details:

```python
# GOOD - Use environment variables
from src.falkordb_mcp.config import config

host = config.host
port = config.port

# BAD - Hardcoded values
host = "192.168.1.100"  # Avoid this
```

### 7. Log Appropriately

Use structured logging for debugging:

```python
import logging

logger = logging.getLogger(__name__)

logger.info(f"Executing query on graph: {graph_name}")
logger.debug(f"Query: {query}")
logger.debug(f"Params: {params}")
```

### 8. Close Connections

Clean up resources when done (especially in long-running applications):

```python
service = get_service()
try:
    # Use service
    result = service.execute_query(...)
finally:
    service.close()
```

## Error Handling

### Common Error Types

#### Connection Errors

Raised when unable to connect to FalkorDB:

```python
from src.falkordb_mcp.service import FalkorDBService

try:
    service = FalkorDBService()
except Exception as e:
    if "connection" in str(e).lower():
        print("Failed to connect to FalkorDB")
        print("Check FALKORDB_HOST and FALKORDB_PORT")
```

#### Query Errors

Raised when Cypher query is invalid:

```python
try:
    result = service.execute_query(
        graph_name="test",
        query="INVALID CYPHER"
    )
except Exception as e:
    print(f"Query syntax error: {e}")
```

#### Graph Not Found

Raised when querying non-existent graph:

```python
graphs = service.list_graphs()

if graph_name not in graphs:
    raise ValueError(f"Graph '{graph_name}' does not exist")
```

### Error Response Format

All MCP tools return consistent error responses:

```json
{
  "success": false,
  "error": "Detailed error message",
  "graphName": "context_graph_name",
  "query": "context_query"
}
```

### Handling Errors in MCP Tools

```python
import json
import logging

logger = logging.getLogger(__name__)

def execute_query_with_retry(graph_name, query, params=None, max_retries=3):
    """Execute query with retry logic."""
    for attempt in range(max_retries):
        result_json = execute_query(graph_name, query, params)
        response = json.loads(result_json)

        if response["success"]:
            return response

        logger.warning(
            f"Query failed (attempt {attempt + 1}/{max_retries}): "
            f"{response['error']}"
        )

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff

    raise Exception(f"Query failed after {max_retries} attempts")
```

## Source File Reference

| Component | File Path | Lines | Description |
|-----------|-----------|-------|-------------|
| **Main Entry Point** | `main.py` | 1-8 | Production server entry point |
| **Dev Server** | `server_dev.py` | 1-289 | Standalone development server |
| **Package Init** | `src/falkordb_mcp/__init__.py` | 1-4 | Package version and metadata |
| **Configuration** | `src/falkordb_mcp/config.py` | 1-35 | FalkorDBConfig class and environment loading |
| `FalkorDBConfig` | `src/falkordb_mcp/config.py` | 14-30 | Configuration dataclass |
| `from_env()` | `src/falkordb_mcp/config.py` | 22-30 | Environment variable loader |
| **Service Layer** | `src/falkordb_mcp/service.py` | 1-134 | FalkorDB service implementation |
| `FalkorDBService` | `src/falkordb_mcp/service.py` | 13-122 | Main service class |
| `__init__()` | `src/falkordb_mcp/service.py` | 16-19 | Service initialization |
| `_initialize()` | `src/falkordb_mcp/service.py` | 21-37 | Connection initialization |
| `client` property | `src/falkordb_mcp/service.py` | 39-44 | Client getter |
| `execute_query()` | `src/falkordb_mcp/service.py` | 46-72 | Query execution |
| `list_graphs()` | `src/falkordb_mcp/service.py` | 74-88 | Graph listing |
| `get_graph_metadata()` | `src/falkordb_mcp/service.py` | 90-114 | Metadata retrieval |
| `close()` | `src/falkordb_mcp/service.py` | 116-121 | Connection cleanup |
| `get_service()` | `src/falkordb_mcp/service.py` | 128-133 | Singleton getter |
| **MCP Server** | `src/falkordb_mcp/server.py` | 1-194 | FastMCP server and tools |
| MCP `execute_query` | `src/falkordb_mcp/server.py` | 30-72 | Query execution tool |
| MCP `list_graphs` | `src/falkordb_mcp/server.py` | 75-103 | Graph listing tool |
| MCP `get_graph_metadata` | `src/falkordb_mcp/server.py` | 106-137 | Metadata tool |
| Resource `falkordb://graphs` | `src/falkordb_mcp/server.py` | 140-160 | Graphs resource |
| Resource `falkordb://status` | `src/falkordb_mcp/server.py` | 163-180 | Status resource |
| `main()` | `src/falkordb_mcp/server.py` | 183-189 | Server main entry |
| **Configuration Example** | `.env.example` | 1-9 | Environment variable template |
| **Project Config** | `pyproject.toml` | 1-39 | Python project configuration |

## Dependencies

The project requires the following Python packages:

| Package | Version | Purpose |
|---------|---------|---------|
| `fastmcp` | >=0.3.0 | FastMCP framework for MCP server |
| `falkordb` | >=1.2.0 | FalkorDB Python client |
| `python-dotenv` | >=1.0.0 | Environment variable loading |
| `claude-agent-sdk` | >=0.1.10 | Claude SDK integration |

**Development Dependencies:**
- `pytest` (>=7.4.0) - Testing framework
- `pytest-asyncio` (>=0.21.0) - Async test support
- `ruff` (>=0.1.0) - Linting and formatting

**Python Version:** Requires Python >=3.11

## Additional Resources

- **FalkorDB Documentation:** https://docs.falkordb.com/
- **FastMCP Documentation:** https://github.com/jlowin/fastmcp
- **Cypher Query Language:** https://neo4j.com/docs/cypher-manual/
- **Model Context Protocol:** https://modelcontextprotocol.io/

---

*Documentation generated for FalkorDB FastMCP Server v1.0.0*
