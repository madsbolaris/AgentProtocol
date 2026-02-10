# Microsoft Agents Protocol Model - Testing Utilities

Testing utilities for Microsoft Agents Protocol LLM clients.

This package provides mock and testing utilities for Protocol LLM clients, making it easy to test your agents without making actual API calls.

## Installation

```bash
pip install microsoft-agents-protocol-model-testing
```

## Usage

```python
from microsoft.agents.protocol.model.testing import MockProtocolLLMClient

# Create a mock client for testing
mock_client = MockProtocolLLMClient()

# Configure mock responses
mock_client.set_response("Hello!")

# Use in tests
response = await mock_client.generate(conversation_history)
assert response.content[0].text == "Hello!"
```

## Version

0.2.0
