#!/usr/bin/env python3
"""
Basic test for the SPARQL server functionality.
"""

import sys
sys.path.insert(0, '.')
from sparql_server.core import SPARQLConfig, SPARQLServer, ResultFormat

def test_sparql_server():
    """Test the basic SPARQL server functionality directly."""
    print("Testing SPARQL server directly...")
    
    # Create configuration
    config = SPARQLConfig(endpoint_url='https://data.legilux.public.lu/sparqlendpoint')
    
    # Initialize server
    server = SPARQLServer(config)
    
    # Execute a query
    print("Executing query...")
    result = server.query('SELECT * WHERE { ?s ?p ?o } LIMIT 2', ResultFormat.SIMPLIFIED)
    
    # Print results
    import json
    print("\nQuery results:")
    print(json.dumps(result, indent=2))
    
    # Check cache
    print("\nCache statistics:")
    print(json.dumps(server.get_cache_stats(), indent=2))
    
    print("\nServer test completed successfully!")

if __name__ == "__main__":
    test_sparql_server()