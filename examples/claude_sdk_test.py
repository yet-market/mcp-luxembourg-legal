#!/usr/bin/env python3
"""
Test MCP server with official MCP SDK using Streamable HTTP (like Claude API uses)
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_mcp_sdk_streamable_http():
    """Test using official MCP SDK with streamable HTTP like Claude API"""
    
    print("🤖 Testing with official MCP SDK - Streamable HTTP")
    print("=" * 55)
    
    try:
        # Use the exact pattern from FastMCP docs
        from fastmcp import Client
        
        # The Client automatically uses StreamableHttpTransport for HTTP URLs
        client = Client("https://yet-mcp-legilux.site/mcp")
        
        async with client:
            print("🤝 Initializing MCP session...")
            
            # List tools
            print("🛠️  Listing tools...")
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            print(f"✅ Available tools: {tool_names}")
            
            # Test Luxembourg search if available
            if "search_luxembourg_documents" in tool_names:
                print("🇱🇺 Testing Luxembourg legal search...")
                result = await client.call_tool(
                    "search_luxembourg_documents",
                    {
                        "keywords": "taxe",
                        "limit": 1,
                        "include_content": False
                    }
                )
                print(f"✅ Search successful! Got results.")
                return True
            else:
                print("⚠️  Luxembourg search tool not found")
                return False
                
    except Exception as e:
        print(f"❌ MCP SDK test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_with_explicit_transport():
    """Test with explicit StreamableHttpTransport"""
    
    print("\n🌐 Testing with explicit StreamableHttpTransport")
    print("=" * 50)
    
    try:
        from fastmcp import Client
        from fastmcp.client.transports import StreamableHttpTransport
        
        # Explicit transport instantiation
        transport = StreamableHttpTransport(url="https://yet-mcp-legilux.site/mcp")
        client = Client(transport)
        
        async with client:
            print("🤝 Connected with explicit transport...")
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            print(f"✅ Available tools: {tool_names}")
            return True
            
    except Exception as e:
        print(f"❌ Explicit transport test failed: {e}")
        return False

async def main():
    """Main test function"""
    
    print("Testing MCP server with official FastMCP Client (Claude API style)...")
    print("This tests if the Accept header issue is FastMCP-specific or universal.\n")
    
    # Test both approaches
    auto_works = await test_mcp_sdk_streamable_http()
    explicit_works = await test_with_explicit_transport()
    
    print(f"\n🎯 RESULTS:")
    print(f"   Auto-inferred transport: {'✅ WORKS' if auto_works else '❌ FAILED'}")
    print(f"   Explicit transport: {'✅ WORKS' if explicit_works else '❌ FAILED'}")
    
    if auto_works or explicit_works:
        print(f"\n✅ SUCCESS: MCP server works with official FastMCP Client!")
        print(f"   This means the server is functional and the issue might be client-specific.")
    else:
        print(f"\n❌ FAILED: Server has fundamental issues with streamable HTTP transport.")
        print(f"   The Accept header bug affects both custom and official clients.")

if __name__ == "__main__":
    asyncio.run(main())