# Protocol-Native LLM Client

**Protocol-Native LLM clients that speak Agent Protocol types directly.**

## Problem

Traditional LLM clients (OpenAI, Anthropic, etc.) return provider-specific types that need to be converted to Agent Protocol types:

```python
# ❌ Traditional approach - requires conversion
openai_response = await openai_client.chat.completions.create(...)
# Need to convert OpenAI types → Agent Protocol types
agent_message = convert_to_protocol(openai_response)
```

This creates several problems:
- Two type systems (provider types vs Protocol types)
- Conversion layer needed for each provider
- Lossy mappings between type systems
- More code to maintain and test

## Solution

**IProtocolLLMClient** returns Agent Protocol types directly:

```python
# ✅ Protocol-Native approach - no conversion needed
llm_client = OpenAIProtocolClient(api_key, model="gpt-4o")
agent_message = await llm_client.generate(conversation_history)
# agent_message is already AgentMessage with Protocol content types!
```

## Installation

```bash
pip install microsoft-agents-protocol-llm
```

## Quick Start

### Basic Usage

```python
from microsoft_agents_protocol_llm import OpenAIProtocolClient
from microsoft_agents_protocol.models import UserMessage, TextContent

# Create client
llm = OpenAIProtocolClient(
    api_key="your-api-key",
    model="gpt-4o",
    temperature=0.7
)

# Build conversation with Protocol types
conversation = [
    UserMessage(contents=[TextContent(text="What is 2+2?")])
]

# Generate response - returns Protocol types!
response = await llm.generate(conversation)

# response is AgentMessage with Protocol TextContent
print(response.contents[0].text)  # "2+2 equals 4."
```

### Streaming

```python
async for delta in llm.stream(conversation):
    if delta.type == DeltaType.TEXT_DELTA:
        print(delta.content.text, end="", flush=True)
```

### Function Calling

```python
from microsoft_agents_protocol_llm import ToolDefinition, FunctionDefinition

# Define tools in Protocol format
tools = [
    ToolDefinition(
        function=FunctionDefinition(
            name="get_weather",
            description="Get weather for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        )
    )
]

# Generate with tools
response = await llm.generate(conversation, available_tools=tools)

# Check for tool calls (already Protocol types!)
for content in response.contents:
    if isinstance(content, FunctionCallContent):
        print(f"Tool call: {content.name}({content.arguments})")
```

### Custom Endpoint (Azure, Foundry, etc.)

```python
llm = OpenAIProtocolClient(
    api_key="your-key",
    base_url="https://your-foundry-endpoint.azure.com/api/projects/your-project/openai/v1",
    model="gpt-5-nano",
    temperature=0.0,
    seed=42
)
```

### Testing with Mocks

```python
from microsoft_agents_protocol_llm import MockProtocolLLMClient

# Create mock
mock_llm = MockProtocolLLMClient()

# Queue responses
mock_llm.enqueue_text_response("Mocked response!")

# Use in tests
response = await mock_llm.generate(conversation)
print(response.contents[0].text)  # "Mocked response!"

# Check call history
print(f"Called {mock_llm.call_count} times")
```

## Benefits

### ✅ Single Type System
Everything uses Agent Protocol types - no conversion needed.

### ✅ Provider Abstraction
Switch providers by changing one line:
```python
# OpenAI
llm = OpenAIProtocolClient(api_key, "gpt-4o")

# Anthropic (when implemented)
llm = AnthropicProtocolClient(api_key, "claude-3-5-sonnet")

# Rest of code stays the same!
```

### ✅ No Lossy Conversions
Provider responses are converted directly to Protocol types internally - nothing is lost.

### ✅ Easier Testing
Mock the `ProtocolLLMClient` interface instead of provider-specific clients.

### ✅ Cleaner Code
~50% less code compared to maintaining conversion layers for each provider.

## API Reference

### ProtocolLLMClient (Abstract Base Class)

```python
class ProtocolLLMClient(ABC):
    @property
    @abstractmethod
    def provider_info(self) -> LLMProviderInfo:
        """Provider metadata and capabilities."""
        pass

    @abstractmethod
    async def generate(
        self,
        conversation_history: list[ChatMessage],
        available_tools: Optional[list[ToolDefinition]] = None,
    ) -> AgentMessage:
        """Generate a response using Protocol types."""
        pass

    @abstractmethod
    async def stream(
        self,
        conversation_history: list[ChatMessage],
        available_tools: Optional[list[ToolDefinition]] = None,
    ) -> AsyncIterator[AgentMessageDelta]:
        """Stream a response using Protocol types."""
        pass
```

### OpenAIProtocolClient

```python
class OpenAIProtocolClient(ProtocolLLMClient):
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        base_url: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        seed: Optional[int] = None,
    ):
        """Create OpenAI protocol client."""
        ...
```

### MockProtocolLLMClient

```python
class MockProtocolLLMClient(ProtocolLLMClient):
    def enqueue_response(self, message: AgentMessage): ...
    def enqueue_text_response(self, text: str): ...
    def enqueue_tool_call_response(self, tool_name: str, arguments: str): ...
    def reset(self): ...

    @property
    def call_history(self) -> list: ...

    @property
    def call_count(self) -> int: ...
```

## Architecture

```
User Input
    ↓
Agent Protocol Types (UserMessage, TextContent, etc.)
    ↓
IProtocolLLMClient
    ↓
[Internal conversion in client]
    ↓
Provider API (OpenAI/Claude/etc)
    ↓
[Internal conversion in client]
    ↓
Agent Protocol Types (AgentMessage, FunctionCallContent, etc.)
    ↓
Output
```

**Key Point**: Conversions happen inside the client implementation, not in your code!

## License

MIT

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for details.
