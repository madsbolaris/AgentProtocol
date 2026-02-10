import asyncio
import time
from typing import List, Optional
from pathlib import Path
from microsoft.agents.protocol import AgentProtocolClient
from microsoft.agents.xml import XmlDeserializer
from microsoft.agents.models import UserMessage, TextContent, ChatMessage


async def main() -> None:
    # Load customer's conversation from XML
    xml = Path("customer-issue-456.xml").read_text()
    deserializer = XmlDeserializer()
    messages: List[ChatMessage] = deserializer.deserialize_many(xml, root_element="thread")

    # Extract thread ID if it exists (for resuming context)
    thread_id: Optional[str] = extract_thread_id(xml)  # Parse thread-id attribute

    # Replay through agent using Client SDK
    client = AgentProtocolClient("http://localhost:5000")

    for message in messages:
        if isinstance(message, UserMessage):
            print("\n--- User Message ---")
            user_text = next(c for c in message.contents if isinstance(c, TextContent)).text
            print(f"User: {user_text}")

            # Re-run through agent via Client SDK
            conversation = (
                client.resume_conversation(thread_id) if thread_id
                else client.create_conversation()
            )

            start = time.time()
            response = await conversation.send(user_text)
            elapsed = (time.time() - start) * 1000

            print(f"Response time: {elapsed:.0f}ms")
            print(f"Agent: {response}")

    print("\n✓ Replay complete - verify behavior matches expectations")


def extract_thread_id(xml: str) -> Optional[str]:
    """Extract thread-id attribute from XML."""
    # Simple regex or XML parsing
    return None  # Placeholder


if __name__ == "__main__":
    asyncio.run(main())
