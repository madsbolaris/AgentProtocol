#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Example demonstrating the high-level Python client SDK API.

This example shows:
1. Simple text chat
2. Chat with options
3. Stateful conversations
4. Tool registration and usage
5. Streaming responses
"""

import asyncio
from microsoft.agents.protocol.client import (
    create_simplified_client,
    ChatOptions,
    ToolCollection,
)


# Example tool functions
def get_weather(location: str) -> str:
    """Gets the weather for a location (mock)"""
    weather_data = {
        "Seattle": "Rainy",
        "San Francisco": "Foggy",
        "Miami": "Sunny",
    }
    return weather_data.get(location, "Unknown")


async def search_database(query: str) -> str:
    """Searches database asynchronously (mock)"""
    await asyncio.sleep(0.1)  # Simulate async operation
    return f"Search results for: {query}"


def calculate(x: int, y: int, operation: str = "add") -> str:
    """Performs a calculation"""
    if operation == "add":
        return str(x + y)
    elif operation == "subtract":
        return str(x - y)
    elif operation == "multiply":
        return str(x * y)
    elif operation == "divide":
        return str(x / y) if y != 0 else "Error: division by zero"
    return "Unknown operation"


async def example_simple_chat():
    """Example 1: Simple text chat"""
    print("=" * 60)
    print("Example 1: Simple Text Chat")
    print("=" * 60)

    client = create_simplified_client("http://localhost:5000")

    async with client:
        response = await client.complete_chat("Hello! How are you today?")
        print(f"User: Hello! How are you today?")
        print(f"Agent: {response}")
        print()


async def example_chat_with_options():
    """Example 2: Chat with options"""
    print("=" * 60)
    print("Example 2: Chat with Options")
    print("=" * 60)

    client = create_simplified_client("http://localhost:5000")

    async with client:
        options = ChatOptions(
            agent_id="helpful-assistant",
            metadata={"session_id": "demo-session-123", "user": "demo-user"},
        )

        response = await client.complete_chat("Tell me a fun fact", options)
        print(f"User: Tell me a fun fact")
        print(f"Agent: {response}")
        print()


async def example_conversation():
    """Example 3: Stateful conversation"""
    print("=" * 60)
    print("Example 3: Stateful Conversation")
    print("=" * 60)

    client = create_simplified_client("http://localhost:5000")

    async with client:
        # Create a new conversation
        conversation = client.create_conversation()

        # Send multiple messages
        messages = [
            "My name is Alice and I'm a software engineer",
            "What's my name?",
            "What's my profession?",
        ]

        for message in messages:
            response = await conversation.send(message)
            print(f"User: {message}")
            print(f"Agent: {response}")
            print()

        print(f"Thread ID: {conversation.thread_id}")
        print()


async def example_tools():
    """Example 4: Tool registration and usage"""
    print("=" * 60)
    print("Example 4: Tools")
    print("=" * 60)

    client = create_simplified_client("http://localhost:5000")

    # Setup tools
    tools = ToolCollection()
    tools.add("get_weather", get_weather, "Gets the current weather for a location")
    tools.add(
        "search_database", search_database, "Searches the database for information"
    )
    tools.add("calculate", calculate, "Performs mathematical calculations")

    print(f"Registered {len(tools)} tools:")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    print()

    async with client:
        options = ChatOptions(tools=tools)

        # Example query that might use tools
        queries = [
            "What's the weather in Seattle?",
            "Search for information about Python",
            "What is 15 multiplied by 7?",
        ]

        for query in queries:
            response = await client.complete_chat(query, options)
            print(f"User: {query}")
            print(f"Agent: {response}")
            print()


async def example_streaming():
    """Example 5: Streaming responses"""
    print("=" * 60)
    print("Example 5: Streaming")
    print("=" * 60)

    client = create_simplified_client("http://localhost:5000")

    def handle_chunk(text: str):
        """Callback for streaming chunks"""
        print(text, end="", flush=True)

    async with client:
        print("User: Tell me a short story")
        print("Agent: ", end="", flush=True)

        await client.stream_chat("Tell me a short story about a robot", handle_chunk)

        print()  # New line after streaming
        print()


async def example_structured_messages():
    """Example 6: Structured messages"""
    print("=" * 60)
    print("Example 6: Structured Messages")
    print("=" * 60)

    client = create_simplified_client("http://localhost:5000")

    async with client:
        # Send structured message
        message = {
            "role": "user",
            "contents": [
                {"kind": "text", "text": "Analyze this:"},
                {"kind": "text", "text": "Python is a great language"},
            ],
        }

        response = await client.complete_chat_structured(message)

        print("User (structured):")
        for content in message["contents"]:
            print(f"  - {content['text']}")

        print(f"\nAgent: {response.get('role')}")
        for content in response.get("contents", []):
            if content.get("kind") == "text":
                print(f"  {content.get('text')}")
        print()


async def example_resume_conversation():
    """Example 7: Resume existing conversation"""
    print("=" * 60)
    print("Example 7: Resume Conversation")
    print("=" * 60)

    client = create_simplified_client("http://localhost:5000")

    async with client:
        # Create and get thread ID
        conv1 = client.create_conversation()
        await conv1.send("My favorite color is blue")
        thread_id = conv1.thread_id

        print(f"Created conversation with thread ID: {thread_id}")
        print()

        # Later, resume from thread ID
        conv2 = client.resume_conversation(thread_id)
        response = await conv2.send("What's my favorite color?")

        print(f"User: What's my favorite color?")
        print(f"Agent: {response}")
        print()


async def example_streaming_messages():
    """Example 8: Stream structured messages"""
    print("=" * 60)
    print("Example 8: Stream Structured Messages")
    print("=" * 60)

    client = create_simplified_client("http://localhost:5000")

    async with client:
        conversation = client.create_conversation()

        print("User: Generate a numbered list of 3 items")
        print("Agent (streaming messages):")

        message_count = 0
        async for message in conversation.stream_messages(
            "Generate a numbered list of 3 items"
        ):
            message_count += 1
            contents = message.get("contents", [])
            for content in contents:
                if content.get("kind") == "text":
                    text = content.get("text", "")
                    if text:
                        print(f"  Message {message_count}: {text[:50]}...")

        print()


async def main():
    """Run all examples"""
    print("\n")
    print("=" * 60)
    print("High-Level Python Client SDK Examples")
    print("=" * 60)
    print()
    print("NOTE: These examples require a running Agent Protocol server")
    print("      at http://localhost:5000")
    print()

    try:
        # Run examples
        await example_simple_chat()
        await example_chat_with_options()
        await example_conversation()
        await example_tools()
        await example_streaming()
        await example_structured_messages()
        await example_resume_conversation()
        await example_streaming_messages()

        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nMake sure you have a running Agent Protocol server at:")
        print("  http://localhost:5000")


if __name__ == "__main__":
    asyncio.run(main())
