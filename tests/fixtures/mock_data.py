"""Mock data for FalkorDB query results."""

from unittest.mock import Mock


def create_mock_query_result(rows, headers=None, **stats):
    """Create a mock QueryResult object.

    Args:
        rows: List of lists representing result rows
        headers: List of column names
        **stats: Query execution statistics

    Returns:
        Mock QueryResult object
    """
    mock_result = Mock()
    mock_result.result_set = rows
    mock_result.header = headers or []

    # Statistics
    mock_result.nodes_created = stats.get('nodes_created', 0)
    mock_result.nodes_deleted = stats.get('nodes_deleted', 0)
    mock_result.relationships_created = stats.get('relationships_created', 0)
    mock_result.relationships_deleted = stats.get('relationships_deleted', 0)
    mock_result.properties_set = stats.get('properties_set', 0)
    mock_result.labels_added = stats.get('labels_added', 0)
    mock_result.labels_removed = stats.get('labels_removed', 0)

    return mock_result


# Pre-built fixtures for common scenarios
MOCK_COUNT_RESULT = create_mock_query_result([[42]], ["count(n)"])
MOCK_EMPTY_RESULT = create_mock_query_result([], [])
MOCK_LABELS_RESULT = create_mock_query_result(
    [["Entity"], ["Episodic"], ["Community"]],
    ["label"]
)
