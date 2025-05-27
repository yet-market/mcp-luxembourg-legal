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

from fastmcp import FastMCP
from fastmcp.client import Client, PythonStdioTransport
from luxembourg_legal_server.core import SPARQLConfig, SPARQLServer, ResultFormat


async def test_in_memory_client():
    """Test the SPARQL server using in-memory FastMCP Client."""
    
    print("=== Testing In-Memory FastMCP Client ===")
    
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
            return {"status": "error", "message": f"Invalid cache action: {action}"}
    
    # Test client connection
    async with Client(mcp) as client:
        print("✓ Client connected successfully")
        
        # List tools
        tools = await client.list_tools()
        print(f"✓ Available tools: {[tool.name for tool in tools]}")
        
        # Test query tool
        query_result = await client.call_tool("query", {
            "query_string": "SELECT * WHERE { ?s ?p ?o } LIMIT 2",
            "format": "simplified"
        })
        
        # Parse the text content from the result
        result_text = query_result[0].text
        result_data = json.loads(result_text)
        
        print(f"✓ Query executed successfully: {'error' not in result_data}")
        print(f"  Results count: {len(result_data.get('results', []))}")
        
        # Test cache tool
        cache_result = await client.call_tool("cache", {"action": "stats"})
        cache_text = cache_result[0].text
        cache_data = json.loads(cache_text)
        
        print(f"✓ Cache stats retrieved: {cache_data.get('status') == 'success'}")


async def test_stdio_client():
    """Test the SPARQL server using stdio transport (production mode)."""
    
    print("\n=== Testing Stdio Transport Client ===")
    
    # Create stdio transport
    transport = PythonStdioTransport(
        script_path="server.py",
        args=["--endpoint", "https://data.legilux.public.lu/sparqlendpoint", "--format", "simplified"]
    )
    
    async with Client(transport) as client:
        print("✓ Client connected via stdio transport")
        
        # List tools
        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]
        print(f"✓ Available tools: {tool_names}")
        
        # Test Luxembourg search tool
        if "search_luxembourg_documents" in tool_names:
            search_result = await client.call_tool("search_luxembourg_documents", {
                "keywords": "taxe",
                "limit": 1,
                "include_content": False
            })
            
            result_text = search_result[0].text
            result_data = json.loads(result_text)
            
            print(f"✓ Luxembourg search successful: {'error' not in result_data}")
            print(f"  Documents found: {len(result_data.get('results', []))}")
        
        # Test basic query tool
        query_result = await client.call_tool("query", {
            "query_string": "SELECT * WHERE { ?s ?p ?o } LIMIT 1",
            "format": "simplified"
        })
        
        result_text = query_result[0].text
        result_data = json.loads(result_text)
        
        print(f"✓ Basic query successful: {'error' not in result_data}")
        print(f"  Results returned: {len(result_data.get('results', []))}")
        
        # Test cache management
        cache_result = await client.call_tool("cache", {"action": "clear"})
        cache_text = cache_result[0].text
        cache_data = json.loads(cache_text)
        
        print(f"✓ Cache cleared: {cache_data.get('status') == 'success'}")


async def main():
    """Run all tests."""
    print("=== FastMCP SPARQL Server Tests ===")
    
    try:
        await test_in_memory_client()
        await test_stdio_client()
        print("\n=== All Tests Passed Successfully ===")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())