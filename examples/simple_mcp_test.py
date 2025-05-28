#!/usr/bin/env python3
"""
Simple MCP Test - Just test the connection
"""

import asyncio
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp import Client

async def test_mcp():
    """Simple MCP test"""
    print("🔌 Testing MCP Connection...")
    
    try:
        transport = StreamableHttpTransport(url="https://yet-mcp-legilux.site/mcp/")
        
        async with Client(transport) as client:
            print("✅ Connected!")
            
            # List tools
            tools = await client.list_tools()
            print(f"🛠️  Tools: {[tool.name for tool in tools]}")
            
            # Test search
            result = await client.call_tool(
                "search_luxembourg_documents",
                {"keywords": "tax", "limit": 1, "include_content": False}
            )
            
            print(f"📊 Result type: {type(result)}")
            print(f"📊 Result: {result}")
            
            if hasattr(result, 'content'):
                print(f"📄 Content type: {type(result.content)}")
                print(f"📄 Content: {result.content}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp())