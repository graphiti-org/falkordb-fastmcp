"""Test suite for FastMCP server/MCP tools."""

import sys
from pathlib import Path
# Add src to path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import pytest
import json
from unittest.mock import Mock, patch
from falkordb_mcp.server import execute_query, list_graphs, get_graph_metadata


class TestExecuteQueryTool:
    """Test suite for execute_query MCP tool."""

    def test_execute_query_returns_json_string(self, mock_falkordb_service):
        """Test execute_query tool returns valid JSON string."""
        with patch('falkordb_mcp.server.get_service', return_value=mock_falkordb_service):
            result_json = execute_query("test_graph", "MATCH (n) RETURN n")

            assert isinstance(result_json, str)
            result = json.loads(result_json)
            assert result["success"] is True

    def test_execute_query_success_structure(self, mock_falkordb_service):
        """Test execute_query success response structure."""
        with patch('falkordb_mcp.server.get_service', return_value=mock_falkordb_service):
            result_json = execute_query("test_graph", "MATCH (n) RETURN n")
            result = json.loads(result_json)

            assert result["success"] is True
            assert "data" in result
            assert "metadata" in result
            assert result["metadata"]["graphName"] == "test_graph"
            assert result["metadata"]["query"] == "MATCH (n) RETURN n"
            assert "timestamp" in result["metadata"]

    def test_execute_query_data_contains_result_set(self, mock_falkordb_service):
        """Test execute_query data contains result_set."""
        with patch('falkordb_mcp.server.get_service', return_value=mock_falkordb_service):
            result_json = execute_query("test_graph", "MATCH (n) RETURN n")
            result = json.loads(result_json)

            assert "result_set" in result["data"]
            assert isinstance(result["data"]["result_set"], list)
            assert len(result["data"]["result_set"]) == 3

    def test_execute_query_error_handling(self):
        """Test execute_query error response structure."""
        mock_service = Mock()
        mock_service.execute_query.side_effect = Exception("Test error")

        with patch('falkordb_mcp.server.get_service', return_value=mock_service):
            result_json = execute_query("test_graph", "INVALID")
            result = json.loads(result_json)

            assert result["success"] is False
            assert "error" in result
            assert "Test error" in result["error"]
            assert result["graphName"] == "test_graph"

    def test_execute_query_with_params(self, mock_falkordb_service):
        """Test execute_query with parameters."""
        with patch('falkordb_mcp.server.get_service', return_value=mock_falkordb_service):
            params = {"id": 123}
            result_json = execute_query(
                "test_graph",
                "MATCH (n) WHERE n.id = $id RETURN n",
                params
            )
            result = json.loads(result_json)

            assert result["success"] is True
            mock_falkordb_service.execute_query.assert_called_with(
                "test_graph",
                "MATCH (n) WHERE n.id = $id RETURN n",
                params
            )


class TestRegressionTests:
    """Regression tests for BUG-001 fix."""

    def test_bug_001_query_result_serialization(self, mock_falkordb_service):
        """Regression test: QueryResult must be JSON serializable."""
        with patch('falkordb_mcp.server.get_service', return_value=mock_falkordb_service):
            # This should not raise "Object of type QueryResult is not JSON serializable"
            result_json = execute_query("graphiti_meta_knowledge", "MATCH (n) RETURN count(n)")
            result = json.loads(result_json)

            assert result["success"] is True
            assert "data" in result
            # Should be able to serialize to JSON without error
            json.dumps(result)

    def test_bug_001_count_query(self, mock_falkordb_service, mock_query_result_count):
        """Regression test: Count queries work correctly."""
        mock_graph = mock_falkordb_service.client.select_graph("test_graph")
        mock_graph.query.return_value = mock_query_result_count

        with patch('falkordb_mcp.server.get_service', return_value=mock_falkordb_service):
            result_json = execute_query("test_graph", "MATCH (n) RETURN count(n)")
            result = json.loads(result_json)

            assert result["success"] is True
            assert result["data"]["result_set"] == [[42]]
