# Architecture Diagrams

## Overview

The FalkorDB FastMCP server is a Python-based Model Context Protocol (MCP) server that provides a clean, layered architecture for interacting with FalkorDB graph databases. The system follows a three-tier architecture pattern with clear separation of concerns:

1. **Server Layer** - FastMCP server handling MCP protocol (tools and resources)
2. **Service Layer** - Business logic and FalkorDB operations
3. **Configuration Layer** - Environment-based configuration management

The architecture emphasizes:
- Type safety with Python type hints throughout
- Singleton pattern for service management
- Clean separation between protocol handling and database operations
- Environment-based configuration
- Comprehensive logging and error handling

## System Architecture

The system follows a layered architecture with clear boundaries between protocol handling, business logic, and data access. The FastMCP framework provides the MCP protocol implementation, while custom layers handle FalkorDB-specific operations.

Key architectural components:
- **Entry Points**: `main.py` (production) and `server_dev.py` (development/standalone)
- **MCP Server**: Decorators-based tools and resources registration
- **Service Layer**: Singleton service managing FalkorDB connections
- **Configuration**: Environment-driven configuration with dotenv support

```mermaid
flowchart TB
    subgraph "Entry Points"
        MAIN[main.py<br/>Production Entry Point]
        DEV[server_dev.py<br/>Development Entry Point]
    end

    subgraph "MCP Protocol Layer"
        MCP[FastMCP Server<br/>src/falkordb_mcp/server.py]
        TOOLS[MCP Tools<br/>- execute_query<br/>- list_graphs<br/>- get_graph_metadata]
        RESOURCES[MCP Resources<br/>- falkordb://graphs<br/>- falkordb://status]
    end

    subgraph "Service Layer"
        SERVICE[FalkorDBService<br/>src/falkordb_mcp/service.py]
        SINGLETON[get_service<br/>Singleton Factory]
    end

    subgraph "Configuration Layer"
        CONFIG[FalkorDBConfig<br/>src/falkordb_mcp/config.py]
        ENV[Environment Variables<br/>.env]
    end

    subgraph "External Systems"
        FALKORDB[(FalkorDB<br/>Graph Database)]
    end

    MAIN --> MCP
    DEV -.-> MCP
    MCP --> TOOLS
    MCP --> RESOURCES
    TOOLS --> SINGLETON
    RESOURCES --> SINGLETON
    SINGLETON --> SERVICE
    SERVICE --> CONFIG
    CONFIG --> ENV
    SERVICE --> FALKORDB

    style MAIN fill:#e1f5ff
    style DEV fill:#fff4e1
    style MCP fill:#e8f5e9
    style SERVICE fill:#f3e5f5
    style CONFIG fill:#fff9c4
    style FALKORDB fill:#ffebee
```

## Component Relationships

The component relationships show how different modules interact with each other. The FastMCP framework provides the foundation, while custom components build on top of it to provide FalkorDB-specific functionality.

**Key Relationships:**
- **main.py** imports and delegates to **server.py**'s main() function
- **server.py** uses FastMCP decorators (@mcp.tool, @mcp.resource) for registration
- **server.py** imports get_service() from **service.py** and config from **config.py**
- **service.py** imports config from **config.py** for connection settings
- **service.py** wraps the FalkorDB client library
- **server_dev.py** is a standalone version with no relative imports (for development/testing)

```mermaid
flowchart LR
    subgraph "Production Entry"
        M[main.py]
    end

    subgraph "Development Entry"
        D[server_dev.py<br/>Standalone]
    end

    subgraph "Core MCP Server"
        S[server.py<br/>MCP Implementation]
    end

    subgraph "Service Layer"
        SVC[service.py<br/>FalkorDBService]
        GS[get_service<br/>Factory Function]
    end

    subgraph "Configuration"
        CFG[config.py<br/>FalkorDBConfig]
    end

    subgraph "External Libraries"
        FASTMCP[fastmcp<br/>FastMCP Framework]
        FALKORDB_LIB[falkordb<br/>FalkorDB Client]
        DOTENV[python-dotenv<br/>Environment Loader]
    end

    M -->|imports main| S
    D -.->|standalone version| S
    S -->|imports| GS
    S -->|imports| CFG
    GS -->|creates/returns| SVC
    SVC -->|imports| CFG
    S -->|uses| FASTMCP
    SVC -->|uses| FALKORDB_LIB
    CFG -->|uses| DOTENV

    style M fill:#e1f5ff
    style D fill:#fff4e1
    style S fill:#e8f5e9
    style SVC fill:#f3e5f5
    style CFG fill:#fff9c4
    style FASTMCP fill:#fce4ec
    style FALKORDB_LIB fill:#fce4ec
    style DOTENV fill:#fce4ec
```

## Class Hierarchies

The codebase uses a minimal class hierarchy focused on configuration and service management. Both classes are dataclasses or plain classes with clear responsibilities.

**Class Details:**

1. **FalkorDBConfig** (config.py and server_dev.py):
   - Dataclass for configuration management
   - Contains connection parameters (host, port, username, password)
   - Class method `from_env()` for environment-based initialization
   - Used as singleton instance at module level

2. **FalkorDBService** (service.py and server_dev.py):
   - Service class managing FalkorDB connections
   - Singleton pattern via module-level factory function
   - Three public methods for database operations
   - Property-based client access with validation

```mermaid
classDiagram
    class FalkorDBConfig {
        +str host
        +int port
        +Optional~str~ username
        +Optional~str~ password
        +from_env() FalkorDBConfig$
    }

    class FalkorDBService {
        -Optional~FalkorDB~ _client
        +__init__()
        -_initialize() None
        +client() FalkorDB
        +execute_query(graph_name: str, query: str, params: Dict) Any
        +list_graphs() List~str~
        +get_graph_metadata(graph_name: str) Dict
        +close() None
    }

    class FalkorDB {
        <<external library>>
        +select_graph(name: str)
        +list_graphs()
        +connection
    }

    FalkorDBService --> FalkorDBConfig : uses
    FalkorDBService --> FalkorDB : wraps

    note for FalkorDBConfig "Singleton instance created\nat module level via\nconfig = FalkorDBConfig.from_env()"

    note for FalkorDBService "Singleton pattern via\nget_service() factory\nfunction at module level"
```

## Module Dependencies

The module dependency graph shows the import relationships between modules. The architecture maintains a clean dependency flow from entry points through the server layer to services and configuration.

**Dependency Notes:**
- **main.py**: Minimal entry point, only imports from server.py
- **server.py**: Core module importing from service.py and config.py
- **service.py**: Depends on config.py for configuration
- **config.py**: Leaf module with only external dependencies
- **server_dev.py**: Standalone version with all code inline (no internal imports)

```mermaid
flowchart TD
    subgraph "Package: src/falkordb_mcp"
        INIT[__init__.py<br/>version: 1.0.0]
        SERVER[server.py<br/>MCP Tools & Resources]
        SERVICE[service.py<br/>FalkorDB Operations]
        CONFIG[config.py<br/>Configuration]
    end

    subgraph "Entry Points"
        MAIN[main.py]
        DEV[server_dev.py]
    end

    subgraph "External Dependencies"
        EXT1[fastmcp]
        EXT2[falkordb]
        EXT3[python-dotenv]
        EXT4[logging]
        EXT5[json]
        EXT6[datetime]
    end

    MAIN -->|from src.falkordb_mcp.server<br/>import main| SERVER
    DEV -.->|standalone<br/>no imports| INIT

    SERVER -->|from .service<br/>import get_service| SERVICE
    SERVER -->|from .config<br/>import config| CONFIG
    SERVER -->|import| EXT1
    SERVER -->|import| EXT4
    SERVER -->|import| EXT5
    SERVER -->|import| EXT6

    SERVICE -->|from .config<br/>import config| CONFIG
    SERVICE -->|import| EXT2
    SERVICE -->|import| EXT4

    CONFIG -->|import| EXT3

    style MAIN fill:#e1f5ff
    style DEV fill:#fff4e1
    style SERVER fill:#e8f5e9
    style SERVICE fill:#f3e5f5
    style CONFIG fill:#fff9c4
    style EXT1 fill:#f5f5f5
    style EXT2 fill:#f5f5f5
    style EXT3 fill:#f5f5f5
    style EXT4 fill:#f5f5f5
    style EXT5 fill:#f5f5f5
    style EXT6 fill:#f5f5f5
```

## Data Flow

This sequence diagram illustrates the complete flow of a typical MCP tool invocation, from the MCP client through the server layers to the FalkorDB database and back.

**Flow Description:**

1. **Client Request**: MCP client (e.g., Claude) calls an MCP tool
2. **Server Reception**: FastMCP framework routes to appropriate tool function
3. **Service Retrieval**: Tool function gets singleton service instance
4. **Database Operation**: Service executes query against FalkorDB
5. **Response Formatting**: Results wrapped in JSON response
6. **Client Response**: Formatted response returned to MCP client

**Example Flow**: `execute_query` tool invocation

```mermaid
sequenceDiagram
    participant Client as MCP Client<br/>(Claude)
    participant FastMCP as FastMCP<br/>Framework
    participant Server as server.py<br/>@mcp.tool()
    participant Factory as get_service()<br/>Factory
    participant Service as FalkorDBService<br/>Instance
    participant Config as FalkorDBConfig<br/>config
    participant DB as FalkorDB<br/>Database

    Client->>FastMCP: Call execute_query tool
    activate FastMCP
    FastMCP->>Server: execute_query(graph_name, query, params)
    activate Server

    Server->>Factory: get_service()
    activate Factory

    alt First call
        Factory->>Config: Read connection settings
        Config-->>Factory: host, port, credentials
        Factory->>Service: __init__()
        activate Service
        Service->>Config: Access config
        Config-->>Service: Connection params
        Service->>DB: Connect and ping()
        DB-->>Service: Connection OK
        deactivate Service
    end

    Factory-->>Server: FalkorDBService instance
    deactivate Factory

    Server->>Service: execute_query(graph_name, query, params)
    activate Service
    Service->>DB: select_graph(graph_name)
    DB-->>Service: Graph object
    Service->>DB: graph.query(query, params)
    DB-->>Service: Query results
    Service-->>Server: Raw results
    deactivate Service

    Server->>Server: Format JSON response<br/>{success, data, metadata}
    Server-->>FastMCP: JSON string
    deactivate Server

    FastMCP-->>Client: Tool response
    deactivate FastMCP
```

## Resource Access Flow

This diagram shows how MCP resources are accessed, which provide read-only information about the FalkorDB server state.

**Resource Types:**
- **falkordb://graphs**: List of all available graphs
- **falkordb://status**: Server connection status

```mermaid
sequenceDiagram
    participant Client as MCP Client<br/>(Claude)
    participant FastMCP as FastMCP<br/>Framework
    participant Resource as server.py<br/>@mcp.resource()
    participant Factory as get_service()
    participant Service as FalkorDBService
    participant DB as FalkorDB<br/>Database

    Client->>FastMCP: Access falkordb://graphs
    activate FastMCP
    FastMCP->>Resource: get_available_graphs()
    activate Resource

    Resource->>Factory: get_service()
    Factory-->>Resource: Service instance

    Resource->>Service: list_graphs()
    activate Service
    Service->>DB: client.list_graphs()
    DB-->>Service: List of graph names
    Service-->>Resource: Graph list
    deactivate Service

    Resource->>Resource: Format JSON<br/>{graphs, count, host, port}
    Resource-->>FastMCP: JSON string
    deactivate Resource

    FastMCP-->>Client: Resource content
    deactivate FastMCP
```

## Error Handling Flow

The system implements comprehensive error handling at each layer with proper logging and error propagation.

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant Server as server.py<br/>Tool Function
    participant Service as FalkorDBService
    participant DB as FalkorDB
    participant Logger as Logging System

    Client->>Server: execute_query(...)
    activate Server

    Server->>Service: execute_query(...)
    activate Service

    Service->>DB: graph.query(...)
    activate DB

    alt Query Error
        DB-->>Service: Exception
        deactivate DB
        Service->>Logger: Log error with graph name
        Service->>Service: Sanitize graph name
        Service-->>Server: Raise exception
        deactivate Service

        Server->>Server: Catch exception
        Server->>Server: Format error response<br/>{success: false, error, graphName}
        Server-->>Client: Error JSON
    else Query Success
        DB-->>Service: Results
        deactivate DB
        Service-->>Server: Results
        deactivate Service

        Server->>Server: Format success response<br/>{success: true, data, metadata}
        Server-->>Client: Success JSON
    end
    deactivate Server
```

## Initialization Sequence

This diagram shows the application startup sequence, including configuration loading, service initialization, and server registration.

```mermaid
sequenceDiagram
    participant OS as Operating System
    participant Main as main.py
    participant Server as server.py
    participant Config as config.py
    participant Service as service.py
    participant FastMCP as FastMCP
    participant DB as FalkorDB

    OS->>Main: python main.py
    activate Main
    Main->>Server: import server module
    activate Server

    Server->>Config: import config
    activate Config
    Config->>Config: load_dotenv()
    Config->>Config: config = FalkorDBConfig.from_env()
    Config-->>Server: config object
    deactivate Config

    Server->>Service: import get_service
    activate Service
    Service->>Config: import config
    Service-->>Server: get_service function
    deactivate Service

    Server->>FastMCP: mcp = FastMCP("FalkorDB")
    FastMCP-->>Server: mcp instance

    Server->>Server: Register tools via @mcp.tool()
    Server->>Server: Register resources via @mcp.resource()
    Server-->>Main: server module loaded
    deactivate Server

    Main->>Server: main()
    activate Server
    Server->>FastMCP: mcp.run()
    activate FastMCP

    Note over FastMCP: Wait for MCP client<br/>connection on stdio

    FastMCP-->>Server: Running...
    deactivate FastMCP
    deactivate Server
    deactivate Main

    Note over Main,DB: Service initialized on<br/>first tool/resource call
```

## Configuration Loading

This diagram details the environment-based configuration loading process.

```mermaid
flowchart TD
    START([Application Start])
    LOAD_MODULE[Import config.py]
    LOAD_DOTENV[load_dotenv<br/>Read .env file]
    CHECK_ENV{Environment<br/>Variables Set?}
    GET_HOST[Get FALKORDB_HOST<br/>default: localhost]
    GET_PORT[Get FALKORDB_PORT<br/>default: 6379]
    GET_USER[Get FALKORDB_USERNAME<br/>optional]
    GET_PASS[Get FALKORDB_PASSWORD<br/>optional]
    CREATE_CONFIG[Create FalkorDBConfig<br/>dataclass instance]
    GLOBAL[Store as module-level<br/>config variable]
    READY([Config Ready for Use])

    START --> LOAD_MODULE
    LOAD_MODULE --> LOAD_DOTENV
    LOAD_DOTENV --> CHECK_ENV
    CHECK_ENV -->|Yes| GET_HOST
    CHECK_ENV -->|No| GET_HOST
    GET_HOST --> GET_PORT
    GET_PORT --> GET_USER
    GET_USER --> GET_PASS
    GET_PASS --> CREATE_CONFIG
    CREATE_CONFIG --> GLOBAL
    GLOBAL --> READY

    style START fill:#e1f5ff
    style LOAD_DOTENV fill:#fff9c4
    style CHECK_ENV fill:#fff4e1
    style CREATE_CONFIG fill:#e8f5e9
    style READY fill:#e1f5ff
```

## Service Lifecycle

The FalkorDBService follows a singleton pattern with lazy initialization and connection pooling.

```mermaid
stateDiagram-v2
    [*] --> Uninitialized: Import service.py

    Uninitialized --> Initializing: First get_service() call

    Initializing --> ReadingConfig: Read config module
    ReadingConfig --> CreatingClient: Create FalkorDB client
    CreatingClient --> TestingConnection: Execute ping()

    TestingConnection --> Connected: Ping successful
    TestingConnection --> Error: Connection failed

    Connected --> Processing: Tool/Resource call
    Processing --> Connected: Query complete

    Error --> [*]: Raise exception
    Connected --> Closed: close() called
    Closed --> [*]

    note right of Uninitialized
        Global _service = None
    end note

    note right of Connected
        Singleton instance cached
        in _service variable
    end note

    note right of Processing
        - execute_query()
        - list_graphs()
        - get_graph_metadata()
    end note
```

## Tool Registration Pattern

FastMCP uses Python decorators for tool and resource registration, providing a clean, declarative API.

```mermaid
flowchart LR
    subgraph "Decorator Pattern"
        DEF[Define Function<br/>execute_query]
        DEC["@mcp.tool<br/>Decorator"]
        REG[Register with FastMCP<br/>Framework]
    end

    subgraph "Runtime"
        CLIENT[MCP Client Call]
        DISPATCH[FastMCP Dispatcher]
        EXEC[Execute Function]
    end

    subgraph "Function Components"
        PARAMS[Function Parameters<br/>graph_name, query, params]
        DOC[Docstring<br/>Becomes tool description]
        BODY[Function Body<br/>Business logic]
        RETURN[Return Value<br/>JSON string]
    end

    DEF --> DEC
    DEC --> REG

    CLIENT --> DISPATCH
    DISPATCH --> EXEC

    DEF -.-> PARAMS
    DEF -.-> DOC
    DEF -.-> BODY
    DEF -.-> RETURN

    EXEC --> PARAMS
    EXEC --> BODY
    EXEC --> RETURN

    style DEC fill:#e8f5e9
    style REG fill:#e8f5e9
    style DISPATCH fill:#e1f5ff
```

## Deployment Architecture

The system supports multiple deployment modes for different use cases.

```mermaid
flowchart TB
    subgraph "Development Mode"
        DEV_ENTRY[server_dev.py<br/>Standalone]
        DEV_MCP[FastMCP Inspector<br/>Web UI]
    end

    subgraph "Production Mode"
        PROD_ENTRY[main.py<br/>Entry Point]
        PROD_SERVER[server.py<br/>MCP Server]
    end

    subgraph "MCP Clients"
        CLAUDE_DESKTOP[Claude Desktop<br/>Direct Python]
        CLAUDE_CODE[Claude Code<br/>via uv run]
        CUSTOM[Custom MCP Client<br/>stdio transport]
    end

    subgraph "FalkorDB"
        LOCAL_DB[(Local FalkorDB<br/>localhost:6379)]
        REMOTE_DB[(Remote FalkorDB<br/>Custom host:port)]
    end

    subgraph "Configuration"
        ENV_FILE[.env file]
        ENV_VARS[Environment Variables]
    end

    DEV_ENTRY -->|HTTP| DEV_MCP
    DEV_ENTRY --> LOCAL_DB

    PROD_ENTRY --> PROD_SERVER

    CLAUDE_DESKTOP -->|stdio| PROD_SERVER
    CLAUDE_CODE -->|stdio| PROD_SERVER
    CUSTOM -->|stdio| PROD_SERVER

    PROD_SERVER --> LOCAL_DB
    PROD_SERVER --> REMOTE_DB

    ENV_FILE -.->|dotenv| PROD_SERVER
    ENV_VARS -.->|os.getenv| PROD_SERVER

    style DEV_ENTRY fill:#fff4e1
    style PROD_ENTRY fill:#e1f5ff
    style PROD_SERVER fill:#e8f5e9
    style ENV_FILE fill:#fff9c4
```

## Package Structure

Visual representation of the package organization and file relationships.

```mermaid
flowchart TD
    ROOT[falkordb-fastmcp/]

    ROOT --> SRC[src/]
    ROOT --> MAIN[main.py<br/>Production Entry]
    ROOT --> DEV[server_dev.py<br/>Development Entry]
    ROOT --> PYPROJECT[pyproject.toml<br/>Project Config]
    ROOT --> ENV[.env.example<br/>Config Template]
    ROOT --> README[README.md]

    SRC --> PKG[falkordb_mcp/]

    PKG --> INIT[__init__.py<br/>version = '1.0.0']
    PKG --> SERVER[server.py<br/>MCP Server<br/>Tools & Resources]
    PKG --> SERVICE[service.py<br/>FalkorDBService<br/>Database Operations]
    PKG --> CONFIG[config.py<br/>FalkorDBConfig<br/>Environment Config]

    style ROOT fill:#f5f5f5
    style SRC fill:#e1f5ff
    style PKG fill:#e8f5e9
    style MAIN fill:#e1f5ff
    style DEV fill:#fff4e1
    style SERVER fill:#e8f5e9
    style SERVICE fill:#f3e5f5
    style CONFIG fill:#fff9c4
```
