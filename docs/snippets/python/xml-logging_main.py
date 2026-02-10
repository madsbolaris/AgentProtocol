import asyncio
from microsoft.agents.protocol import AgentProtocolClient
from pathlib import Path


async def main() -> None:
    # Create client with automatic logging enabled
    client = AgentProtocolClient(
        base_url="http://localhost:5000",
        enable_logging=True  # That's it! Auto-saves to logs/conversations/
    )

    # Have a conversation - it's automatically logged
    conversation = client.create_conversation()
    response = await conversation.send("What's the weather in Seattle?")
    print(f"Agent: {response}")

    # Done! Conversation automatically saved to:
    # logs/conversations/{thread_id}.xml

    # Or manually save to a custom location
    xml = str(conversation)  # conversation.__str__() returns XML
    Path("my-conversation.xml").write_text(xml, encoding="utf-8")
    print(f"Saved conversation XML ({len(xml)} bytes)")


if __name__ == "__main__":
    asyncio.run(main())
