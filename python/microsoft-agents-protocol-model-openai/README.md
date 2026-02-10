# Microsoft Agents Protocol Model - OpenAI Provider

OpenAI provider implementation for Microsoft Agents Protocol.

This package provides an OpenAI-specific implementation of the Protocol LLM Client, allowing you to use OpenAI's models with Agent Protocol types natively.

## Installation

```bash
pip install microsoft-agents-protocol-model-openai
```

## Usage

```python
from microsoft.agents.protocol.model.openai import OpenAIProtocolClient

# Create an OpenAI Protocol LLM Client
client = OpenAIProtocolClient(api_key="your-api-key", model="gpt-4")

# Use with Agent Protocol types
response = await client.generate(conversation_history)
```

## Version

0.2.0
