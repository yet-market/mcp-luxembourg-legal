"""
Test script for the MCP SPARQL server.
"""

import json
import time
import subprocess
from typing import Dict, Any, List, Optional

def run_query(query: str, format: Optional[str] = None) -> Dict[str, Any]:
    """Run a query against the SPARQL server using the direct API.
    
    Args:
        query: The SPARQL query to run.
        format: Optional result format.
        
    Returns:
        The query results.
    """
    # Import the required modules
    import sys
    sys.path.insert(0, '.')
    from sparql_server.core import SPARQLConfig, SPARQLServer, ResultFormat
    
    # Create a server instance
    config = SPARQLConfig(endpoint_url='https://data.legilux.public.lu/sparqlendpoint')
    server = SPARQLServer(config)
    
    # Run the query
    format_type = None
    if format:
        format_type = ResultFormat(format)
    
    return server.query(query, format_type)

def test_basic_query():
    """Test a basic SPARQL query."""
    print("\n=== Testing Basic Query ===")
    result = run_query("SELECT * WHERE { ?s ?p ?o } LIMIT 3")
    print(f"Query returned {len(result.get('results', {}).get('bindings', []))} results")
    print(json.dumps(result, indent=2)[:500] + "...")  # Truncate for readability

def test_formats():
    """Test different result formats."""
    print("\n=== Testing Result Formats ===")
    query = "SELECT * WHERE { ?s ?p ?o } LIMIT 2"
    
    print("\n--- JSON Format ---")
    json_result = run_query(query, "json")
    print(json.dumps(json_result, indent=2)[:500] + "...")
    
    print("\n--- Simplified Format ---")
    simplified_result = run_query(query, "simplified")
    print(json.dumps(simplified_result, indent=2))
    
    print("\n--- Tabular Format ---")
    tabular_result = run_query(query, "tabular")
    print(json.dumps(tabular_result, indent=2))

def test_caching():
    """Test query caching."""
    print("\n=== Testing Caching ===")
    
    # Import required modules
    import sys
    sys.path.insert(0, '.')
    from sparql_server.core import SPARQLConfig, SPARQLServer, ResultFormat
    
    # Create a server instance with caching enabled
    config = SPARQLConfig(
        endpoint_url='https://data.legilux.public.lu/sparqlendpoint',
        cache_enabled=True,
        cache_ttl=300,
        cache_max_size=100
    )
    server = SPARQLServer(config)
    
    # Run the first query and time it
    query = "SELECT * WHERE { ?s ?p ?o } LIMIT 5"
    print("First query (not cached):")
    start = time.time()
    server.query(query, ResultFormat.SIMPLIFIED)
    first_time = time.time() - start
    print(f"Time: {first_time:.4f}s")
    
    # Run the same query again and time it (should be cached)
    print("\nSecond query (should be cached):")
    start = time.time()
    server.query(query, ResultFormat.SIMPLIFIED)
    second_time = time.time() - start
    print(f"Time: {second_time:.4f}s")
    
    # Check cache statistics
    print("\nCache stats:")
    cache_stats = server.get_cache_stats()
    print(json.dumps(cache_stats, indent=2))
    
    # Compare timings
    if second_time < first_time:
        print(f"\nCaching is working! Second query was {first_time/second_time:.1f}x faster.")
    else:
        print("\nCaching does not seem to be working as expected.")
    
    # Clear the cache and check stats
    print("\nClearing cache...")
    server.clear_cache()
    print("Cache stats after clearing:")
    cache_stats = server.get_cache_stats()
    print(json.dumps(cache_stats, indent=2))

if __name__ == "__main__":
    print("=== MCP SPARQL Server Test ===\n")
    
    try:
        # Run all tests
        test_basic_query()
        test_formats()
        test_caching()
        
        print("\n=== All Tests Completed Successfully ===")
    except Exception as e:
        print(f"\nTest failed with error: {e}")