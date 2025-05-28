#!/usr/bin/env python3
"""
OpenAI Direct MCP Integration Test
This uses OpenAI SDK's native MCP support to connect directly to our Luxembourg Legal server.
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment variables
load_dotenv()


async def test_openai_direct_mcp():
    """Test OpenAI SDK direct MCP integration"""

    print("🚀 Testing OpenAI SDK Direct MCP Integration")
    print("=" * 50)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in .env file")
        return

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Test questions
    test_questions = [
        "What are the main tax laws in Luxembourg?",
        "How to create a company in Luxembourg?",
        "What are worker rights in Luxembourg?"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n📋 Test {i}/3: {question}")
        print("-" * 60)

        try:
            # Use OpenAI SDK's native MCP support
            response = await client.responses.create(
                model="gpt-4.1",
                input=question,
                tools=[
                    {
                        "type": "mcp",
                        "server_label": "luxembourg-legal",
                        "server_url": "https://yet-mcp-legilux.site/mcp/",
                        "require_approval": "never",
                    }
                ]
            )

            # Extract the actual text answer
            answer = None
            mcp_calls = 0
            
            # Parse the response output
            for output in response.output:
                if hasattr(output, 'type'):
                    if output.type == 'mcp_list_tools':
                        mcp_calls += 1
                        print(f"✅ MCP Tools Available: {len(output.tools)} tools from '{output.server_label}'")
                    elif output.type == 'message' and hasattr(output, 'content'):
                        for content in output.content:
                            if hasattr(content, 'text'):
                                answer = content.text
            
            if answer:
                print(f"🇱🇺 Answer with Luxembourg Legal MCP:")
                print("-" * 40)
                print(answer)
            
            if mcp_calls > 0:
                print(f"\n✅ MCP Server Called: {mcp_calls} interactions with luxembourg-legal server")
            else:
                print(f"\n⚠️  No MCP calls detected")

        except Exception as e:
            print(f"❌ Error: {e}")

        if i < len(test_questions):
            print("\n" + "=" * 60)
            await asyncio.sleep(2)

    print(f"\n🎉 OpenAI Direct MCP Integration Test Complete!")
    print("This is the proper way to use MCP with OpenAI!")

if __name__ == "__main__":
    asyncio.run(test_openai_direct_mcp())
