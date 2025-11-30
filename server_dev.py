#!/usr/bin/env python3
"""
Standalone FastMCP server for development and inspector use.
This version has no relative imports for compatibility with fastmcp dev.
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from falkordb import FalkorDB
from falkordb.node import Node
from falkordb.edge import Edge
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _serialize_value(value: Any) -> Any:
    """Serialize FalkorDB objects to JSON-compatible types.

    Args:
        value: Value to serialize (may be Node, Edge, or primitive)

    Returns:
        JSON-serializable value
    """
    if isinstance(value, Node):
        return {
            "type": "node",
            "id": value.id,
            "labels": list(value.labels),
            "properties": dict(value.properties)
        }
    elif isinstance(value, Edge):
        return {
            "type": "edge",
            "id": value.id,
            "relation": value.relation,
            "src_node": value.src_node,
            "dest_node": value.dest_node,
            "properties": dict(value.properties)
        }
    elif isinstance(value, (list, tuple)):
        return [_serialize_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    else:
        # Primitive types (int, str, float, bool, None)
        return value


# Configuration
@dataclass
class FalkorDBConfig:
    """FalkorDB connection configuration."""

    host: str
    port: int
    username: Optional[str]
    password: Optional[str]

    @classmethod
    def from_env(cls) -> "FalkorDBConfig":
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("FALKORDB_HOST", "localhost"),
            port=int(os.getenv("FALKORDB_PORT", "6379")),
            username=os.getenv("FALKORDB_USERNAME") or None,
            password=os.getenv("FALKORDB_PASSWORD") or None,
        )


config = FalkorDBConfig.from_env()


# Service Layer
class FalkorDBService:
    """Service for interacting with FalkorDB graph database."""

    def __init__(self):
        """Initialize FalkorDB service."""
        self._client: Optional[FalkorDB] = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize connection to FalkorDB."""
        try:
            self._client = FalkorDB(
                host=config.host,
                port=config.port,
                username=config.username,
                password=config.password,
            )
            # Test connection
            self._client.connection.ping()
            logger.info(f"✓ Connected to FalkorDB at {config.host}:{config.port}")
        except Exception as e:
            logger.error(f"Failed to connect to FalkorDB: {e}")
            raise

    @property
    def client(self) -> FalkorDB:
        """Get FalkorDB client instance."""
        if self._client is None:
            raise RuntimeError("FalkorDB client not initialized")
        return self._client

    def execute_query(
        self, graph_name: str, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a Cypher query against a FalkorDB graph."""
        try:
            graph = self.client.select_graph(graph_name)
            result = graph.query(query, params or {})

            # Extract data from QueryResult object for JSON serialization
            data = []
            if result.result_set:
                data = [list(row) for row in result.result_set]

            # Include column headers if available
            headers = []
            if hasattr(result, 'header') and result.header:
                headers = result.header

            return {
                "result_set": data,
                "headers": headers,
                "statistics": {
                    "nodes_created": getattr(result, 'nodes_created', 0),
                    "nodes_deleted": getattr(result, 'nodes_deleted', 0),
                    "relationships_created": getattr(result, 'relationships_created', 0),
                    "relationships_deleted": getattr(result, 'relationships_deleted', 0),
                    "properties_set": getattr(result, 'properties_set', 0),
                    "labels_added": getattr(result, 'labels_added', 0),
                    "labels_removed": getattr(result, 'labels_removed', 0),
                }
            }
        except Exception as e:
            sanitized_graph = graph_name.replace("\n", "").replace("\r", "")
            logger.error(f"Error executing query on graph '{sanitized_graph}': {e}")
            raise

    def list_graphs(self) -> List[str]:
        """List all available graphs in FalkorDB."""
        try:
            return self.client.list_graphs()
        except Exception as e:
            logger.error(f"Error listing FalkorDB graphs: {e}")
            raise

    def get_graph_metadata(self, graph_name: str) -> Dict[str, Any]:
        """Get metadata about a specific graph."""
        try:
            graph = self.client.select_graph(graph_name)
            labels_result = graph.query("CALL db.labels()")

            # Extract data from QueryResult object for JSON serialization
            labels_list = []
            if labels_result.result_set:
                labels_list = [row[0] for row in labels_result.result_set]

            return {
                "name": graph_name,
                "labels": labels_list,
            }
        except Exception as e:
            sanitized = graph_name.replace("\n", "").replace("\r", "")
            logger.error(f"Error getting metadata for graph '{sanitized}': {e}")
            raise


# Global service instance
_service: Optional[FalkorDBService] = None


def get_service() -> FalkorDBService:
    """Get or create the global FalkorDB service instance."""
    global _service
    if _service is None:
        _service = FalkorDBService()
    return _service


# Initialize MCP server
mcp = FastMCP("FalkorDB")


# MCP Tools
@mcp.tool()
def execute_query(
    graph_name: str, query: str, params: Optional[Dict[str, Any]] = None
) -> str:
    """
    Execute a Cypher query against a FalkorDB graph.

    Use this to query nodes, relationships, and graph patterns in FalkorDB.

    Args:
        graph_name: Name of the graph to query
        query: Cypher query to execute (e.g., "MATCH (n:Person) RETURN n LIMIT 10")
        params: Optional query parameters as key-value pairs

    Returns:
        JSON string with query results and metadata
    """
    try:
        service = get_service()
        result = service.execute_query(graph_name, query, params)

        return json.dumps(
            {
                "success": True,
                "data": result,
                "metadata": {
                    "graphName": graph_name,
                    "query": query,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": str(e),
                "graphName": graph_name,
                "query": query,
            },
            indent=2,
        )


@mcp.tool()
def list_graphs() -> str:
    """
    List all available graphs in the FalkorDB instance.

    Returns:
        JSON string with list of graph names and count
    """
    try:
        service = get_service()
        graphs = service.list_graphs()

        return json.dumps(
            {
                "success": True,
                "graphs": graphs,
                "count": len(graphs),
                "timestamp": datetime.utcnow().isoformat(),
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": str(e),
            },
            indent=2,
        )


@mcp.tool()
def get_graph_metadata(graph_name: str) -> str:
    """
    Get metadata and labels for a specific FalkorDB graph.

    Args:
        graph_name: Name of the graph

    Returns:
        JSON string with graph metadata
    """
    try:
        service = get_service()
        metadata = service.get_graph_metadata(graph_name)

        return json.dumps(
            {
                "success": True,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat(),
            },
            indent=2,
        )
    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": str(e),
                "graphName": graph_name,
            },
            indent=2,
        )


# MCP Resources
@mcp.resource("falkordb://graphs")
def get_available_graphs() -> str:
    """
    Resource providing list of all available graphs in FalkorDB.

    Returns:
        JSON string with graphs, count, and server information
    """
    service = get_service()
    graphs = service.list_graphs()

    return json.dumps(
        {
            "graphs": graphs,
            "count": len(graphs),
            "host": config.host,
            "port": config.port,
            "timestamp": datetime.utcnow().isoformat(),
        },
        indent=2,
    )


@mcp.resource("falkordb://status")
def get_server_status() -> str:
    """
    Resource providing FalkorDB connection status and server information.

    Returns:
        JSON string with server status
    """
    return json.dumps(
        {
            "status": "connected",
            "host": config.host,
            "port": config.port,
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
        },
        indent=2,
    )
