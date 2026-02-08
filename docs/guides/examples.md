# Code Examples

This page contains working code examples for common Agent Protocol tasks.

!!! tip "Test-Driven Examples"
    All examples on this page are extracted from actual test files and are guaranteed to work.
    They are automatically validated as part of our test suite.

## Protocol Client

### Quick Start

Connect to an Agent Protocol API and execute a run:

{% include-test-all "protocol-client-quickstart" %}

## XML Message Serialization

### Basic XML Serialization

Create and serialize a simple user message to XML format.

{% include-test-all "basic-xml-serialization" %}

## System Messages

Create system instruction messages that guide agent behavior.

{% include-test-all "system-message" %}

## User Messages

Create user input messages with text content.

{% include-test-all "user-message" %}

## Agent Messages

Create agent response messages.

{% include-test-all "agent-message" %}

## Multimodal Messages

Create messages with multiple content types (text + images).

{% include-test-all "multimodal-message" %}

## Tool Call Messages

Create messages that represent function/tool calls.

{% include-test-all "tool-call-message" %}

## Tool Result Messages

Create messages with tool execution results.

{% include-test-all "tool-result-message" %}

## Error Handling

Handle and represent errors in agent conversations.

{% include-test-all "error-content" %}

## Message Metadata

Add custom metadata to messages.

{% include-test-all "message-with-metadata" %}

## Conversation Threads

Work with conversation threads and message history.

{% include-test-all "thread-messages" %}

## Source Files

These examples are extracted from the following test files:

- **Python**: [test_doc_examples.py](https://github.com/madsbolaris/AgentFramework/blob/main/python/microsoft-agents-xml/tests/test_doc_examples.py)
- **C#**: [DocExampleTests.cs](https://github.com/madsbolaris/AgentFramework/blob/main/dotnet/tests/Microsoft.Agents.Xml.Tests/AgentXml.CodeGen.Tests/DocExampleTests.cs)

To run these examples yourself:

```bash
# Python
cd python/microsoft-agents-xml
pytest tests/test_doc_examples.py -v

# C#
cd dotnet/tests/Microsoft.Agents.Xml.Tests
dotnet test
```
