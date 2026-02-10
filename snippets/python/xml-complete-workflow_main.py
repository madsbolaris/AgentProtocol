import asyncio
from typing import Optional, List
from pathlib import Path
from microsoft.agents.protocol import AgentProtocolClient
from microsoft.agents.xml import XmlDeserializer
from microsoft.agents.validation import ThreadValidator
from microsoft.agents.models import UserMessage, TextContent, ChatMessage


class ProductionAgentService:
    def __init__(self, endpoint: str):
        # Enable automatic logging
        self.client = AgentProtocolClient(
            endpoint,
            enable_logging=True,
            log_directory="logs/production"
        )
        self.deserializer = XmlDeserializer()
        self.validator = ThreadValidator()

    # 1. Have conversations via Client SDK (auto-logged)
    async def chat(self, user_input: str, thread_id: Optional[str] = None) -> str:
        if thread_id:
            conversation = self.client.resume_conversation(thread_id)
        else:
            conversation = self.client.create_conversation()

        return await conversation.send(user_input)

    # 2. Export conversation XML instantly
    def export_conversation(self, thread_id: str) -> str:
        conversation = self.client.resume_conversation(thread_id)
        return str(conversation)  # Instant XML export

    # 3. Run tests from XML eval files
    async def run_test(self, eval_file: str) -> bool:
        xml = Path(eval_file).read_text()
        test_messages: List[ChatMessage] = self.deserializer.deserialize_many(xml, root_element="eval")

        user_msg = next(m for m in test_messages if isinstance(m, UserMessage))
        conversation = self.client.create_conversation()

        user_text = next(c for c in user_msg.contents if isinstance(c, TextContent)).text
        await conversation.send(user_text)

        # Use local message cache (no HTTP call)
        actual = conversation.messages

        return self.validator.validate(actual, test_messages).is_valid

    # 4. Replay logged conversations for debugging
    async def replay(self, log_file: str) -> None:
        xml = Path(log_file).read_text()
        messages: List[ChatMessage] = self.deserializer.deserialize_many(xml, root_element="thread")

        conversation = self.client.create_conversation()

        for msg in messages:
            if isinstance(msg, UserMessage):
                text = next(c for c in msg.contents if isinstance(c, TextContent)).text
                response = await conversation.send(text)
                print(f"User: {text}\nAgent: {response}\n")


async def main() -> None:
    service = ProductionAgentService("http://localhost:5000")
    await service.chat("Hello")


if __name__ == "__main__":
    asyncio.run(main())
