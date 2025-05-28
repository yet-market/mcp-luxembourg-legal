#!/usr/bin/env python3
"""
Test streamable-http transport directly (bypass nginx)

This test verifies if the FastMCP streamable-http transport works
by connecting directly to the server, bypassing nginx.
"""

import asyncio
import json
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def test_direct_streamable_http():
    """Test streamable-http transport directly on localhost:8000"""
    
    print("🧪 Testing Streamable HTTP Transport DIRECTLY")
    print("=" * 50)
    print("This bypasses nginx to test if FastMCP streamable-http works")
    print()
    
    # Test direct connection to localhost:8000 (bypass nginx)
    transport = StreamableHttpTransport(url="http://localhost:8000/mcp")
    
    try:
        async with Client(transport) as client:
            print("✅ Connected to http://localhost:8000/mcp")
            
            # List tools
            print("🛠️  Listing available tools...")
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
                print(f"✅ Luxembourg search successful!")
                
            print()
            print("🎉 STREAMABLE HTTP WORKS DIRECTLY!")
            print("   → The issue is definitely nginx configuration")
            return True
            
    except Exception as e:
        print(f"❌ Direct streamable-http failed: {e}")
        print()
        print("🔍 This means the issue is in FastMCP streamable-http transport")
        print("   → Not a nginx problem")
        return False

async def test_with_https():
    """Test with HTTPS (through nginx)"""
    
    print("\n🌐 Testing HTTPS (through nginx)")
    print("=" * 35)
    
    transport = StreamableHttpTransport(url="https://yet-mcp-legilux.site/mcp/")
    
    try:
        async with Client(transport) as client:
            tools = await client.list_tools()
            print(f"✅ HTTPS through nginx works!")
            return True
    except Exception as e:
        print(f"❌ HTTPS through nginx failed: {e}")
        return False

async def main():
    """Main test function"""
    
    print("🎯 DIAGNOSIS: Streamable HTTP Transport Test")
    print("=" * 45)
    print("This will determine if the issue is nginx or FastMCP")
    print()
    
    # Test 1: Direct connection (bypass nginx)
    direct_works = await test_direct_streamable_http()
    
    # Test 2: HTTPS through nginx
    nginx_works = await test_with_https()
    
    print("\n" + "=" * 50)
    print("🎯 DIAGNOSIS RESULTS:")
    print("=" * 50)
    
    if direct_works and not nginx_works:
        print("✅ Direct HTTP works")
        print("❌ HTTPS through nginx fails")
        print("🎯 CONCLUSION: nginx configuration problem")
    elif not direct_works and not nginx_works:
        print("❌ Direct HTTP fails") 
        print("❌ HTTPS through nginx fails")
        print("🎯 CONCLUSION: FastMCP streamable-http bug")
    elif direct_works and nginx_works:
        print("✅ Direct HTTP works")
        print("✅ HTTPS through nginx works") 
        print("🎯 CONCLUSION: Everything is working!")
    else:
        print("❌ Direct HTTP fails")
        print("✅ HTTPS through nginx works")
        print("🎯 CONCLUSION: Unexpected result")

if __name__ == "__main__":
    asyncio.run(main())