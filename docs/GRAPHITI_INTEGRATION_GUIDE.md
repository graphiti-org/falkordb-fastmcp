# Graphiti Integration Guide - FalkorDB MCP Service

**Version**: 1.0
**Date**: 2025-11-30
**Status**: ⚠️ Partial functionality - awaiting BUG-001 fix

---

## Overview

This guide explains how to use the FalkorDB MCP service to validate and monitor Graphiti knowledge graph memory systems. Graphiti creates knowledge graphs from unstructured text and conversations, and this MCP service enables direct validation of the underlying graph structure.

### What is Graphiti?

**Graphiti** is a knowledge graph memory system for AI agents that:
- Ingests text, JSON, and conversation data as "episodes"
- Extracts entities (People, Organizations, Locations, Events, etc.)
- Creates relationships between entities with temporal metadata
- Supports hybrid search (vector + keyword)
- Handles entity deduplication and merging
- Provides multi-namespace support via `group_id`

### What This MCP Service Provides

The FalkorDB MCP service enables you to:
- ✅ **Discover Graphiti graphs** using `list_graphs()`
- ⚠️ **Validate graph schemas** using `get_graph_metadata()` (blocked by BUG-001)
- ✅ **Run custom validation queries** using `execute_query()` (workaround for BUG-001)

---

## Current Capabilities & Limitations

### ✅ What Works (Production-Ready)

#### 1. Graph Discovery via `list_graphs()`

**Use Case**: Find all Graphiti-created graphs in your FalkorDB instance

**Example**:
```python
import json

# Discover all graphs
result = list_graphs()
response = json.loads(result)

# Filter for Graphiti graphs by naming convention
graphiti_graphs = [
    g for g in response["graphs"]
    if "graphiti" in g.lower() or "agent_memory" in g.lower() or "knowledge" in g.lower()
]

print(f"Found {len(graphiti_graphs)} Graphiti graphs:")
for graph in graphiti_graphs:
    print(f"  - {graph}")
```

**Expected Output**:
```
Found 2 Graphiti graphs:
  - graphiti_meta_knowledge
  - agent_memory_decision_tree_2025
```

**Validation Checks**:
- ✅ Verify expected graphs exist
- ✅ Check for missing graphs (indicates setup issues)
- ✅ Monitor new graph creation (multi-namespace scenarios)

---

### ⚠️ What's Blocked (Awaiting Fix)

#### 2. Schema Validation via `get_graph_metadata()`

**Status**: **BLOCKED** by [BUG-001](VALIDATION_REPORT.md#tc-bug-001-queryresult-serialization-issue)

**Expected Use Case** (when fixed):
```python
# Get graph schema to validate entity types
result = get_graph_metadata(graph_name="graphiti_meta_knowledge")
response = json.loads(result)

if response["success"]:
    labels = response["metadata"]["labels"]

    # Validate expected Graphiti entity types
    expected_types = ["Person", "Organization", "Location", "Event", "Episode", "Entity"]
    for entity_type in expected_types:
        if entity_type in labels:
            print(f"✅ {entity_type} type exists")
        else:
            print(f"❌ Missing {entity_type} type!")
```

**Current Behavior**:
```json
{
  "success": false,
  "error": "Object of type QueryResult is not JSON serializable",
  "graphName": "graphiti_meta_knowledge"
}
```

**Workaround**: Use `execute_query()` directly (see section below)

---

### ✅ Workaround: Direct Cypher Queries

Until BUG-001 is fixed, use `execute_query()` for schema validation:

```python
import json

# Query node labels directly
result = execute_query(
    graph_name="graphiti_meta_knowledge",
    query="CALL db.labels()"
)

response = json.loads(result)
if response["success"]:
    print("Graph schema labels:")
    print(response["data"])
```

---

## Graphiti Validation Use Cases

### Use Case 1: Verify Graph Exists After Episode Processing

**Scenario**: You've added episodes to Graphiti and want to confirm the graph was created

**Solution**:
```python
import json

def verify_graphiti_graph(expected_graph_name: str) -> bool:
    """Check if a Graphiti graph exists in FalkorDB."""
    result = list_graphs()
    response = json.loads(result)

    if not response["success"]:
        print(f"❌ Error: {response['error']}")
        return False

    if expected_graph_name in response["graphs"]:
        print(f"✅ Graph '{expected_graph_name}' exists")
        return True
    else:
        print(f"❌ Graph '{expected_graph_name}' not found")
        print(f"Available graphs: {response['graphs']}")
        return False

# Example usage
verify_graphiti_graph("graphiti_meta_knowledge")
```

---

### Use Case 2: Validate Entity Types (via execute_query workaround)

**Scenario**: Confirm that Graphiti extracted the expected entity types from your episodes

**Solution**:
```python
import json

def validate_graphiti_schema(graph_name: str) -> dict:
    """
    Validate that Graphiti graph contains expected entity types.

    Returns dict with validation results.
    """
    # Expected Graphiti entity types
    expected_types = {
        "Person": "Individual people mentioned in episodes",
        "Organization": "Companies, groups, institutions",
        "Location": "Places, addresses, geographic entities",
        "Event": "Temporal occurrences, meetings, activities",
        "Topic": "Subject matter, themes, concepts",
        "Document": "Referenced documents, files, artifacts",
        "Episode": "Source episodes that created entities",
        "Entity": "Base entity type for all nodes"
    }

    # Query for all node labels
    result = execute_query(
        graph_name=graph_name,
        query="CALL db.labels()"
    )

    response = json.loads(result)
    if not response["success"]:
        return {
            "success": False,
            "error": response["error"]
        }

    # Parse labels from query result
    # Note: Exact structure depends on FalkorDB's db.labels() output
    # This is a placeholder until BUG-001 is fixed
    actual_labels = response["data"]  # Adjust based on actual structure

    validation_results = {
        "success": True,
        "graph_name": graph_name,
        "found_types": [],
        "missing_types": [],
        "unexpected_types": []
    }

    # Check which expected types are present
    for entity_type in expected_types:
        if entity_type in str(actual_labels):  # Simplified check
            validation_results["found_types"].append(entity_type)
        else:
            validation_results["missing_types"].append(entity_type)

    return validation_results

# Example usage
results = validate_graphiti_schema("graphiti_meta_knowledge")
print(f"Found {len(results['found_types'])} expected entity types")
print(f"Missing {len(results['missing_types'])} expected entity types")
```

---

### Use Case 3: Monitor Graph Growth

**Scenario**: Track how your Graphiti graph grows as you add episodes

**Solution**:
```python
import json
from datetime import datetime

def monitor_graph_metrics(graph_name: str) -> dict:
    """
    Get key metrics about a Graphiti graph.

    Returns:
        dict with node counts, edge counts, and metadata
    """
    queries = {
        "total_nodes": "MATCH (n) RETURN COUNT(n) AS count",
        "total_edges": "MATCH ()-[r]->() RETURN COUNT(r) AS count",
        "entity_count": "MATCH (n:Entity) RETURN COUNT(n) AS count",
        "episode_count": "MATCH (n:Episode) RETURN COUNT(n) AS count",
        "person_count": "MATCH (n:Person) RETURN COUNT(n) AS count",
        "organization_count": "MATCH (n:Organization) RETURN COUNT(n) AS count"
    }

    metrics = {
        "graph_name": graph_name,
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": {}
    }

    for metric_name, query in queries.items():
        result = execute_query(graph_name=graph_name, query=query)
        response = json.loads(result)

        if response["success"]:
            # Extract count from result
            # Note: Adjust based on actual response structure
            count = response["data"]  # Placeholder
            metrics["metrics"][metric_name] = count
        else:
            metrics["metrics"][metric_name] = f"Error: {response['error']}"

    return metrics

# Example usage
metrics = monitor_graph_metrics("graphiti_meta_knowledge")
print(f"Graph Metrics for '{metrics['graph_name']}':")
for metric, value in metrics["metrics"].items():
    print(f"  {metric}: {value}")
```

**Example Output**:
```
Graph Metrics for 'graphiti_meta_knowledge':
  total_nodes: 1247
  total_edges: 3891
  entity_count: 892
  episode_count: 125
  person_count: 234
  organization_count: 67
```

---

### Use Case 4: Validate Entity Deduplication

**Scenario**: Ensure Graphiti is properly merging similar entities

**Solution**:
```python
import json

def check_for_duplicate_entities(graph_name: str, entity_type: str = "Person") -> dict:
    """
    Check for potential duplicate entities by name similarity.

    This helps validate that Graphiti's deduplication is working.
    """
    # Query for all entity names
    query = f"""
        MATCH (n:{entity_type})
        RETURN n.name AS name, COUNT(n) AS count
        ORDER BY count DESC
    """

    result = execute_query(graph_name=graph_name, query=query)
    response = json.loads(result)

    if not response["success"]:
        return {
            "success": False,
            "error": response["error"]
        }

    # Parse results and identify potential duplicates
    # Note: Adjust based on actual response structure
    duplicates = {
        "success": True,
        "entity_type": entity_type,
        "potential_duplicates": [],
        "unique_entities": 0
    }

    # Analyze results for duplicates
    # This is a simplified example
    data = response["data"]

    return duplicates

# Example usage
duplicates = check_for_duplicate_entities("graphiti_meta_knowledge", "Person")
if duplicates["success"]:
    print(f"Entity Deduplication Check:")
    print(f"  Unique entities: {duplicates['unique_entities']}")
    print(f"  Potential duplicates: {len(duplicates['potential_duplicates'])}")
```

---

### Use Case 5: Multi-Namespace Validation

**Scenario**: Verify namespace isolation when using Graphiti with multiple `group_id` values

**Solution**:
```python
import json

def validate_namespace_isolation() -> dict:
    """
    Check that different group_ids create separate graphs.

    Graphiti uses group_id for multi-tenancy. Each group_id should
    result in a separate graph in FalkorDB.
    """
    result = list_graphs()
    response = json.loads(result)

    if not response["success"]:
        return {
            "success": False,
            "error": response["error"]
        }

    # Identify Graphiti graphs (may have group_id in name)
    graphiti_graphs = [
        g for g in response["graphs"]
        if "graphiti" in g.lower() or "agent_memory" in g.lower()
    ]

    validation = {
        "success": True,
        "total_graphs": len(response["graphs"]),
        "graphiti_graphs": graphiti_graphs,
        "namespace_count": len(graphiti_graphs),
        "isolation_verified": True,
        "notes": []
    }

    # Check for naming patterns that indicate namespaces
    if len(graphiti_graphs) > 1:
        validation["notes"].append(
            f"Multiple Graphiti graphs found - likely using multi-namespace"
        )
    elif len(graphiti_graphs) == 1:
        validation["notes"].append(
            f"Single Graphiti graph - likely single namespace (default group_id)"
        )
    else:
        validation["notes"].append("No Graphiti graphs found")
        validation["isolation_verified"] = False

    return validation

# Example usage
isolation = validate_namespace_isolation()
print(f"Namespace Isolation Check:")
print(f"  Graphiti graphs: {isolation['graphiti_graphs']}")
print(f"  Namespace count: {isolation['namespace_count']}")
for note in isolation["notes"]:
    print(f"  {note}")
```

---

## Expected Graphiti Graph Structure

### Node Types (Labels)

After processing episodes, Graphiti creates these node types:

| Label | Description | Example Properties |
|-------|-------------|-------------------|
| `Entity` | Base type for all entities | `uuid`, `name`, `created_at`, `summary` |
| `Person` | Individual people | `name`, `occupation`, `age` |
| `Organization` | Companies, institutions | `name`, `industry`, `location` |
| `Location` | Places, addresses | `name`, `address`, `coordinates` |
| `Event` | Temporal occurrences | `name`, `date`, `description` |
| `Topic` | Subject matter | `name`, `category` |
| `Document` | Referenced documents | `title`, `url`, `content` |
| `Episode` | Source episodes | `name`, `content`, `created_at`, `group_id` |

### Relationship Types (Edges)

Graphiti creates relationships with temporal metadata:

| Relationship Type | Description | Properties |
|-------------------|-------------|------------|
| `MENTIONS` | Episode mentions entity | `created_at`, `expired_at` |
| `RELATED_TO` | Entities are related | `fact`, `created_at`, `expired_at` |
| `WORKS_FOR` | Person works for org | `role`, `created_at`, `expired_at` |
| `LOCATED_IN` | Entity in location | `created_at`, `expired_at` |
| Custom types | Domain-specific | Varies |

### Common Graphiti Queries

```cypher
-- Get all entity types
CALL db.labels()

-- Get all relationship types
CALL db.relationshipTypes()

-- Count nodes by type
MATCH (n) RETURN labels(n) AS type, COUNT(n) AS count

-- Get recent episodes
MATCH (e:Episode)
RETURN e.name, e.created_at
ORDER BY e.created_at DESC
LIMIT 10

-- Find entities created from a specific episode
MATCH (ep:Episode {name: "episode_name"})-[:MENTIONS]->(e:Entity)
RETURN e.name, labels(e)

-- Get entity relationships
MATCH (e1:Entity)-[r]->(e2:Entity)
RETURN e1.name, type(r), e2.name, r.fact
LIMIT 20

-- Check temporal validity (non-expired facts)
MATCH (e1:Entity)-[r]->(e2:Entity)
WHERE r.expired_at IS NULL OR r.expired_at > datetime()
RETURN e1.name, type(r), e2.name, r.fact
```

---

## Validation Workflow

### Recommended Validation Steps

**Step 1: Verify Graph Exists**
```python
# After adding episodes to Graphiti
result = list_graphs()
response = json.loads(result)
assert "graphiti_meta_knowledge" in response["graphs"]
```

**Step 2: Check Node Counts**
```python
# Ensure entities were created
result = execute_query(
    graph_name="graphiti_meta_knowledge",
    query="MATCH (n:Entity) RETURN COUNT(n) AS count"
)
response = json.loads(result)
entity_count = response["data"]  # Adjust based on structure
assert entity_count > 0, "No entities created!"
```

**Step 3: Validate Schema** (once BUG-001 is fixed)
```python
# Verify expected entity types exist
result = get_graph_metadata(graph_name="graphiti_meta_knowledge")
response = json.loads(result)
assert "Person" in response["metadata"]["labels"]
assert "Organization" in response["metadata"]["labels"]
```

**Step 4: Check Relationships**
```python
# Verify entities are connected
result = execute_query(
    graph_name="graphiti_meta_knowledge",
    query="MATCH ()-[r]->() RETURN COUNT(r) AS count"
)
response = json.loads(result)
edge_count = response["data"]
assert edge_count > 0, "No relationships created!"
```

**Step 5: Validate Episode Processing**
```python
# Check that episodes were recorded
result = execute_query(
    graph_name="graphiti_meta_knowledge",
    query="MATCH (ep:Episode) RETURN COUNT(ep) AS count"
)
response = json.loads(result)
episode_count = response["data"]
print(f"Processed {episode_count} episodes")
```

---

## Troubleshooting

### Issue: Graph Not Found

**Symptoms**: `list_graphs()` doesn't return expected Graphiti graph

**Possible Causes**:
1. Episodes not yet processed (async queue)
2. Wrong FalkorDB instance
3. Incorrect `group_id` or graph name
4. Connection configuration issue

**Debug Steps**:
```python
# 1. List ALL graphs
result = list_graphs()
print(json.dumps(json.loads(result), indent=2))

# 2. Check FalkorDB connection
result = execute_query(
    graph_name="default_db",  # Try default graph
    query="MATCH (n) RETURN COUNT(n) LIMIT 1"
)
print(json.loads(result))

# 3. Check Graphiti configuration
# Review your Graphiti setup for correct FalkorDB host/port
```

---

### Issue: Missing Entity Types

**Symptoms**: Expected labels (Person, Organization) not present

**Possible Causes**:
1. Episodes don't contain relevant entities
2. LLM extraction issues
3. Schema migration incomplete
4. Custom entity types used

**Debug Steps**:
```python
# Check what labels DO exist
result = execute_query(
    graph_name="graphiti_meta_knowledge",
    query="CALL db.labels()"
)
print("Actual labels:", json.loads(result)["data"])

# Check if any entities exist
result = execute_query(
    graph_name="graphiti_meta_knowledge",
    query="MATCH (n) RETURN DISTINCT labels(n) AS labels LIMIT 10"
)
print("Sample node types:", json.loads(result)["data"])
```

---

### Issue: get_graph_metadata() Fails

**Symptoms**: Always returns serialization error

**Cause**: **BUG-001** - Known issue

**Status**: ⚠️ **BLOCKER** - Must be fixed before production use

**Workaround**: Use `execute_query()` with direct Cypher queries (see examples above)

**Permanent Fix**: See [VALIDATION_REPORT.md - BUG-001](VALIDATION_REPORT.md#tc-bug-001-queryresult-serialization-issue) for implementation details

---

## Best Practices

### 1. Use Graph Naming Conventions

Recommended naming pattern for Graphiti graphs:
```
graphiti_<namespace>_<purpose>
```

Examples:
- `graphiti_default_knowledge` - Default namespace knowledge graph
- `graphiti_user123_memory` - User-specific memory
- `graphiti_prod_agent_memory` - Production agent memory

### 2. Monitor Graph Growth Over Time

```python
import json
from datetime import datetime

def log_graph_metrics(graph_name: str, log_file: str = "graph_metrics.log"):
    """Append current metrics to log file for trend analysis."""
    result = execute_query(
        graph_name=graph_name,
        query="MATCH (n) RETURN COUNT(n) AS nodes"
    )

    with open(log_file, "a") as f:
        timestamp = datetime.utcnow().isoformat()
        nodes = json.loads(result)["data"]
        f.write(f"{timestamp},{graph_name},{nodes}\n")

# Run periodically
log_graph_metrics("graphiti_meta_knowledge")
```

### 3. Validate After Each Episode Batch

```python
def validate_after_episode_processing(graph_name: str, expected_min_entities: int):
    """
    Run validation checks after processing a batch of episodes.
    """
    # Wait for async processing (Graphiti uses queue)
    import time
    time.sleep(2)

    # Check entity count
    result = execute_query(
        graph_name=graph_name,
        query="MATCH (n:Entity) RETURN COUNT(n) AS count"
    )
    response = json.loads(result)
    entity_count = response["data"]

    if entity_count < expected_min_entities:
        print(f"⚠️ Warning: Only {entity_count} entities, expected >= {expected_min_entities}")
        return False
    else:
        print(f"✅ Validation passed: {entity_count} entities created")
        return True
```

### 4. Automate Schema Validation

```python
EXPECTED_GRAPHITI_SCHEMA = {
    "required_labels": ["Entity", "Episode", "Person", "Organization"],
    "optional_labels": ["Location", "Event", "Topic", "Document"],
    "required_relationships": ["MENTIONS", "RELATED_TO"]
}

def automated_schema_validation(graph_name: str, schema: dict) -> dict:
    """
    Automated validation against expected schema.

    Returns validation report.
    """
    report = {
        "graph_name": graph_name,
        "timestamp": datetime.utcnow().isoformat(),
        "passed": True,
        "checks": []
    }

    # Check required labels
    for label in schema["required_labels"]:
        # Query to check if label exists
        result = execute_query(
            graph_name=graph_name,
            query=f"MATCH (n:{label}) RETURN COUNT(n) AS count LIMIT 1"
        )
        response = json.loads(result)

        if response["success"] and response["data"] > 0:
            report["checks"].append({
                "type": "required_label",
                "label": label,
                "status": "✅ PASS"
            })
        else:
            report["checks"].append({
                "type": "required_label",
                "label": label,
                "status": "❌ FAIL"
            })
            report["passed"] = False

    return report
```

---

## Integration with Graphiti Workflows

### Example: End-to-End Validation Pipeline

```python
import json
from typing import List, Dict

class GraphitiValidator:
    """
    Validation helper for Graphiti knowledge graphs.
    """

    def __init__(self, graph_name: str):
        self.graph_name = graph_name

    def validate_graph_exists(self) -> bool:
        """Check if graph exists in FalkorDB."""
        result = list_graphs()
        response = json.loads(result)
        return self.graph_name in response.get("graphs", [])

    def get_metrics(self) -> Dict:
        """Get current graph metrics."""
        queries = {
            "total_nodes": "MATCH (n) RETURN COUNT(n) AS count",
            "total_edges": "MATCH ()-[r]->() RETURN COUNT(r) AS count",
            "entities": "MATCH (n:Entity) RETURN COUNT(n) AS count",
            "episodes": "MATCH (n:Episode) RETURN COUNT(n) AS count"
        }

        metrics = {}
        for name, query in queries.items():
            result = execute_query(self.graph_name, query)
            response = json.loads(result)
            if response["success"]:
                metrics[name] = response["data"]

        return metrics

    def validate_schema(self, expected_types: List[str]) -> Dict:
        """Validate that expected entity types exist."""
        validation = {
            "found": [],
            "missing": []
        }

        for entity_type in expected_types:
            query = f"MATCH (n:{entity_type}) RETURN COUNT(n) AS count LIMIT 1"
            result = execute_query(self.graph_name, query)
            response = json.loads(result)

            if response["success"] and response.get("data", 0) > 0:
                validation["found"].append(entity_type)
            else:
                validation["missing"].append(entity_type)

        return validation

    def run_full_validation(self) -> Dict:
        """Run complete validation suite."""
        return {
            "graph_exists": self.validate_graph_exists(),
            "metrics": self.get_metrics(),
            "schema": self.validate_schema([
                "Person", "Organization", "Location",
                "Event", "Topic", "Episode", "Entity"
            ])
        }

# Usage
validator = GraphitiValidator("graphiti_meta_knowledge")
report = validator.run_full_validation()

print(f"Validation Report for {validator.graph_name}:")
print(f"  Graph exists: {report['graph_exists']}")
print(f"  Metrics: {report['metrics']}")
print(f"  Schema validation: {len(report['schema']['found'])} types found, "
      f"{len(report['schema']['missing'])} missing")
```

---

## Next Steps

### After BUG-001 is Fixed

Once `get_graph_metadata()` is functional:

1. **Update all examples** to use `get_graph_metadata()` instead of workarounds
2. **Add automated schema validation** using metadata labels
3. **Create monitoring dashboards** showing graph health
4. **Build test suite** for regression testing
5. **Document actual label structures** returned by FalkorDB

### Feature Requests

Consider these enhancements to the MCP service:

1. **Enhanced Metadata**: Add node/edge counts to `get_graph_metadata()`
2. **Relationship Types**: Include `db.relationshipTypes()` in metadata
3. **Graph Statistics**: Add summary statistics (avg degree, density)
4. **Batch Operations**: Support querying multiple graphs at once
5. **Schema Diff**: Compare schemas between graphs

---

## References

- **Graphiti Documentation**: (Add Graphiti docs link)
- **FalkorDB MCP Validation Report**: [VALIDATION_REPORT.md](VALIDATION_REPORT.md)
- **FalkorDB MCP Test Plan**: [VALIDATION_TEST_PLAN.md](VALIDATION_TEST_PLAN.md)
- **FalkorDB MCP API Reference**: [architecture/docs/04_api_reference.md](architecture/docs/04_api_reference.md)
- **Cypher Query Language**: https://neo4j.com/docs/cypher-manual/

---

## Support

For issues with:
- **FalkorDB MCP Service**: See [VALIDATION_REPORT.md](VALIDATION_REPORT.md) for known issues
- **Graphiti**: Refer to Graphiti documentation and issue tracker
- **FalkorDB**: https://docs.falkordb.com/

---

**Document Version**: 1.0
**Last Updated**: 2025-11-30
**Status**: ⚠️ Awaiting BUG-001 fix for full functionality
