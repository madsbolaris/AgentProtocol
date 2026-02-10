import asyncio
from microsoft.agents.protocol import AgentProtocolClient


async def main() -> None:
    client = AgentProtocolClient(base_url="http://localhost:5000")
    conversation = client.create_conversation()
    await conversation.send("Hello!")
    await conversation.send("How are you?")

    # Access cached messages (no HTTP call)
    messages = conversation.messages
    print(f"Conversation has {len(messages)} messages")

    # Or convert to XML instantly
    xml = str(conversation)
    print(xml)


if __name__ == "__main__":
    asyncio.run(main())
