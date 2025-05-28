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
from fastmcp import Client

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# MCP Server Configuration - Streamable HTTP Transport
MCP_SERVER_URL = "https://yet-mcp-legilux.site/mcp/"

async def test_fastmcp_client():
    """Test using FastMCP's official StreamableHttpTransport"""
    
    print("🔌 Testing FastMCP StreamableHttpTransport")
    print("=" * 45)
    
    try:
        # Create FastMCP client with StreamableHttpTransport
        transport = StreamableHttpTransport(url=MCP_SERVER_URL)
        
        async with Client(transport) as client:
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
        # Use the same working connection as test_streamable_http.py
        transport = StreamableHttpTransport(url="https://yet-mcp-legilux.site/mcp")
        
        async with Client(transport) as client:
            result = await client.call_tool(
                "search_luxembourg_documents",
                {
                    "keywords": keywords,
                    "limit": limit,
                    "include_content": True  # Get actual content for OpenAI
                }
            )
            
            # Extract content from FastMCP result (it's a list of TextContent objects)
            if isinstance(result, list):
                content_text = []
                for item in result:
                    if hasattr(item, 'text'):
                        content_text.append(item.text)
                    else:
                        content_text.append(str(item))
                return '\n'.join(content_text)
            else:
                return str(result)
            
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

async def interactive_legal_assistant():
    """Interactive Luxembourg Legal Assistant"""
    
    print("\n🎯 Interactive Luxembourg Legal Assistant")
    print("=" * 55)
    print("Ask questions about Luxembourg law, regulations, or companies.")
    print("Examples:")
    print("  • Quelles sont les lois sur les taxes?")
    print("  • Comment créer une société au Luxembourg?")
    print("  • Règlements sur l'environnement")
    print("\nType 'quit' to exit.\n")
    
    while True:
        try:
            # Get user question
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q', '']:
                print("👋 Au revoir!")
                break
                
            if not question:
                continue
                
            print(f"\n🔍 Searching Luxembourg legal data for: '{question}'")
            print("-" * 60)
            
            # Extract keywords for MCP search
            # Simple keyword extraction - could be enhanced
            keywords = question.lower()
            for word in ['quelles', 'sont', 'les', 'comment', 'que', 'qui', 'où', 'quand', 'pourquoi']:
                keywords = keywords.replace(word, '')
            keywords = keywords.strip()
            
            if not keywords:
                keywords = question  # fallback to full question
                
            print(f"📊 Searching with keywords: '{keywords[:50]}...'")
            
            # Step 1: Search Luxembourg documents
            documents = await search_luxembourg_documents(keywords, limit=3)
            
            if "Error:" in documents:
                print(f"❌ MCP Error: {documents}")
                # Fallback to OpenAI without MCP data
                print("🤖 Answering without legal documents...")
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system", 
                            "content": "Tu es un assistant juridique général. Réponds en français avec des informations générales."
                        },
                        {
                            "role": "user", 
                            "content": question
                        }
                    ]
                )
                
                answer = response.choices[0].message.content
                print(f"\n🤖 General Answer:")
                print("-" * 30)
                print(answer)
                
            else:
                print(f"✅ Found legal documents")
                
                # Step 2: Use OpenAI to analyze with legal context
                print("🤖 Analyzing with Luxembourg legal context...")
                response = await client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system", 
                            "content": "Tu es un assistant juridique spécialisé dans le droit luxembourgeois. Utilise les documents fournis pour donner une réponse précise et détaillée en français. Cite les références légales quand possible."
                        },
                        {
                            "role": "user", 
                            "content": f"Question: {question}\n\nDocuments juridiques luxembourgeois pertinents:\n{documents[:2000]}"
                        }
                    ]
                )
                
                answer = response.choices[0].message.content
                print(f"\n🇱🇺 Enhanced Answer with Luxembourg Legal Data:")
                print("-" * 50)
                print(answer)
                
            print("\n" + "=" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Au revoir!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again with a different question.\n")

async def main():
    """Main test function"""
    
    if not validate_environment():
        return
    
    # Ask user what they want to do
    print("🇱🇺 Luxembourg Legal MCP Server Test")
    print("=" * 40)
    print("Choose an option:")
    print("1. Run automated tests")
    print("2. Interactive legal assistant")
    print("3. Both")
    
    try:
        choice = input("\nYour choice (1-3): ").strip()
        
        if choice in ['1', '3']:
            # Test MCP server connectivity first
            print("\n🔧 Running automated tests...")
            mcp_works = await test_mcp_server_direct()
            
            if mcp_works:
                print()
                # Then run comprehensive legal search tests
                await test_luxembourg_legal_with_openai()
            else:
                print("⚠️  MCP server issues detected, but OpenAI still works")
                
        if choice in ['2', '3']:
            # Run interactive assistant
            await interactive_legal_assistant()
            
        if choice not in ['1', '2', '3']:
            print("Invalid choice. Running interactive mode...")
            await interactive_legal_assistant()
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())