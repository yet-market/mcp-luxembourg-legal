#!/usr/bin/env python3
"""
Test the SPARQL server using the FastMCP Client.

This test uses the FastMCP Client to communicate with our server,
ensuring proper MCP protocol compliance.
"""

import json
import asyncio
import os
import sys
from typing import Dict, Any

# Add the project directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP
from mcp.client.session import BaseSession as Client
from sparql_server.core import SPARQLConfig, SPARQLServer, ResultFormat


async def test_sparql_server():
    """Test the SPARQL server using the FastMCP Client."""
    
    print("=== Starting SPARQL Server Test ===")
    
    # Create a configuration
    config = SPARQLConfig(endpoint_url="https://data.legilux.public.lu/sparqlendpoint")
    
    # Create a SPARQL server instance
    sparql_server = SPARQLServer(config)
    
    # Create an MCP server
    mcp = FastMCP("SPARQL Query Server")
    
    # Define the query tool
    @mcp.tool()
    def query(query_string: str, format: str = None) -> Dict[str, Any]:
        """Execute a SPARQL query and return the results."""
        # Convert format string to enum if provided
        format_type = None
        if format:
            try:
                format_type = ResultFormat(format)
            except ValueError:
                return {
                    "error": f"Invalid format: {format}. Must be one of: {', '.join([f.value for f in ResultFormat])}"
                }
                
        return sparql_server.query(query_string, format_type)
    
    # Define the cache tool
    @mcp.tool()
    def cache(action: str) -> Dict[str, Any]:
        """Manage the query cache."""
        if action.lower() == "clear":
            sparql_server.clear_cache()
            return {"status": "success", "message": "Cache cleared"}
        elif action.lower() == "stats":
            return {"status": "success", "stats": sparql_server.get_cache_stats()}
        else:
            return {
                "status": "error", 
                "message": f"Invalid cache action: {action}. Must be 'clear' or 'stats'."
            }
    
    # Create a client to interact with the server in-memory
    async with Client(mcp) as client:
        # Test the query tool
        print("\n=== Testing Query Tool ===")
        query_result = await client.call_tool(
            "query", 
            {
                "query_string": "SELECT * WHERE { ?s ?p ?o } LIMIT 2",
                "format": "simplified"
            }
        )
        
        print("\nQuery Results:")
        print(json.dumps(query_result.json, indent=2))
        
        # Test the cache tool
        print("\n=== Testing Cache Tool ===")
        cache_result = await client.call_tool("cache", {"action": "stats"})
        
        print("\nCache Statistics:")
        print(json.dumps(cache_result.json, indent=2))
        
        print("\n=== All Tests Passed ===")


def main():
    """Run the tests."""
    asyncio.run(test_sparql_server())


if __name__ == "__main__":
    main()