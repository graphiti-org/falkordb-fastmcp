# FalkorDB MCP Service - API Validation Test Plan

## Overview

This document outlines a comprehensive test plan for validating the FalkorDB MCP service, focusing on the two core discovery operations: `list_graphs()` and `get_graph_metadata()`.

## Test Environment

- **Service**: FalkorDB FastMCP Server (Python implementation)
- **Protocol**: Model Context Protocol (MCP)
- **Database**: FalkorDB graph database
- **Test Approach**: Direct MCP tool invocation via `mcp__falkordb__*` functions

## API Under Test

### API 1: `list_graphs()`

**Purpose**: List all available graphs in the FalkorDB instance

**Request Parameters**: None

**Expected Success Response**:
```json
{
  "success": true,
  "graphs": ["graph1", "graph2", ...],
  "count": <number>,
  "timestamp": "ISO 8601 timestamp"
}
```

**Expected Error Response**:
```json
{
  "success": false,
  "error": "error message"
}
```

### API 2: `get_graph_metadata(graph_name: str)`

**Purpose**: Get metadata and labels for a specific FalkorDB graph

**Request Parameters**:
- `graph_name` (string, required): Name of the graph

**Expected Success Response**:
```json
{
  "success": true,
  "metadata": {
    "name": "graph_name",
    "labels": [<query_result>]
  },
  "timestamp": "ISO 8601 timestamp"
}
```

**Expected Error Response**:
```json
{
  "success": false,
  "error": "error message",
  "graphName": "requested_graph_name"
}
```

---

## Test Cases

### Test Suite 1: `list_graphs()` - Positive Tests

#### TC-LG-P001: List graphs with active database
**Preconditions**: FalkorDB instance is running and accessible
**Test Steps**:
1. Call `mcp__falkordb__list_graphs()`
2. Parse JSON response
**Expected Results**:
- ✅ Response contains `"success": true`
- ✅ Response contains `"graphs"` array (may be empty)
- ✅ Response contains `"count"` field
- ✅ `count` value matches length of `graphs` array
- ✅ Response contains `"timestamp"` in ISO 8601 format
- ✅ All graph names are strings
**Priority**: P0 - Critical

#### TC-LG-P002: Verify graph count accuracy
**Preconditions**: Known number of graphs exist in database
**Test Steps**:
1. Call `mcp__falkordb__list_graphs()`
2. Verify count matches expected number
**Expected Results**:
- ✅ `count` field equals number of graphs in `graphs` array
- ✅ Each graph name appears exactly once (no duplicates)
**Priority**: P0 - Critical

#### TC-LG-P003: Timestamp format validation
**Preconditions**: FalkorDB instance is running
**Test Steps**:
1. Call `mcp__falkordb__list_graphs()`
2. Extract timestamp field
3. Validate ISO 8601 format (e.g., "2025-11-29T12:34:56.123456")
**Expected Results**:
- ✅ Timestamp matches pattern `YYYY-MM-DDTHH:MM:SS.microseconds`
- ✅ Timestamp represents current UTC time (within reasonable delta)
**Priority**: P1 - High

#### TC-LG-P004: Empty graph list handling
**Preconditions**: FalkorDB instance running with no graphs
**Test Steps**:
1. Call `mcp__falkordb__list_graphs()`
**Expected Results**:
- ✅ Response contains `"success": true`
- ✅ `graphs` array is empty `[]`
- ✅ `count` is `0`
- ✅ No error field present
**Priority**: P1 - High

### Test Suite 2: `list_graphs()` - Negative Tests

#### TC-LG-N001: Database connection failure
**Preconditions**: FalkorDB instance is not running or unreachable
**Test Steps**:
1. Stop FalkorDB service (if running)
2. Call `mcp__falkordb__list_graphs()`
**Expected Results**:
- ✅ Response contains `"success": false`
- ✅ Response contains `"error"` field with descriptive message
- ✅ No `graphs` or `count` fields present (or they're null)
**Priority**: P0 - Critical

#### TC-LG-N002: Response structure validation
**Preconditions**: FalkorDB instance is running
**Test Steps**:
1. Call `mcp__falkordb__list_graphs()`
2. Validate all required fields are present
**Expected Results**:
- ✅ Response is valid JSON
- ✅ Response contains exactly the documented fields
- ✅ No unexpected fields in response
**Priority**: P1 - High

---

### Test Suite 3: `get_graph_metadata()` - Positive Tests

#### TC-GM-P001: Get metadata for existing graph
**Preconditions**: At least one graph exists in FalkorDB
**Test Steps**:
1. Call `mcp__falkordb__list_graphs()` to get graph name
2. Call `mcp__falkordb__get_graph_metadata(graph_name=<first_graph>)`
3. Parse JSON response
**Expected Results**:
- ✅ Response contains `"success": true`
- ✅ Response contains `"metadata"` object
- ✅ `metadata.name` matches requested graph name
- ✅ `metadata.labels` contains label information (structure TBD based on db.labels() output)
- ✅ Response contains `"timestamp"` in ISO 8601 format
**Priority**: P0 - Critical

#### TC-GM-P002: Get metadata for multiple graphs
**Preconditions**: Multiple graphs exist in FalkorDB
**Test Steps**:
1. Call `mcp__falkordb__list_graphs()` to get all graph names
2. For each graph name:
   - Call `mcp__falkordb__get_graph_metadata(graph_name=<name>)`
   - Verify response structure
**Expected Results**:
- ✅ All requests return `"success": true`
- ✅ Each `metadata.name` matches its requested graph
- ✅ Each response has valid timestamp
- ✅ All responses have valid structure
**Priority**: P0 - Critical

#### TC-GM-P003: Graphiti graph schema validation
**Preconditions**: Graphiti-created graph exists (e.g., "graphiti_meta_knowledge")
**Test Steps**:
1. Call `mcp__falkordb__get_graph_metadata(graph_name="graphiti_meta_knowledge")`
2. Examine `metadata.labels` for expected entity types
**Expected Results**:
- ✅ Response contains `"success": true`
- ✅ Labels include expected Graphiti entity types:
  - Entity base types (Person, Organization, Location, Event, Document, Topic, etc.)
  - Episode tracking nodes
  - Relationship types
**Priority**: P1 - High (Graphiti-specific)

#### TC-GM-P004: Timestamp consistency
**Preconditions**: FalkorDB instance is running
**Test Steps**:
1. Record current time
2. Call `mcp__falkordb__get_graph_metadata(graph_name=<valid_graph>)`
3. Extract timestamp from response
**Expected Results**:
- ✅ Timestamp is within 5 seconds of test execution time
- ✅ Timestamp format is ISO 8601
**Priority**: P2 - Medium

### Test Suite 4: `get_graph_metadata()` - Negative Tests

#### TC-GM-N001: Non-existent graph name
**Preconditions**: FalkorDB instance is running
**Test Steps**:
1. Call `mcp__falkordb__get_graph_metadata(graph_name="NONEXISTENT_GRAPH_12345")`
**Expected Results**:
- ✅ Response contains `"success": false`
- ✅ Response contains `"error"` field with descriptive message
- ✅ Response contains `"graphName"` field with the requested name
- ✅ No `metadata` field present (or it's null)
**Priority**: P0 - Critical

#### TC-GM-N002: Empty graph name
**Preconditions**: FalkorDB instance is running
**Test Steps**:
1. Call `mcp__falkordb__get_graph_metadata(graph_name="")`
**Expected Results**:
- ✅ Response contains `"success": false`
- ✅ Error message indicates invalid/missing graph name
**Priority**: P1 - High

#### TC-GM-N003: Special characters in graph name
**Preconditions**: FalkorDB instance is running
**Test Steps**:
1. Call `mcp__falkordb__get_graph_metadata(graph_name="'; DROP TABLE graphs;--")`
**Expected Results**:
- ✅ Response handles input safely (no injection)
- ✅ Response contains `"success": false`
- ✅ No database corruption or errors
**Priority**: P0 - Critical (Security)

#### TC-GM-N004: Database connection failure during metadata retrieval
**Preconditions**: FalkorDB connection can be disrupted
**Test Steps**:
1. Initiate `mcp__falkordb__get_graph_metadata(graph_name=<valid_graph>)`
2. (If possible) Interrupt database connection
**Expected Results**:
- ✅ Response contains `"success": false`
- ✅ Error message is descriptive
- ✅ No unhandled exceptions
**Priority**: P1 - High

---

### Test Suite 5: Integration & Cross-functional Tests

#### TC-INT-001: Sequential workflow - Discovery to metadata
**Preconditions**: FalkorDB instance with multiple graphs
**Test Steps**:
1. Call `mcp__falkordb__list_graphs()`
2. For each graph in response:
   - Call `mcp__falkordb__get_graph_metadata(graph_name=<graph>)`
   - Verify metadata retrieval succeeds
**Expected Results**:
- ✅ All graphs from `list_graphs()` have retrievable metadata
- ✅ No graphs fail metadata retrieval
- ✅ All responses maintain consistent structure
**Priority**: P0 - Critical

#### TC-INT-002: Response time validation
**Preconditions**: FalkorDB instance is running
**Test Steps**:
1. Measure response time for `list_graphs()`
2. Measure response time for `get_graph_metadata()` on each graph
**Expected Results**:
- ✅ `list_graphs()` completes in < 2 seconds
- ✅ `get_graph_metadata()` completes in < 2 seconds per graph
- ✅ No timeouts occur
**Priority**: P2 - Medium

#### TC-INT-003: Concurrent requests handling
**Preconditions**: FalkorDB instance is running
**Test Steps**:
1. Make multiple simultaneous calls to `list_graphs()`
2. Make multiple simultaneous calls to `get_graph_metadata()` with different graph names
**Expected Results**:
- ✅ All requests complete successfully
- ✅ No race conditions or errors
- ✅ Singleton service pattern handles concurrency correctly
**Priority**: P2 - Medium

---

### Test Suite 6: Known Issues / Bug Validation

#### TC-BUG-001: QueryResult serialization issue in get_graph_metadata()
**Issue**: `metadata.labels` contains non-JSON-serializable QueryResult object
**Current Status**: Known bug discovered during initial testing
**Test Steps**:
1. Call `mcp__falkordb__get_graph_metadata(graph_name=<any_valid_graph>)`
2. Attempt to parse response as JSON
**Current Behavior**:
- ❌ Error: "Object of type QueryResult is not JSON serializable"
**Expected Behavior** (after fix):
- ✅ `metadata.labels` contains serialized label data (list of strings or structured objects)
- ✅ Response is valid JSON
**Priority**: P0 - Critical (BLOCKER)
**Code Location**: [service.py:106-111](src/falkordb_mcp/service.py#L106-L111)

**Root Cause**:
```python
# Line 106 in service.py
labels_result = graph.query("CALL db.labels()")

# Line 110 - QueryResult object is not JSON serializable
return {
    "name": graph_name,
    "labels": labels_result,  # ← Problem: QueryResult object
}
```

**Suggested Fix**:
```python
# Need to extract data from QueryResult
labels_result = graph.query("CALL db.labels()")
labels_list = [record[0] for record in labels_result.result_set]

return {
    "name": graph_name,
    "labels": labels_list,  # ← Returns list of label strings
}
```

---

## Test Execution Strategy

### Phase 1: Smoke Tests (5 min)
- TC-LG-P001: List graphs with active database
- TC-GM-P001: Get metadata for existing graph
- **Goal**: Verify basic connectivity and functionality

### Phase 2: Positive Path Tests (10 min)
- Execute all P0 positive tests
- Document actual responses
- Build graph inventory

### Phase 3: Negative Path Tests (10 min)
- Execute all P0 negative tests
- Verify error handling
- Test edge cases

### Phase 4: Bug Validation & Fixes (15 min)
- TC-BUG-001: Confirm QueryResult serialization issue
- Implement fix if needed
- Re-test affected scenarios

### Phase 5: Documentation (10 min)
- Create validation report
- Document discovered graphs
- Create Graphiti integration guide

---

## Success Criteria

### Must Have (P0)
- ✅ `list_graphs()` returns valid JSON with correct structure
- ✅ `get_graph_metadata()` returns valid JSON with correct structure
- ✅ Both APIs handle errors gracefully
- ✅ QueryResult serialization bug is identified and documented
- ✅ All discovered graphs are catalogued

### Should Have (P1)
- ✅ Timestamp validation passes for all responses
- ✅ Empty/missing parameter handling works correctly
- ✅ Graphiti graph schemas are documented
- ✅ Integration workflow (list → metadata) validated

### Nice to Have (P2)
- ✅ Performance benchmarks documented
- ✅ Concurrency handling verified
- ✅ Security tests (injection) pass

---

## Test Data Requirements

### Graphs Expected in Test Environment
Based on initial discovery, the following graphs exist:
- `default_db`
- `tutorials`
- `main`
- `graphiti_meta_knowledge` ← Graphiti graph
- `agent_memory_decision_tree_2025` ← Graphiti graph
- `research-2025`
- `mcp-validation-test`
- `repository_analyzer_patterns`
- `claude_agent_sdk_patterns`
- `claude_agent_sdk`

### Test Scenarios by Graph Type
- **Standard graphs**: `default_db`, `tutorials`, `main`
- **Graphiti graphs**: `graphiti_meta_knowledge`, `agent_memory_decision_tree_2025`
- **Test graphs**: `mcp-validation-test`

---

## Defect Tracking

| ID | Severity | Status | Description | Location |
|----|----------|--------|-------------|----------|
| BUG-001 | Critical | Open | QueryResult not JSON serializable in `get_graph_metadata()` | [service.py:106-111](src/falkordb_mcp/service.py#L106-L111) |

---

## References

- **TypeScript API Reference**: `/home/donbr/graphiti-org/FalkorDB-MCPServer/architecture/docs/04_api_reference.md`
- **Python API Reference**: `/home/donbr/graphiti-org/falkordb-fastmcp/architecture/docs/04_api_reference.md`
- **Service Implementation**: [src/falkordb_mcp/service.py](src/falkordb_mcp/service.py)
- **MCP Tool Definitions**: [src/falkordb_mcp/server.py](src/falkordb_mcp/server.py)
