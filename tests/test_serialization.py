"""Test suite for FalkorDB object serialization."""

import sys
from pathlib import Path
# Add src to path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import pytest
import json
from unittest.mock import Mock
from falkordb_mcp.service import _serialize_value


class TestSerializeValue:
    """Test suite for _serialize_value function."""

    def test_serialize_node(self, mock_node):
        """Test serialization of Node object."""
        result = _serialize_value(mock_node)

        assert isinstance(result, dict)
        assert result["type"] == "node"
        assert result["id"] == 123
        assert set(result["labels"]) == {'Entity', 'Person'}
        assert result["properties"]["name"] == "Alice"
        assert result["properties"]["age"] == 30
        assert result["properties"]["tags"] == ['developer', 'python']

    def test_serialize_node_json_compatible(self, mock_node):
        """Test that serialized Node is JSON compatible."""
        result = _serialize_value(mock_node)

        # Should not raise exception
        json_str = json.dumps(result)
        assert json_str is not None

        # Verify round-trip
        parsed = json.loads(json_str)
        assert parsed["type"] == "node"
        assert parsed["id"] == 123

    def test_serialize_edge(self, mock_edge):
        """Test serialization of Edge object."""
        result = _serialize_value(mock_edge)

        assert isinstance(result, dict)
        assert result["type"] == "edge"
        assert result["id"] == 456
        assert result["relation"] == "KNOWS"
        assert result["src_node"] == 123
        assert result["dest_node"] == 789
        assert result["properties"]["since"] == "2020"
        assert result["properties"]["strength"] == 0.8

    def test_serialize_edge_json_compatible(self, mock_edge):
        """Test that serialized Edge is JSON compatible."""
        result = _serialize_value(mock_edge)

        # Should not raise exception
        json_str = json.dumps(result)
        assert json_str is not None

        # Verify round-trip
        parsed = json.loads(json_str)
        assert parsed["type"] == "edge"
        assert parsed["relation"] == "KNOWS"

    def test_serialize_primitives(self):
        """Test serialization of primitive types."""
        assert _serialize_value(42) == 42
        assert _serialize_value("hello") == "hello"
        assert _serialize_value(3.14) == 3.14
        assert _serialize_value(True) is True
        assert _serialize_value(None) is None

    def test_serialize_list(self, mock_node):
        """Test serialization of lists containing various types."""
        test_list = [42, "hello", mock_node]
        result = _serialize_value(test_list)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == 42
        assert result[1] == "hello"
        assert result[2]["type"] == "node"
        assert result[2]["id"] == 123

    def test_serialize_nested_list(self, mock_node, mock_edge):
        """Test serialization of nested lists."""
        test_list = [[mock_node], [mock_edge, 42]]
        result = _serialize_value(test_list)

        assert isinstance(result, list)
        assert result[0][0]["type"] == "node"
        assert result[1][0]["type"] == "edge"
        assert result[1][1] == 42

    def test_serialize_dict(self, mock_node):
        """Test serialization of dictionaries."""
        test_dict = {
            "node": mock_node,
            "value": 42,
            "name": "test"
        }
        result = _serialize_value(test_dict)

        assert isinstance(result, dict)
        assert result["node"]["type"] == "node"
        assert result["value"] == 42
        assert result["name"] == "test"

    def test_serialize_tuple(self, mock_node):
        """Test serialization of tuples (converts to list)."""
        test_tuple = (mock_node, 42, "hello")
        result = _serialize_value(test_tuple)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["type"] == "node"
        assert result[1] == 42
        assert result[2] == "hello"

    def test_serialize_complex_nested_structure(self, mock_node, mock_edge):
        """Test serialization of complex nested structures."""
        test_data = {
            "nodes": [mock_node, mock_node],
            "edges": [mock_edge],
            "metadata": {
                "count": 2,
                "nested": [1, 2, mock_node]
            }
        }
        result = _serialize_value(test_data)

        assert result["nodes"][0]["type"] == "node"
        assert result["nodes"][1]["type"] == "node"
        assert result["edges"][0]["type"] == "edge"
        assert result["metadata"]["count"] == 2
        assert result["metadata"]["nested"][2]["type"] == "node"

        # Verify JSON compatibility
        json_str = json.dumps(result)
        assert json_str is not None

    def test_serialize_node_with_nested_properties(self):
        """Test serialization of Node with nested property values."""
        from falkordb.node import Node

        mock_node = Mock(spec=Node)
        mock_node.id = 999
        mock_node.labels = {'ComplexNode'}
        mock_node.properties = {
            'simple': 'value',
            'nested_list': [1, 2, 3],
            'nested_dict': {'key': 'value'}
        }

        result = _serialize_value(mock_node)

        assert result["properties"]["simple"] == "value"
        assert result["properties"]["nested_list"] == [1, 2, 3]
        assert result["properties"]["nested_dict"] == {'key': 'value'}

        # Verify JSON compatibility
        json_str = json.dumps(result)
        assert json_str is not None
