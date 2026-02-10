import asyncio
from pathlib import Path
from microsoft.agents.protocol import AgentProtocolClient


async def main() -> None:
    # Have a conversation via Client SDK
    client = AgentProtocolClient("http://localhost:5000")
    conversation = client.create_conversation()
    await conversation.send("Book a flight to Seattle")
    await conversation.send("The first one")

    # Export conversation instantly with str()
    xml = str(conversation)

    # Save or send to developer
    Path("customer-issue-456.xml").write_text(xml, encoding="utf-8")
    print("Exported conversation to customer-issue-456.xml")


if __name__ == "__main__":
    asyncio.run(main())
