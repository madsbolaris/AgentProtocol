# Microsoft Agents Protocol Model

LLM client abstractions for Microsoft Agents Protocol.

This package provides the core abstractions for Protocol-Native LLM clients that speak Agent Protocol types natively, eliminating the need for conversion layers between provider-specific types and Agent Protocol types.

## Installation

```bash
pip install microsoft-agents-protocol-model
```

## Usage

```python
from microsoft.agents.protocol.model import ProtocolLLMClient, LLMProviderInfo, ToolDefinition

# Implement your custom Protocol LLM Client
class MyProtocolLLMClient(ProtocolLLMClient):
    @property
    def provider_info(self) -> LLMProviderInfo:
        return LLMProviderInfo(provider="my-provider", model="my-model")

    async def generate(self, conversation_history, available_tools=None):
        # Your implementation here
        pass

    async def stream(self, conversation_history, available_tools=None):
        # Your streaming implementation here
        pass
```

## Version

0.2.0
