import asyncio
import time
from typing import List
from pathlib import Path
from microsoft.agents.protocol import AgentProtocolClient
from microsoft.agents.xml import XmlDeserializer
from microsoft.agents.validation import ThreadValidator
from microsoft.agents.models import UserMessage, TextContent, ChatMessage


class EvaluationRunner:
    def __init__(self, agent_endpoint: str):
        self.client = AgentProtocolClient(agent_endpoint)
        self.deserializer = XmlDeserializer()
        self.validator = ThreadValidator()

    async def run_multi_turn_eval(self, test_file_path: str) -> bool:
        # Load eval
        xml = Path(test_file_path).read_text()
        test_messages: List[ChatMessage] = self.deserializer.deserialize_many(xml, root_element="eval")

        # Extract user messages and expected responses
        user_messages = [m for m in test_messages if isinstance(m, UserMessage)]

        # Use Client SDK with persistent conversation
        conversation = self.client.create_conversation()
        start = time.time()

        # Send each user message in sequence
        for user_msg in user_messages:
            text = next(c for c in user_msg.contents if isinstance(c, TextContent)).text
            await conversation.send(text)

        elapsed_ms = (time.time() - start) * 1000

        # Get messages from local cache (no HTTP call)
        actual_messages = conversation.messages

        # Validate against expected behavior
        result = self.validator.validate(actual_messages, test_messages)

        # Check metrics
        if elapsed_ms > 2000:
            print(f"⚠ Performance threshold exceeded: {elapsed_ms:.0f}ms")

        return result.is_valid


async def main() -> None:
    runner = EvaluationRunner("http://localhost:5000")
    await runner.run_multi_turn_eval("test-cases/multi-turn-booking.xml")


if __name__ == "__main__":
    asyncio.run(main())
