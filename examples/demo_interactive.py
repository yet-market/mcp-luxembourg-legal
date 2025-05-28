#!/usr/bin/env python3
"""
Demo: Interactive Luxembourg Legal Assistant with OpenAI
This demonstrates the enhanced legal search capabilities.
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp import Client

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# MCP Server Configuration
MCP_SERVER_URL = "https://yet-mcp-legilux.site/mcp/"

async def search_luxembourg_documents(keywords: str, limit: int = 3):
    """Search Luxembourg documents via FastMCP client"""
    
    try:
        transport = StreamableHttpTransport(url=MCP_SERVER_URL)
        
        async with Client(transport) as client:
            result = await client.call_tool(
                "search_luxembourg_documents",
                {
                    "keywords": keywords,
                    "limit": limit,
                    "include_content": False
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

async def demo_question(question: str):
    """Demo a single question with Luxembourg legal enhancement"""
    
    print(f"🔍 Question: {question}")
    print("=" * 60)
    
    # Extract keywords (simple approach)
    keywords = question.lower()
    for word in ['quelles', 'sont', 'les', 'comment', 'que', 'qui', 'où', 'quand', 'pourquoi']:
        keywords = keywords.replace(word, '')
    keywords = keywords.strip()
    
    if not keywords:
        keywords = question
        
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

async def main():
    """Demo with sample questions"""
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env file")
        return
    
    print("🎯 Luxembourg Legal Assistant Demo")
    print("=" * 50)
    print("Testing enhanced legal search with sample questions...\n")
    
    # Demo questions
    questions = [
        "Quelles sont les principales taxes au Luxembourg?",
        "Comment créer une société au Luxembourg?",
        "Quels sont les droits des travailleurs?"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n📋 Demo {i}/3:")
        await demo_question(question)
        print("\n" + "=" * 60 + "\n")
        
        if i < len(questions):
            print("⏳ Next question in 2 seconds...")
            await asyncio.sleep(2)
    
    print("🎉 Demo complete!")
    print("\nTo use interactively, run: python openai_test.py")
    print("Then choose option 2 for interactive mode.")

if __name__ == "__main__":
    asyncio.run(main())