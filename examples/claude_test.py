#!/usr/bin/env python3
"""
Test MCP server with official MCP SDK (like Claude uses)
"""

import asyncio
import os
from dotenv import load_dotenv
from mcp.client.session import ClientSession

load_dotenv()

async def test_with_mcp_sdk():
    """Test using official MCP SDK like Claude would"""
    
    print("🤖 Testing with official MCP SDK (Claude-style)")
    print("=" * 50)
    
    try:
        # Test SSE transport like Claude might use
        transport = SseClientTransport("https://yet-mcp-legilux.site/sse")
        
        async with ClientSession(transport) as session:
            # Initialize
            print("🤝 Initializing MCP session...")
            await session.initialize()
            
            # List tools
            print("🛠️  Listing tools...")
            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]
            print(f"✅ Available tools: {tool_names}")
            
            # Test Luxembourg search
            if "search_luxembourg_documents" in tool_names:
                print("🇱🇺 Testing Luxembourg search...")
                result = await session.call_tool(
                    "search_luxembourg_documents",
                    {
                        "keywords": "taxe",
                        "limit": 1,
                        "include_content": False
                    }
                )
                print(f"✅ Search successful!")
                return True
            else:
                print("⚠️  Luxembourg tool not found")
                return False
                
    except Exception as e:
        print(f"❌ MCP SDK test failed: {e}")
        return False

async def test_streamable_http_sdk():
    """Test streamable HTTP with MCP SDK"""
    
    print("\n🌐 Testing Streamable HTTP with MCP SDK")
    print("=" * 45)
    
    try:
        # Import streamable HTTP transport from MCP SDK
        from mcp.client.streamable_http import StreamableHttpTransport
        
        transport = StreamableHttpTransport("https://yet-mcp-legilux.site/mcp/")
        
        async with ClientSession(transport) as session:
            print("🤝 Initializing streamable HTTP session...")
            await session.initialize()
            
            print("🛠️  Listing tools...")
            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]
            print(f"✅ Available tools: {tool_names}")
            
            return True
            
    except ImportError as e:
        print(f"⚠️  StreamableHttpTransport not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Streamable HTTP test failed: {e}")
        return False

async def main():
    """Main test function"""
    
    print("Testing MCP server like Claude API would...")
    
    # Test both transports
    sse_works = await test_with_mcp_sdk()
    http_works = await test_streamable_http_sdk()
    
    if sse_works or http_works:
        print("\n✅ At least one transport works - server is functional!")
    else:
        print("\n❌ Both transports failed - server has issues")

if __name__ == "__main__":
    asyncio.run(main())