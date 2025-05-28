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
import aiohttp
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# MCP Server Configuration
MCP_SERVER_URL = "https://yet-mcp-legilux.site/mcp/"

class MCPClient:
    """MCP Streamable HTTP Client with session management"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session_id = None
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def call(self, method: str, params: dict = None):
        """Call the MCP server with proper session handling"""
        
        message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json,text/event-stream",  # No space after comma
            "Cache-Control": "no-cache"
        }
        
        # Add session ID if we have one (except for initialize)
        if self.session_id and method != "initialize":
            headers["Mcp-Session-Id"] = self.session_id
        
        async with self.session.post(
            self.server_url,
            json=message,
            headers=headers
        ) as response:
            
            # Check for session ID in response (during initialize)
            if "Mcp-Session-Id" in response.headers:
                self.session_id = response.headers["Mcp-Session-Id"]
                print(f"🆔 Session ID: {self.session_id}")
            
            if response.status == 200:
                content = await response.text()
                # Handle both JSON and event-stream responses
                if content.startswith('data: '):
                    json_data = content.replace('data: ', '').strip()
                    return json.loads(json_data)
                else:
                    return json.loads(content)
            else:
                response_text = await response.text()
                raise Exception(f"MCP server error: {response.status} - {response_text}")

async def call_mcp_server(method: str, params: dict = None):
    """Legacy wrapper for backward compatibility"""
    async with MCPClient(MCP_SERVER_URL) as client:
        if method == "initialize":
            return await client.call(method, params)
        else:
            # For non-initialize calls, we need to initialize first
            await client.call("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            })
            return await client.call(method, params)

async def search_luxembourg_documents(keywords: str, limit: int = 3):
    """Search Luxembourg documents via MCP server"""
    
    try:
        result = await call_mcp_server(
            "tools/call",
            {
                "name": "search_luxembourg_documents",
                "arguments": {
                    "keywords": keywords,
                    "limit": limit,
                    "include_content": False
                }
            }
        )
        
        if "result" in result and "content" in result["result"]:
            return result["result"]["content"][0]["text"]
        else:
            return "No results found"
            
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
    """Test direct MCP server connectivity with proper session management"""
    
    print("🔌 Testing Direct MCP Server Connectivity")
    print("=" * 40)
    
    try:
        async with MCPClient(MCP_SERVER_URL) as client:
            # Test MCP initialization
            print("🤝 Testing MCP initialization...")
            init_result = await client.call(
                "initialize",
                {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            )
            
            server_info = init_result.get('result', {}).get('serverInfo', {})
            print(f"✅ MCP Initialize: {server_info.get('name', 'Success')}")
            print(f"📋 Server version: {server_info.get('version', 'unknown')}")
            
            # Test listing tools
            print("🛠️  Testing tools list...")
            tools_result = await client.call("tools/list")
            
            if "result" in tools_result and "tools" in tools_result["result"]:
                tools = tools_result["result"]["tools"]
                tool_names = [tool['name'] for tool in tools]
                print(f"✅ Available tools: {tool_names}")
                
                # Test a simple tool call
                if "search_luxembourg_documents" in tool_names:
                    print("🧪 Testing search tool...")
                    search_result = await client.call(
                        "tools/call",
                        {
                            "name": "search_luxembourg_documents",
                            "arguments": {
                                "keywords": "test",
                                "limit": 1,
                                "include_content": False
                            }
                        }
                    )
                    print(f"✅ Search test successful")
                
                return True
            else:
                print("⚠️  No tools found in response")
                print(f"🔍 Full response: {tools_result}")
                return False
                
    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

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