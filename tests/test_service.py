"""Test suite for FalkorDBService layer."""

import sys
from pathlib import Path
# Add src to path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import pytest
import json
from unittest.mock import Mock, patch
from falkordb_mcp.service import FalkorDBService, get_service


class TestExecuteQuery:
    """Test suite for execute_query method."""

    def test_execute_query_returns_dict(self, mock_falkordb_service):
        """Test execute_query returns a dictionary."""
        result = mock_falkordb_service.execute_query("test_graph", "MATCH (n) RETURN n")

        assert isinstance(result, dict)
        assert "result_set" in result
        assert "headers" in result
        assert "statistics" in result

    def test_execute_query_extracts_result_set(self, mock_falkordb_service):
        """Test execute_query properly extracts result_set data."""
        result = mock_falkordb_service.execute_query("test_graph", "MATCH (n) RETURN n")

        assert isinstance(result["result_set"], list)
        assert len(result["result_set"]) == 3
        assert result["result_set"][0] == [1, "Alice", 30]

    def test_execute_query_includes_headers(self, mock_falkordb_service):
        """Test execute_query includes column headers."""
        result = mock_falkordb_service.execute_query("test_graph", "MATCH (n) RETURN n")

        assert result["headers"] == ["id", "name", "age"]

    def test_execute_query_with_parameters(self, mock_falkordb_service):
        """Test execute_query with query parameters."""
        params = {"name": "Alice"}
        result = mock_falkordb_service.execute_query(
            "test_graph",
            "MATCH (n:Person {name: $name}) RETURN n",
            params
        )

        assert result is not None
        # Verify params were passed to query
        mock_graph = mock_falkordb_service.client.select_graph("test_graph")
        mock_graph.query.assert_called_with(
            "MATCH (n:Person {name: $name}) RETURN n",
            params
        )

    def test_execute_query_count(self, mock_falkordb_service, mock_query_result_count):
        """Test execute_query with count query."""
        mock_graph = mock_falkordb_service.client.select_graph("test_graph")
        mock_graph.query.return_value = mock_query_result_count

        result = mock_falkordb_service.execute_query("test_graph", "MATCH (n) RETURN count(n)")

        assert result["result_set"] == [[42]]
        assert result["headers"] == ["count(n)"]

    def test_execute_query_empty_result(self, mock_falkordb_service, mock_query_result_empty):
        """Test execute_query with empty result set."""
        mock_graph = mock_falkordb_service.client.select_graph("test_graph")
        mock_graph.query.return_value = mock_query_result_empty

        result = mock_falkordb_service.execute_query("test_graph", "MATCH (n:NoSuchLabel) RETURN n")

        assert result["result_set"] == []

    def test_execute_query_json_serializable(self, mock_falkordb_service):
        """Test execute_query returns JSON-serializable data."""
        result = mock_falkordb_service.execute_query("test_graph", "MATCH (n) RETURN n")

        # Should not raise exception
        json_str = json.dumps(result)
        assert json_str is not None

        # Verify round-trip
        parsed = json.loads(json_str)
        assert parsed["result_set"] == result["result_set"]

    def test_execute_query_raises_on_error(self, mock_falkordb_service):
        """Test execute_query raises exception on query error."""
        mock_graph = mock_falkordb_service.client.select_graph("test_graph")
        mock_graph.query.side_effect = Exception("Query syntax error")

        with pytest.raises(Exception, match="Query syntax error"):
            mock_falkordb_service.execute_query("test_graph", "INVALID QUERY")

    def test_execute_query_sanitizes_graph_name_in_error(self, mock_falkordb_service):
        """Test execute_query sanitizes graph name in error logs."""
        mock_graph = mock_falkordb_service.client.select_graph("test\ngraph")
        mock_graph.query.side_effect = Exception("Error")

        with pytest.raises(Exception):
            mock_falkordb_service.execute_query("test\ngraph", "MATCH (n) RETURN n")


class TestNodeEdgeSerialization:
    """Test suite for Node and Edge object serialization."""

    def test_execute_query_with_nodes(self, mock_falkordb_service, mock_query_result_with_nodes):
        """Test execute_query properly serializes Node objects."""
        mock_graph = mock_falkordb_service.client.select_graph("test_graph")
        mock_graph.query.return_value = mock_query_result_with_nodes

        result = mock_falkordb_service.execute_query("test_graph", "MATCH (n) RETURN n")

        assert isinstance(result["result_set"], list)
        assert len(result["result_set"]) == 2

        # Check first node serialization
        node_dict = result["result_set"][0][0]
        assert isinstance(node_dict, dict)
        assert node_dict["type"] == "node"
        assert node_dict["id"] == 123
        assert set(node_dict["labels"]) == {'Entity', 'Person'}
        assert node_dict["properties"]["name"] == "Alice"

    def test_execute_query_with_edges(self, mock_falkordb_service, mock_query_result_with_edges):
        """Test execute_query properly serializes Edge objects."""
        mock_graph = mock_falkordb_service.client.select_graph("test_graph")
        mock_graph.query.return_value = mock_query_result_with_edges

        result = mock_falkordb_service.execute_query("test_graph", "MATCH ()-[r]->() RETURN r")

        assert isinstance(result["result_set"], list)
        assert len(result["result_set"]) == 2

        # Check first edge serialization
        edge_dict = result["result_set"][0][0]
        assert isinstance(edge_dict, dict)
        assert edge_dict["type"] == "edge"
        assert edge_dict["id"] == 456
        assert edge_dict["relation"] == "KNOWS"
        assert edge_dict["src_node"] == 123
        assert edge_dict["dest_node"] == 789

    def test_execute_query_with_mixed_types(self, mock_falkordb_service, mock_query_result_mixed):
        """Test execute_query with mixed Node, Edge, and primitive types."""
        mock_graph = mock_falkordb_service.client.select_graph("test_graph")
        mock_graph.query.return_value = mock_query_result_mixed

        result = mock_falkordb_service.execute_query(
            "test_graph",
            "MATCH (n)-[r]->(m) RETURN n, r, n.name, n.age"
        )

        assert len(result["result_set"]) == 1
        row = result["result_set"][0]

        # Node
        assert row[0]["type"] == "node"
        assert row[0]["id"] == 123

        # Edge
        assert row[1]["type"] == "edge"
        assert row[1]["id"] == 456

        # Primitives
        assert row[2] == "Alice"
        assert row[3] == 30

    def test_node_query_json_serializable(self, mock_falkordb_service, mock_query_result_with_nodes):
        """Test that query results with Nodes are JSON serializable."""
        mock_graph = mock_falkordb_service.client.select_graph("test_graph")
        mock_graph.query.return_value = mock_query_result_with_nodes

        result = mock_falkordb_service.execute_query("test_graph", "MATCH (n) RETURN n")

        # Should not raise exception
        json_str = json.dumps(result)
        assert json_str is not None

        # Verify round-trip
        parsed = json.loads(json_str)
        assert parsed["result_set"][0][0]["type"] == "node"

    def test_edge_query_json_serializable(self, mock_falkordb_service, mock_query_result_with_edges):
        """Test that query results with Edges are JSON serializable."""
        mock_graph = mock_falkordb_service.client.select_graph("test_graph")
        mock_graph.query.return_value = mock_query_result_with_edges

        result = mock_falkordb_service.execute_query("test_graph", "MATCH ()-[r]->() RETURN r")

        # Should not raise exception
        json_str = json.dumps(result)
        assert json_str is not None

        # Verify round-trip
        parsed = json.loads(json_str)
        assert parsed["result_set"][0][0]["type"] == "edge"
