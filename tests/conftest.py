"""Pytest fixtures for FalkorDB FastMCP tests."""

import sys
from pathlib import Path
# Add src to path
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import pytest
from unittest.mock import Mock, patch
from falkordb.node import Node
from falkordb.edge import Edge


@pytest.fixture
def mock_node():
    """Mock FalkorDB Node object."""
    mock = Mock(spec=Node)
    mock.id = 123
    mock.labels = {'Entity', 'Person'}
    mock.properties = {
        'name': 'Alice',
        'age': 30,
        'tags': ['developer', 'python']
    }
    return mock


@pytest.fixture
def mock_edge():
    """Mock FalkorDB Edge object."""
    mock = Mock(spec=Edge)
    mock.id = 456
    mock.relation = 'KNOWS'
    mock.src_node = 123
    mock.dest_node = 789
    mock.properties = {
        'since': '2020',
        'strength': 0.8
    }
    return mock


@pytest.fixture
def mock_query_result():
    """Mock FalkorDB QueryResult object with sample data."""
    mock_result = Mock()
    mock_result.result_set = [
        [1, "Alice", 30],
        [2, "Bob", 25],
        [3, "Charlie", 35]
    ]
    mock_result.header = ["id", "name", "age"]
    mock_result.nodes_created = 0
    mock_result.nodes_deleted = 0
    mock_result.relationships_created = 0
    mock_result.relationships_deleted = 0
    mock_result.properties_set = 0
    mock_result.labels_added = 0
    mock_result.labels_removed = 0
    return mock_result


@pytest.fixture
def mock_query_result_count():
    """Mock QueryResult for count queries."""
    mock_result = Mock()
    mock_result.result_set = [[42]]
    mock_result.header = ["count(n)"]
    mock_result.nodes_created = 0
    mock_result.nodes_deleted = 0
    mock_result.relationships_created = 0
    mock_result.relationships_deleted = 0
    mock_result.properties_set = 0
    mock_result.labels_added = 0
    mock_result.labels_removed = 0
    return mock_result


@pytest.fixture
def mock_query_result_empty():
    """Mock empty QueryResult."""
    mock_result = Mock()
    mock_result.result_set = []
    mock_result.header = []
    mock_result.nodes_created = 0
    mock_result.nodes_deleted = 0
    mock_result.relationships_created = 0
    mock_result.relationships_deleted = 0
    mock_result.properties_set = 0
    mock_result.labels_added = 0
    mock_result.labels_removed = 0
    return mock_result


@pytest.fixture
def mock_query_result_with_nodes(mock_node):
    """Mock QueryResult containing Node objects."""
    mock_result = Mock()
    mock_result.result_set = [
        [mock_node],
        [mock_node]
    ]
    mock_result.header = [['node', 'n']]
    mock_result.nodes_created = 0
    mock_result.nodes_deleted = 0
    mock_result.relationships_created = 0
    mock_result.relationships_deleted = 0
    mock_result.properties_set = 0
    mock_result.labels_added = 0
    mock_result.labels_removed = 0
    return mock_result


@pytest.fixture
def mock_query_result_with_edges(mock_edge):
    """Mock QueryResult containing Edge objects."""
    mock_result = Mock()
    mock_result.result_set = [
        [mock_edge],
        [mock_edge]
    ]
    mock_result.header = [['relationship', 'r']]
    mock_result.nodes_created = 0
    mock_result.nodes_deleted = 0
    mock_result.relationships_created = 0
    mock_result.relationships_deleted = 0
    mock_result.properties_set = 0
    mock_result.labels_added = 0
    mock_result.labels_removed = 0
    return mock_result


@pytest.fixture
def mock_query_result_mixed(mock_node, mock_edge):
    """Mock QueryResult with mixed types (node, edge, primitives)."""
    mock_result = Mock()
    mock_result.result_set = [
        [mock_node, mock_edge, "Alice", 30],
    ]
    mock_result.header = [['node', 'n'], ['relationship', 'r'], ['string', 'name'], ['int', 'age']]
    mock_result.nodes_created = 0
    mock_result.nodes_deleted = 0
    mock_result.relationships_created = 0
    mock_result.relationships_deleted = 0
    mock_result.properties_set = 0
    mock_result.labels_added = 0
    mock_result.labels_removed = 0
    return mock_result


@pytest.fixture
def mock_falkordb_service(mock_query_result):
    """Mock FalkorDBService with mocked client."""
    import sys
    from pathlib import Path
    # Add src to path
    src_path = str(Path(__file__).parent.parent / "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    with patch('falkordb_mcp.service.FalkorDB') as mock_fdb:
        mock_client = Mock()
        mock_graph = Mock()

        mock_fdb.return_value = mock_client
        mock_client.select_graph.return_value = mock_graph
        mock_client.list_graphs.return_value = ["graph1", "graph2"]
        mock_client.connection.ping.return_value = True
        mock_graph.query.return_value = mock_query_result

        # Reset singleton
        import falkordb_mcp.service as service_module
        service_module._service = None

        from falkordb_mcp.service import FalkorDBService
        service = FalkorDBService()
        yield service

        # Cleanup
        service_module._service = None
