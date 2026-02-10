import asyncio
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

    async def run_evaluation(self, test_file_path: str) -> bool:
        """Run evaluation test case against live agent."""
        # Load evaluation test case from XML
        test_xml = Path(test_file_path).read_text()
        test_messages: List[ChatMessage] = self.deserializer.deserialize_many(test_xml, root_element="eval")

        # Extract the user input from the test case
        user_message = next(m for m in test_messages if isinstance(m, UserMessage))
        expected_messages = [m for m in test_messages if not isinstance(m, UserMessage)]

        # Send to agent via Client SDK
        conversation = self.client.create_conversation()
        user_text = next(c for c in user_message.contents if isinstance(c, TextContent)).text
        await conversation.send(user_text)

        # Get messages from local cache (no HTTP call)
        actual_messages = conversation.messages

        # Validate actual vs expected behavior
        validation_result = self.validator.validate(actual_messages, expected_messages)

        if validation_result.is_valid:
            print(f"✓ Test passed: {test_file_path}")
            return True
        else:
            print(f"✗ Test failed: {test_file_path}")
            for error in validation_result.errors:
                print(f"  - {error.message}")
            return False


async def main() -> None:
    # Usage: Run all evals
    runner = EvaluationRunner("http://localhost:5000")
    test_files = Path("test-cases").glob("*.xml")
    for test_file in test_files:
        await runner.run_evaluation(str(test_file))


if __name__ == "__main__":
    asyncio.run(main())
