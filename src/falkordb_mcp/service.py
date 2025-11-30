"""FalkorDB service layer for database operations."""

import logging
from typing import Any, Dict, List, Optional

from falkordb import FalkorDB
from falkordb.node import Node
from falkordb.edge import Edge

from .config import config

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
            logger.info(
                f"✓ Connected to FalkorDB at {config.host}:{config.port}"
            )
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
        """
        Execute a Cypher query against a FalkorDB graph.

        Args:
            graph_name: Name of the graph to query
            query: Cypher query to execute
            params: Optional query parameters

        Returns:
            Dictionary with query results and metadata

        Raises:
            Exception: If query execution fails
        """
        try:
            graph = self.client.select_graph(graph_name)
            result = graph.query(query, params or {})

            # Extract data from QueryResult object for JSON serialization
            # Serialize Node/Edge objects to dicts
            data = []
            if result.result_set:
                data = [[_serialize_value(cell) for cell in row] for row in result.result_set]

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
            logger.error(
                f"Error executing query on graph '{sanitized_graph}': {e}"
            )
            raise

    def list_graphs(self) -> List[str]:
        """
        List all available graphs in FalkorDB.

        Returns:
            List of graph names

        Raises:
            Exception: If listing fails
        """
        try:
            return self.client.list_graphs()
        except Exception as e:
            logger.error(f"Error listing FalkorDB graphs: {e}")
            raise

    def get_graph_metadata(self, graph_name: str) -> Dict[str, Any]:
        """
        Get metadata about a specific graph.

        Args:
            graph_name: Name of the graph

        Returns:
            Dictionary containing graph metadata with:
                - name: Graph name
                - labels: List of node label strings

        Raises:
            Exception: If metadata retrieval fails
        """
        try:
            graph = self.client.select_graph(graph_name)
            # Execute a simple query to get graph statistics
            labels_result = graph.query("CALL db.labels()")

            # Extract data from QueryResult object for JSON serialization
            # FalkorDB query results must be accessed via .result_set property
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

    def close(self) -> None:
        """Close connection to FalkorDB."""
        if self._client:
            self._client.close()
            self._client = None
            logger.info("✓ FalkorDB connection closed")


# Global service instance
_service: Optional[FalkorDBService] = None


def get_service() -> FalkorDBService:
    """Get or create the global FalkorDB service instance."""
    global _service
    if _service is None:
        _service = FalkorDBService()
    return _service
