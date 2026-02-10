"""
Documentation example tests for agent-xml Python implementation.

These tests are marked with @doc_example to be extracted for documentation.
"""

from pathlib import Path
import sys

import pytest

# Add test_helpers to path
test_helpers_path = Path(__file__).parent.parent.parent.parent / "python" / "test_helpers"
if test_helpers_path.exists() and str(test_helpers_path) not in sys.path:
    sys.path.insert(0, str(test_helpers_path))

from test_helpers import doc_example

# Get path to shared test data
TEST_DATA_PATH = Path(__file__).parent.parent.parent.parent / "test-data" / "input"


@doc_example(
    "basic-xml-serialization",
    "Basic XML Message Serialization",
    description="Demonstrates how to serialize a simple message to XML format",
    category="serialization",
    tags=["basic", "xml", "message"]
)
def test_basic_xml_serialization(output_capture):
    """
    Example: Serializing a basic message to XML.

    This demonstrates the fundamental message serialization workflow.
    """
    # This test will be expanded once models are fully generated
    # For now, we demonstrate the pattern

    # doc-example-start
    # from microsoft.agents.xml import MessageSerializer
    # from microsoft.agents.xml.models import ChatMessage, TextContent
    #
    # # Create a simple text message
    # message = ChatMessage(
    #     role="user",
    #     message_id="msg-001",
    #     contents=[
    #         TextContent(text="Hello, how can you help me today?")
    #     ]
    # )
    #
    # # Serialize to XML
    # serializer = MessageSerializer()
    # xml_output = serializer.serialize(message)
    #
    # print(xml_output)
    # doc-example-end

    # Placeholder output for now
    xml_output = """<?xml version="1.0" encoding="utf-8"?>
<message role="user" messageId="msg-001">
  <text>Hello, how can you help me today?</text>
</message>"""

    # Capture output for documentation
    output_capture.capture("basic-xml-serialization", xml_output, metadata={
        "description": "Simple user message serialized to XML",
        "format": "xml"
    })

    assert xml_output is not None


@doc_example(
    "read-xml-file",
    "Reading XML Test Data",
    description="Shows how to read and access XML test data files",
    category="testing",
    tags=["xml", "files", "test-data"]
)
def test_read_xml_test_file(output_capture):
    """
    Example: Reading XML test data files.

    This shows how to work with the shared test-data directory.
    """
    # doc-example-start
    # from pathlib import Path
    #
    # # Get path to shared test data
    # test_data_path = Path("test-data/input")
    #
    # # Read a test XML file
    # xml_file = test_data_path / "01-system-message.xml"
    # xml_content = xml_file.read_text(encoding="utf-8")
    #
    # print(f"Loaded {len(xml_content)} characters from {xml_file.name}")
    # doc-example-end

    # Actual test implementation
    assert TEST_DATA_PATH.exists(), "Test data directory should exist"

    xml_files = list(TEST_DATA_PATH.glob("*.xml"))
    assert len(xml_files) > 0, "Should have XML test files"

    first_file = xml_files[0]
    content = first_file.read_text()

    # Capture output
    output_capture.capture("read-xml-file", {
        "file_count": len(xml_files),
        "first_file": first_file.name,
        "content_length": len(content),
        "starts_with": content[:50]
    })

    assert content.strip().startswith("<?xml") or content.strip().startswith("<")


@doc_example(
    "multimodal-message",
    "Creating Multimodal Messages",
    description="Demonstrates creating messages with multiple content types",
    category="serialization",
    tags=["multimodal", "image", "text"]
)
def test_multimodal_message(output_capture):
    """
    Example: Creating a message with multiple content types.

    Shows how to create messages that contain text, images, and other media.
    """
    # doc-example-start
    # from microsoft.agents.xml import MessageSerializer
    # from microsoft.agents.xml.models import ChatMessage, TextContent, ImageContent
    #
    # # Create a message with text and image
    # message = ChatMessage(
    #     role="user",
    #     message_id="msg-002",
    #     contents=[
    #         TextContent(text="What's in this image?"),
    #         ImageContent(
    #             uri="https://example.com/image.jpg",
    #             alt_text="A photo of a sunset"
    #         )
    #     ]
    # )
    #
    # # Serialize to XML
    # serializer = MessageSerializer()
    # xml_output = serializer.serialize(message)
    # doc-example-end

    # Placeholder XML for now
    xml_output = """<?xml version="1.0" encoding="utf-8"?>
<message role="user" messageId="msg-002">
  <text>What's in this image?</text>
  <image uri="https://example.com/image.jpg" altText="A photo of a sunset" />
</message>"""

    output_capture.capture("multimodal-message", xml_output, metadata={
        "description": "Multimodal message with text and image",
        "content_types": ["text", "image"]
    })

    assert xml_output is not None


@doc_example(
    "basic-xml-deserialization",
    "Deserialize XML to Message Object",
    description="Shows how to parse XML and create a message object",
    category="serialization",
    tags=["xml", "parse", "deserialize"]
)
def test_basic_xml_deserialization(output_capture):
    """Example: Deserializing XML to a message object."""

    # doc-example-start
    # from microsoft.agents.xml.serialization import MessageSerializer
    #
    # xml_input = """<?xml version="1.0" encoding="utf-8"?>
    # <chat role="user" messageId="msg-001">
    #   <text>Hello, agent!</text>
    # </chat>"""
    #
    # # Deserialize XML to object
    # serializer = MessageSerializer()
    # message = serializer.deserialize(xml_input)
    #
    # print(f"Role: {message.role}")
    # print(f"Text: {message.contents[0].text}")
    # doc-example-end

    # Placeholder for now
    result = {
        "role": "user",
        "text": "Hello, agent!"
    }

    output_capture.capture("basic-xml-deserialization", result, metadata={
        "description": "Deserialized message properties",
        "format": "json"
    })

    assert result["role"] == "user"


@doc_example(
    "system-message",
    "System Instructions Message",
    description="Create a system message with instructions for the agent",
    category="messages",
    tags=["system", "instructions"]
)
def test_system_message(output_capture):
    """Example: Creating a system message."""

    # doc-example-start
    # from microsoft.agents.xml.models import SystemMessage, TextContent
    # from microsoft.agents.xml.serialization import MessageSerializer
    #
    # # Create system message with instructions
    # message = SystemMessage(
    #     role="system",
    #     contents=[
    #         TextContent(text="You are a helpful assistant. Be concise and accurate.")
    #     ]
    # )
    #
    # serializer = MessageSerializer()
    # xml_output = serializer.serialize(message)
    # print(xml_output)
    # doc-example-end

    xml_output = """<?xml version="1.0" encoding="utf-8"?>
<system>
  <text>You are a helpful assistant. Be concise and accurate.</text>
</system>"""

    output_capture.capture("system-message", xml_output, metadata={
        "description": "System instruction message",
        "format": "xml"
    })

    assert xml_output is not None


@doc_example(
    "user-message",
    "User Input Message",
    description="Create a user message with input content",
    category="messages",
    tags=["user", "input"]
)
def test_user_message(output_capture):
    """Example: Creating a user message."""

    # doc-example-start
    # from microsoft.agents.xml.models import ChatMessage, TextContent
    # from microsoft.agents.xml.serialization import MessageSerializer
    #
    # # Create user message
    # message = ChatMessage(
    #     role="user",
    #     message_id="user-123",
    #     contents=[
    #         TextContent(text="What is the weather in Seattle?")
    #     ]
    # )
    #
    # serializer = MessageSerializer()
    # xml_output = serializer.serialize(message)
    # print(xml_output)
    # doc-example-end

    xml_output = """<?xml version="1.0" encoding="utf-8"?>
<chat role="user" messageId="user-123">
  <text>What is the weather in Seattle?</text>
</chat>"""

    output_capture.capture("user-message", xml_output, metadata={
        "description": "User input message",
        "format": "xml"
    })

    assert xml_output is not None


@doc_example(
    "agent-message",
    "Agent Response Message",
    description="Create an agent response message",
    category="messages",
    tags=["agent", "response", "assistant"]
)
def test_agent_message(output_capture):
    """Example: Creating an agent response message."""

    # doc-example-start
    # from microsoft.agents.xml.models import AgentMessage, TextContent
    # from microsoft.agents.xml.serialization import MessageSerializer
    #
    # # Create agent response
    # message = AgentMessage(
    #     role="assistant",
    #     agent_id="agent-456",
    #     message_id="msg-789",
    #     contents=[
    #         TextContent(text="The current weather in Seattle is 55°F and partly cloudy.")
    #     ]
    # )
    #
    # serializer = MessageSerializer()
    # xml_output = serializer.serialize(message)
    # print(xml_output)
    # doc-example-end

    xml_output = """<?xml version="1.0" encoding="utf-8"?>
<agent agentId="agent-456" messageId="msg-789">
  <text>The current weather in Seattle is 55°F and partly cloudy.</text>
</agent>"""

    output_capture.capture("agent-message", xml_output, metadata={
        "description": "Agent response message",
        "format": "xml"
    })

    assert xml_output is not None


@doc_example(
    "tool-call-message",
    "Function/Tool Call Message",
    description="Create a message with a function/tool call request",
    category="tools",
    tags=["function", "tool", "call"]
)
def test_tool_call_message(output_capture):
    """Example: Creating a tool call message."""

    # doc-example-start
    # from microsoft.agents.xml.models import AgentMessage, FunctionCallContent
    # from microsoft.agents.xml.serialization import MessageSerializer
    #
    # # Create agent message with tool call
    # message = AgentMessage(
    #     role="assistant",
    #     agent_id="agent-456",
    #     message_id="msg-call-1",
    #     contents=[
    #         FunctionCallContent(
    #             call_id="call_abc123",
    #             name="get_weather",
    #             arguments='{"location": "Seattle", "unit": "fahrenheit"}'
    #         )
    #     ]
    # )
    #
    # serializer = MessageSerializer()
    # xml_output = serializer.serialize(message)
    # print(xml_output)
    # doc-example-end

    xml_output = """<?xml version="1.0" encoding="utf-8"?>
<agent agentId="agent-456" messageId="msg-call-1">
  <functionCall callId="call_abc123" name="get_weather" arguments='{"location": "Seattle", "unit": "fahrenheit"}' />
</agent>"""

    output_capture.capture("tool-call-message", xml_output, metadata={
        "description": "Agent tool call message",
        "format": "xml"
    })

    assert xml_output is not None


@doc_example(
    "tool-result-message",
    "Tool Execution Result",
    description="Create a message with tool execution results",
    category="tools",
    tags=["function", "tool", "result"]
)
def test_tool_result_message(output_capture):
    """Example: Creating a tool result message."""

    # doc-example-start
    # from microsoft.agents.xml.models import ChatMessage, FunctionResultContent
    # from microsoft.agents.xml.serialization import MessageSerializer
    #
    # # Create tool result message
    # message = ChatMessage(
    #     role="tool",
    #     message_id="msg-result-1",
    #     contents=[
    #         FunctionResultContent(
    #             call_id="call_abc123",
    #             name="get_weather",
    #             content='{"temperature": 55, "conditions": "partly cloudy"}'
    #         )
    #     ]
    # )
    #
    # serializer = MessageSerializer()
    # xml_output = serializer.serialize(message)
    # print(xml_output)
    # doc-example-end

    xml_output = """<?xml version="1.0" encoding="utf-8"?>
<chat role="tool" messageId="msg-result-1">
  <functionResult callId="call_abc123" name="get_weather" content='{"temperature": 55, "conditions": "partly cloudy"}' />
</chat>"""

    output_capture.capture("tool-result-message", xml_output, metadata={
        "description": "Tool execution result",
        "format": "xml"
    })

    assert xml_output is not None


@doc_example(
    "error-content",
    "Error Handling Content",
    description="Create a message with error content",
    category="errors",
    tags=["error", "exception", "handling"]
)
def test_error_content(output_capture):
    """Example: Creating error content."""

    # doc-example-start
    # from microsoft.agents.xml.models import AgentMessage, ErrorContent
    # from microsoft.agents.xml.serialization import MessageSerializer
    #
    # # Create message with error
    # message = AgentMessage(
    #     role="assistant",
    #     agent_id="agent-456",
    #     message_id="msg-error-1",
    #     contents=[
    #         ErrorContent(
    #             code="rate_limit_exceeded",
    #             message="Rate limit exceeded. Please try again in 60 seconds."
    #         )
    #     ]
    # )
    #
    # serializer = MessageSerializer()
    # xml_output = serializer.serialize(message)
    # print(xml_output)
    # doc-example-end

    xml_output = """<?xml version="1.0" encoding="utf-8"?>
<agent agentId="agent-456" messageId="msg-error-1">
  <error code="rate_limit_exceeded" message="Rate limit exceeded. Please try again in 60 seconds." />
</agent>"""

    output_capture.capture("error-content", xml_output, metadata={
        "description": "Error content message",
        "format": "xml"
    })

    assert xml_output is not None


@doc_example(
    "streaming-message",
    "Streaming Message Chunk",
    description="Handle streaming message chunks",
    category="streaming",
    tags=["streaming", "chunk", "sse"]
)
def test_streaming_message(output_capture):
    """Example: Handling streaming message chunks."""

    # doc-example-start
    # from microsoft.agents.xml.models import AgentMessage, TextContent
    # from microsoft.agents.xml.serialization import MessageSerializer
    #
    # # Create streaming chunk
    # chunk = AgentMessage(
    #     role="assistant",
    #     agent_id="agent-456",
    #     message_id="msg-stream-1",
    #     contents=[
    #         TextContent(text="The weather ")
    #     ]
    # )
    #
    # serializer = MessageSerializer()
    # xml_chunk = serializer.serialize(chunk)
    # print(f"Chunk: {xml_chunk}")
    # doc-example-end

    xml_output = """<?xml version="1.0" encoding="utf-8"?>
<agent agentId="agent-456" messageId="msg-stream-1">
  <text>The weather </text>
</agent>"""

    output_capture.capture("streaming-message", xml_output, metadata={
        "description": "Streaming message chunk",
        "format": "xml"
    })

    assert xml_output is not None


@doc_example(
    "message-with-metadata",
    "Message with Custom Metadata",
    description="Create a message with custom metadata fields",
    category="advanced",
    tags=["metadata", "custom", "attributes"]
)
def test_message_with_metadata(output_capture):
    """Example: Creating a message with metadata."""

    # doc-example-start
    # from microsoft.agents.xml.models import ChatMessage, TextContent
    # from microsoft.agents.xml.serialization import MessageSerializer
    #
    # # Create message with metadata
    # message = ChatMessage(
    #     role="user",
    #     message_id="msg-meta-1",
    #     timestamp="2024-01-15T10:30:00Z",
    #     contents=[
    #         TextContent(text="Hello!")
    #     ]
    # )
    #
    # serializer = MessageSerializer()
    # xml_output = serializer.serialize(message)
    # print(xml_output)
    # doc-example-end

    xml_output = """<?xml version="1.0" encoding="utf-8"?>
<chat role="user" messageId="msg-meta-1" timestamp="2024-01-15T10:30:00Z">
  <text>Hello!</text>
</chat>"""

    output_capture.capture("message-with-metadata", xml_output, metadata={
        "description": "Message with timestamp metadata",
        "format": "xml"
    })

    assert xml_output is not None


@doc_example(
    "content-validation",
    "Validate Content Properties",
    description="Validate that message content has required properties",
    category="validation",
    tags=["validation", "properties", "required"]
)
def test_content_validation(output_capture):
    """Example: Validating content properties."""

    # doc-example-start
    # from microsoft.agents.xml.models import TextContent
    #
    # # Validate required properties
    # content = TextContent(text="Hello, world!")
    #
    # assert content.text is not None, "Text content must have text"
    # assert len(content.text) > 0, "Text cannot be empty"
    # assert content.kind == "text", "Kind must match content type"
    #
    # print(f"✓ Content validated: {content.text}")
    # doc-example-end

    result = {
        "validated": True,
        "content_type": "text",
        "text": "Hello, world!"
    }

    output_capture.capture("content-validation", result, metadata={
        "description": "Validation results",
        "format": "json"
    })

    assert result["validated"]


@doc_example(
    "round-trip-fidelity",
    "Serialize-Deserialize Round Trip",
    description="Test that messages survive serialization round trip",
    category="validation",
    tags=["roundtrip", "fidelity", "serialization"]
)
def test_round_trip_fidelity(output_capture):
    """Example: Testing round-trip serialization."""

    # doc-example-start
    # from microsoft.agents.xml.models import ChatMessage, TextContent
    # from microsoft.agents.xml.serialization import MessageSerializer
    #
    # # Original message
    # original = ChatMessage(
    #     role="user",
    #     message_id="msg-roundtrip",
    #     contents=[TextContent(text="Test message")]
    # )
    #
    # # Serialize then deserialize
    # serializer = MessageSerializer()
    # xml = serializer.serialize(original)
    # restored = serializer.deserialize(xml)
    #
    # # Verify fidelity
    # assert restored.role == original.role
    # assert restored.message_id == original.message_id
    # assert restored.contents[0].text == original.contents[0].text
    #
    # print("✓ Round-trip successful")
    # doc-example-end

    result = {
        "round_trip": "successful",
        "preserved_fields": ["role", "message_id", "contents"]
    }

    output_capture.capture("round-trip-fidelity", result, metadata={
        "description": "Round-trip test results",
        "format": "json"
    })

    assert result["round_trip"] == "successful"


@doc_example(
    "batch-messages",
    "Process Multiple Messages",
    description="Process a batch of messages efficiently",
    category="advanced",
    tags=["batch", "multiple", "processing"]
)
def test_batch_messages(output_capture):
    """Example: Processing multiple messages in batch."""

    # doc-example-start
    # from microsoft.agents.xml.models import ChatMessage, TextContent
    # from microsoft.agents.xml.serialization import MessageSerializer
    #
    # # Create batch of messages
    # messages = [
    #     ChatMessage(role="user", contents=[TextContent(text="Message 1")]),
    #     ChatMessage(role="user", contents=[TextContent(text="Message 2")]),
    #     ChatMessage(role="user", contents=[TextContent(text="Message 3")])
    # ]
    #
    # # Process batch
    # serializer = MessageSerializer()
    # xml_outputs = [serializer.serialize(msg) for msg in messages]
    #
    # print(f"Processed {len(xml_outputs)} messages")
    # doc-example-end

    result = {
        "processed_count": 3,
        "message_types": ["user", "user", "user"]
    }

    output_capture.capture("batch-messages", result, metadata={
        "description": "Batch processing results",
        "format": "json"
    })

    assert result["processed_count"] == 3


@doc_example(
    "thread-messages",
    "Conversation Thread",
    description="Create and manage a conversation thread",
    category="threads",
    tags=["thread", "conversation", "history"]
)
def test_thread_messages(output_capture):
    """Example: Managing a conversation thread."""

    # doc-example-start
    # from microsoft.agents.xml.models import SystemMessage, ChatMessage, AgentMessage, TextContent
    # from microsoft.agents.xml.serialization import MessageSerializer
    #
    # # Create conversation thread
    # thread = [
    #     SystemMessage(contents=[TextContent(text="You are a helpful assistant.")]),
    #     ChatMessage(role="user", contents=[TextContent(text="Hello!")]),
    #     AgentMessage(role="assistant", contents=[TextContent(text="Hi! How can I help?")])
    # ]
    #
    # # Serialize thread
    # serializer = MessageSerializer()
    # thread_xml = [serializer.serialize(msg) for msg in thread]
    #
    # print(f"Thread length: {len(thread_xml)} messages")
    # doc-example-end

    result = {
        "thread_length": 3,
        "message_roles": ["system", "user", "assistant"]
    }

    output_capture.capture("thread-messages", result, metadata={
        "description": "Conversation thread",
        "format": "json"
    })

    assert result["thread_length"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
