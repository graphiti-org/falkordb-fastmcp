#!/usr/bin/env python3
"""
FalkorDB FastMCP Server

A Model Context Protocol server for FalkorDB graph database using FastMCP.
Provides tools and resources for querying and managing FalkorDB graphs.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from .config import config
from .service import get_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("FalkorDB")


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


def main():
    """Main entry point for the MCP server."""
    logger.info("Starting FalkorDB FastMCP Server...")
    logger.info(f"FalkorDB: {config.host}:{config.port}")

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
