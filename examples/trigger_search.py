#!/usr/bin/env python3
"""
Simple test to trigger search_luxembourg_documents and see detailed logs
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

async def trigger_search():
    """Trigger a simple search to see logs"""
    
    print("🔍 Triggering Luxembourg legal search to see detailed logs...")
    
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        response = await client.responses.create(
            model="gpt-4.1",
            input="Search for the latest Luxembourg tax regulations from 2024-2025 in the official legal database. I need specific document titles, dates, and legal references.",
            tools=[
                {
                    "type": "mcp",
                    "server_label": "luxembourg-legal", 
                    "server_url": "https://yet-mcp-legilux.site/mcp/",
                    "require_approval": "never",
                }
            ]
        )
        
        print("✅ Search triggered successfully!")
        print("Check your server logs with: sudo ./logs.sh")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(trigger_search())