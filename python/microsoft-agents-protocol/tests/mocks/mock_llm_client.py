"""
Mock LLM Client for test mode.

Replays recorded LLM responses instead of making real API calls.
"""

from typing import Any, Dict, List, Optional
from pathlib import Path
from .llm_recorder import LLMRecorder


class MockLLMClient:
    """Mock OpenAI client that replays recorded responses.

    Uses recorded request/response pairs from generation mode to provide
    deterministic, fast, free LLM responses for testing.

    Example:
        mock_client = MockLLMClient(Path("test-data/llm-recordings/sample/basic-m365"))
        completion = await mock_client.chat.completions.create(...)
        # Returns recorded response, no API call
    """

    def __init__(self, recordings_dir: Path):
        """Initialize mock client.

        Args:
            recordings_dir: Directory containing recorded interactions
        """
        self.recorder = LLMRecorder(recordings_dir)
        self.call_count = 0

        # Provide chat.completions namespace
        self.chat = _MockChatNamespace(self)

    async def _replay_response(
        self,
        model: str,
        messages: list,
        tools: Optional[list] = None,
        temperature: float = 0.0,
        seed: Optional[int] = None,
        **kwargs
    ) -> "MockChatCompletion":
        """Replay recorded response for this request.

        Args:
            model: Model name
            messages: Conversation messages
            tools: Function tool definitions
            temperature: Temperature setting
            seed: Random seed
            **kwargs: Other parameters

        Returns:
            MockChatCompletion with recorded response

        Raises:
            FileNotFoundError: If no recording exists for this request
        """
        self.call_count += 1

        # Generate hash to find recording
        hash_key = self.recorder.hash_request(
            model=model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            seed=seed,
            **kwargs
        )

        # Load recorded response
        try:
            response_data = self.recorder.load_response(hash_key)
        except FileNotFoundError as e:
            # Provide helpful error message
            raise FileNotFoundError(
                f"No recorded LLM response found for request hash: {hash_key}\n"
                f"Expected file: {self.recorder.recordings_dir}/{hash_key}.response.json\n"
                f"\n"
                f"This usually means:\n"
                f"1. Tests need to be run in generation mode first: TEST_MODE=generate\n"
                f"2. The request parameters have changed (different hash)\n"
                f"3. The recording file was deleted\n"
                f"\n"
                f"Request details:\n"
                f"  Model: {model}\n"
                f"  Messages: {len(messages)} messages\n"
                f"  Tools: {len(tools) if tools else 0} tools\n"
                f"  Temperature: {temperature}\n"
                f"  Seed: {seed}\n"
            ) from e

        # Log replay
        print(f"  ▶️  Replaying LLM call #{self.call_count}: {hash_key}")

        # Convert recorded data to mock response object
        return MockChatCompletion.from_dict(response_data)


class MockChatCompletion:
    """Mock ChatCompletion response object.

    Mimics the structure of OpenAI's ChatCompletion response.
    """

    def __init__(
        self,
        id: str,
        object: str,
        created: int,
        model: str,
        choices: List["MockChoice"],
        usage: Optional[Dict[str, int]] = None
    ):
        self.id = id
        self.object = object
        self.created = created
        self.model = model
        self.choices = choices
        self.usage = MockUsage(**usage) if usage else None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MockChatCompletion":
        """Create MockChatCompletion from recorded dict.

        Args:
            data: Dictionary from recorded response

        Returns:
            MockChatCompletion instance
        """
        choices = [
            MockChoice.from_dict(choice_data)
            for choice_data in data.get("choices", [])
        ]

        return cls(
            id=data.get("id", "mock-completion"),
            object=data.get("object", "chat.completion"),
            created=data.get("created", 0),
            model=data.get("model", "unknown"),
            choices=choices,
            usage=data.get("usage")
        )

    def model_dump(self, exclude_none: bool = True) -> Dict[str, Any]:
        """Convert to dictionary (Pydantic-style).

        Args:
            exclude_none: Whether to exclude None values

        Returns:
            Dictionary representation
        """
        result = {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [choice.to_dict() for choice in self.choices],
        }

        if self.usage:
            result["usage"] = {
                "prompt_tokens": self.usage.prompt_tokens,
                "completion_tokens": self.usage.completion_tokens,
                "total_tokens": self.usage.total_tokens,
            }

        return result


class MockChoice:
    """Mock Choice object from ChatCompletion."""

    def __init__(
        self,
        index: int,
        message: "MockMessage",
        finish_reason: str
    ):
        self.index = index
        self.message = message
        self.finish_reason = finish_reason

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MockChoice":
        """Create MockChoice from dict."""
        return cls(
            index=data.get("index", 0),
            message=MockMessage.from_dict(data.get("message", {})),
            finish_reason=data.get("finish_reason", "stop")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "index": self.index,
            "message": self.message.to_dict(),
            "finish_reason": self.finish_reason
        }


class MockMessage:
    """Mock Message object from ChatCompletion."""

    def __init__(
        self,
        role: str,
        content: Optional[str] = None,
        tool_calls: Optional[List["MockToolCall"]] = None,
        tool_call_id: Optional[str] = None
    ):
        self.role = role
        self.content = content
        self.tool_calls = tool_calls or []
        self.tool_call_id = tool_call_id

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MockMessage":
        """Create MockMessage from dict."""
        tool_calls = None
        if "tool_calls" in data and data["tool_calls"]:
            tool_calls = [
                MockToolCall.from_dict(tc_data)
                for tc_data in data["tool_calls"]
            ]

        return cls(
            role=data.get("role", "assistant"),
            content=data.get("content"),
            tool_calls=tool_calls,
            tool_call_id=data.get("tool_call_id")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "role": self.role,
            "content": self.content,
        }

        if self.tool_calls:
            result["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]

        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id

        return result


class MockToolCall:
    """Mock ToolCall object."""

    def __init__(self, id: str, type: str, function: "MockFunction"):
        self.id = id
        self.type = type
        self.function = function

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MockToolCall":
        """Create MockToolCall from dict."""
        return cls(
            id=data.get("id", "mock-tool-call"),
            type=data.get("type", "function"),
            function=MockFunction.from_dict(data.get("function", {}))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "function": self.function.to_dict()
        }


class MockFunction:
    """Mock Function object from ToolCall."""

    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MockFunction":
        """Create MockFunction from dict."""
        return cls(
            name=data.get("name", "unknown"),
            arguments=data.get("arguments", "{}")
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "arguments": self.arguments
        }


class MockUsage:
    """Mock Usage object."""

    def __init__(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int
    ):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class _MockChatNamespace:
    """Mock namespace for chat.completions methods."""

    def __init__(self, mock_client: MockLLMClient):
        self.completions = _MockCompletionsNamespace(mock_client)


class _MockCompletionsNamespace:
    """Mock namespace for chat.completions.create method."""

    def __init__(self, mock_client: MockLLMClient):
        self._mock_client = mock_client

    async def create(
        self,
        model: str,
        messages: list,
        tools: Optional[list] = None,
        temperature: float = 0.0,
        seed: Optional[int] = None,
        **kwargs
    ) -> MockChatCompletion:
        """Create chat completion from recording.

        Args:
            model: Model name
            messages: Conversation messages
            tools: Function tool definitions
            temperature: Temperature setting
            seed: Random seed
            **kwargs: Other parameters

        Returns:
            MockChatCompletion with recorded response
        """
        return await self._mock_client._replay_response(
            model=model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            seed=seed,
            **kwargs
        )
