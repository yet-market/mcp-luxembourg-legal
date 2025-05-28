#!/usr/bin/env python3
"""
OpenAI + Luxembourg Legal MCP Server Test

This script tests the Luxembourg Legal MCP server by:
1. Directly calling the MCP server
2. Using the results with OpenAI for intelligent responses

Requires OPENAI_API_KEY in .env file.
"""

import os
import json
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp import FastMCPClient

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# MCP Server Configuration - Streamable HTTP Transport
MCP_SERVER_URL = "https://yet-mcp-legilux.site/mcp"

async def test_fastmcp_client():
    """Test using FastMCP's official StreamableHttpTransport"""
    
    print("🔌 Testing FastMCP StreamableHttpTransport")
    print("=" * 45)
    
    try:
        # Create FastMCP client with StreamableHttpTransport
        transport = StreamableHttpTransport(url=MCP_SERVER_URL)
        
        async with FastMCPClient(transport) as client:
            # Test server info
            print("🤝 Getting server info...")
            server_info = await client.get_server_info()
            print(f"✅ Server: {server_info.name} v{server_info.version}")
            
            # Test tools
            print("🛠️  Listing available tools...")
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            print(f"✅ Available tools: {tool_names}")
            
            # Test Luxembourg legal search
            if "search_luxembourg_documents" in tool_names:
                print("🇱🇺 Testing Luxembourg legal search...")
                result = await client.call_tool(
                    "search_luxembourg_documents",
                    {
                        "keywords": "taxe",
                        "limit": 2,
                        "include_content": False
                    }
                )
                
                print(f"✅ Search successful! Found results.")
                return result
            else:
                print("⚠️  Luxembourg search tool not found")
                return None
                
    except Exception as e:
        print(f"❌ FastMCP client failed: {e}")
        return None

async def search_luxembourg_documents(keywords: str, limit: int = 3):
    """Search Luxembourg documents via FastMCP client"""
    
    try:
        transport = StreamableHttpTransport(url=MCP_SERVER_URL)
        
        async with FastMCPClient(transport) as client:
            result = await client.call_tool(
                "search_luxembourg_documents",
                {
                    "keywords": keywords,
                    "limit": limit,
                    "include_content": False
                }
            )
            
            # result is already parsed by FastMCP client
            return json.dumps(result, ensure_ascii=False)
            
    except Exception as e:
        return f"Error: {e}"

async def test_luxembourg_legal_with_openai():
    """Test Luxembourg legal search with OpenAI analysis"""
    
    print("🇱🇺 Testing Luxembourg Legal MCP + OpenAI Integration")
    print("=" * 55)
    
    # Test queries in French (Luxembourg documents are in French)
    test_queries = [
        ("taxe", "Recherche des documents sur la taxe"),
        ("société", "Trouve des informations sur les sociétés"),
        ("environnement", "Lois sur l'environnement"),
        ("travail", "Règlements sur le travail")
    ]
    
    for i, (keyword, description) in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {description}")
        print("-" * 30)
        
        try:
            # Step 1: Search Luxembourg documents
            print(f"🔍 Searching for '{keyword}'...")
            documents = await search_luxembourg_documents(keyword, limit=2)
            
            if "Error:" in documents:
                print(f"❌ MCP Error: {documents}")
                continue
                
            print(f"✅ Found documents: {len(documents.split('title')) - 1 if 'title' in documents else 0}")
            
            # Step 2: Use OpenAI to analyze the results
            print("🤖 Analyzing with OpenAI...")
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es un assistant juridique spécialisé dans le droit luxembourgeois. Analyse les documents fournis et donne un résumé concis en français."
                    },
                    {
                        "role": "user", 
                        "content": f"Analyse ces documents juridiques luxembourgeois sur '{keyword}':\n\n{documents[:1500]}..."
                    }
                ]
            )
            
            # Display analysis
            analysis = response.choices[0].message.content
            print(f"📄 Analysis: {analysis[:200]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n🎉 Luxembourg Legal + OpenAI Test Complete!")

async def test_mcp_server_direct():
    """Test direct MCP server connectivity using FastMCP client"""
    
    return await test_fastmcp_client()

def validate_environment():
    """Validate required environment variables"""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env file")
        print("💡 Create a .env file with: OPENAI_API_KEY=your_key_here")
        return False
    
    print("✅ Environment configured correctly")
    return True

async def main():
    """Main test function"""
    
    if not validate_environment():
        return
    
    try:
        # Test MCP server connectivity first
        mcp_works = await test_mcp_server_direct()
        
        if mcp_works:
            print()
            # Then run comprehensive legal search tests
            await test_luxembourg_legal_with_openai()
        else:
            print("❌ Skipping OpenAI tests due to MCP server issues")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())