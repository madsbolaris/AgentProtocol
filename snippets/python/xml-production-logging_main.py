import asyncio
import logging
from typing import Optional
from microsoft.agents.protocol import AgentProtocolClient


class ProductionAgentService:
    def __init__(self, endpoint: str):
        # Enable automatic logging to files
        self.client = AgentProtocolClient(
            endpoint,
            enable_logging=True,
            log_directory="logs/production"
        )
        self.logger = logging.getLogger(__name__)

    async def chat(self, user_input: str, thread_id: Optional[str] = None) -> str:
        if thread_id:
            conversation = self.client.resume_conversation(thread_id)
        else:
            conversation = self.client.create_conversation()

        response = await conversation.send(user_input)

        # Structured logging with message count
        self.logger.info(
            "Conversation turn completed",
            extra={
                "thread_id": conversation.thread_id,
                "message_count": len(conversation.messages)
            }
        )

        # Optionally stream XML to centralized storage
        await self.send_to_observability_platform(
            conversation.thread_id,
            str(conversation)
        )

        return response

    async def send_to_observability_platform(self, thread_id: str, xml: str) -> None:
        # Send to Datadog, New Relic, etc.
        pass


async def main() -> None:
    service = ProductionAgentService("http://localhost:5000")
    await service.chat("Hello, how can you help?")


if __name__ == "__main__":
    asyncio.run(main())
