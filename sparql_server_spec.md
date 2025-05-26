# SPARQL-Enabled MCP Server Specification

## Overview
This specification outlines the development of an enhanced SPARQL-enabled MCP server that provides flexible querying capabilities against any SPARQL endpoint, with result formatting options and caching. The system will follow best practices with no hardcoded values, allowing it to be used with any SPARQL endpoint.

## Requirements

### 1. Core Functionality
- Connect to any user-specified SPARQL endpoint URL
- Execute SPARQL queries and return results
- Support all standard SPARQL query types (SELECT, ASK, CONSTRUCT, DESCRIBE)
- Handle errors gracefully with informative error messages

### 2. Result Formatting Options
- Format query results into consistent JSON structures
- Support configurable output formats (JSON, simplified JSON, tabular)
- Normalize results across different SPARQL endpoint implementations
- Allow users to specify desired output format

### 3. Query Caching
- Cache query results to improve performance
- Implement configurable cache expiration times
- Allow cache size limits to be configured
- Support cache invalidation mechanisms
- Make caching optional and configurable

### 4. Configuration
- All settings should be configurable via parameters
- No hardcoded values for endpoints, timeouts, or other settings
- Support configuration via command-line arguments
- Support environment variable configuration

## Technical Design

### Class Structure

#### 1. `SPARQLServer` Class
- **Purpose**: Core class for connecting to and querying SPARQL endpoints
- **Properties**:
  - `endpoint_url`: URL of the SPARQL endpoint
  - `default_format`: Default return format
  - `cache_enabled`: Boolean to enable/disable caching
  - `cache_ttl`: Time-to-live for cache entries
  - `cache_max_size`: Maximum number of cache entries
- **Methods**:
  - `query()`: Execute a SPARQL query
  - `query_with_params()`: Execute a parameterized SPARQL query

#### 2. `ResultFormatter` Class
- **Purpose**: Handle formatting of query results
- **Methods**:
  - `format_results()`: Format results according to specified format
  - `to_json()`: Convert to standard JSON
  - `to_simplified_json()`: Convert to simplified JSON
  - `to_tabular()`: Convert to tabular format

#### 3. `QueryCache` Class
- **Purpose**: Handle caching of query results
- **Properties**:
  - `ttl`: Time-to-live for cache entries
  - `max_size`: Maximum cache size
- **Methods**:
  - `get()`: Get cached result for a query
  - `set()`: Store result for a query
  - `invalidate()`: Invalidate specific cache entries
  - `clear()`: Clear entire cache

### Implementation Plan

#### Phase 1: Core SPARQL Server Enhancement
1. Update `SPARQLServer` class to accept all configuration parameters
2. Implement support for all SPARQL query types
3. Improve error handling and reporting

#### Phase 2: Result Formatting Implementation
1. Create `ResultFormatter` class
2. Implement standard formatting methods
3. Add format selection to query methods

#### Phase 3: Caching Implementation
1. Create `QueryCache` class
2. Integrate caching with query execution
3. Implement cache management functions

#### Phase 4: CLI and Configuration
1. Enhance CLI argument parsing
2. Add environment variable support
3. Implement configuration validation

## Configuration Parameters

### SPARQL Server Configuration
- `endpoint_url`: SPARQL endpoint URL (required)
- `request_timeout`: Timeout for SPARQL requests in seconds (default: 30)
- `default_format`: Default result format (default: "json")
- `max_results`: Maximum number of results to return (default: 1000)

### Cache Configuration
- `cache_enabled`: Enable caching (default: True)
- `cache_ttl`: Cache time-to-live in seconds (default: 300)
- `cache_max_size`: Maximum cache size (default: 100)
- `cache_strategy`: Cache replacement strategy (default: "lru")

### Result Formatting Configuration
- `format`: Output format (options: "json", "simplified", "tabular")
- `pretty_print`: Pretty print JSON output (default: False)
- `include_metadata`: Include query metadata in results (default: True)

## CLI Interface
```
mcp-server-sparql --endpoint <endpoint_url> [options]

Options:
  --endpoint URL         SPARQL endpoint URL (required)
  --timeout SECONDS      Request timeout in seconds
  --format FORMAT        Result format (json, simplified, tabular)
  --cache-enabled        Enable caching (default: true)
  --cache-ttl SECONDS    Cache time-to-live in seconds
  --cache-max-size SIZE  Maximum cache size
  --pretty-print         Pretty print JSON output
```

## Environment Variables
- `SPARQL_ENDPOINT`: SPARQL endpoint URL
- `SPARQL_TIMEOUT`: Request timeout
- `SPARQL_FORMAT`: Default result format
- `SPARQL_CACHE_ENABLED`: Enable caching
- `SPARQL_CACHE_TTL`: Cache time-to-live
- `SPARQL_CACHE_MAX_SIZE`: Maximum cache size
- `SPARQL_PRETTY_PRINT`: Pretty print JSON output

## Error Handling
- Network errors: Return clear error with HTTP status and endpoint details
- Query syntax errors: Return error with query excerpt and position
- Timeout errors: Return error with timeout value and query excerpt
- Authentication errors: Return clear authentication failure message
- Caching errors: Log error but continue with uncached query

## Development Timeline
- Phase 1 (Core Enhancement): 2 days
- Phase 2 (Result Formatting): 2 days
- Phase 3 (Caching): 2 days
- Phase 4 (CLI and Configuration): 1 day
- Testing and Documentation: 1 day

Total estimated time: 8 days