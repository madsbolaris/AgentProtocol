"""
Recording LLM Client wrapper for generation mode.

Wraps a real OpenAI client and records all interactions for later replay.
"""

from typing import Any, Dict, Optional
from openai import AsyncOpenAI
from .llm_recorder import LLMRecorder


class RecordingLLMClient:
    """Wrapper around AsyncOpenAI that records all interactions.

    Transparently proxies all calls to the real LLM client while recording
    request/response pairs for later replay in tests.

    Example:
        real_client = AsyncOpenAI(api_key="...", base_url="...")
        recorder = LLMRecorder(Path("recordings"))
        recording_client = RecordingLLMClient(real_client, recorder)

        # Use like normal client - automatically records
        completion = await recording_client.chat.completions.create(...)
    """

    def __init__(self, real_client: AsyncOpenAI, recorder: LLMRecorder):
        """Initialize recording client.

        Args:
            real_client: Real OpenAI client to wrap
            recorder: LLMRecorder instance for saving interactions
        """
        self.real_client = real_client
        self.recorder = recorder
        self.call_count = 0

        # Wrap the chat.completions namespace
        self.chat = _ChatNamespace(self)

    async def _record_and_call(
        self,
        model: str,
        messages: list,
        tools: Optional[list] = None,
        temperature: float = 0.0,
        seed: Optional[int] = None,
        **kwargs
    ) -> Any:
        """Record request, call real LLM, record response.

        Args:
            model: Model name
            messages: Conversation messages
            tools: Function tool definitions
            temperature: Temperature setting
            seed: Random seed
            **kwargs: Other OpenAI parameters

        Returns:
            ChatCompletion response from real LLM
        """
        self.call_count += 1

        # Generate hash for this request
        hash_key = self.recorder.hash_request(
            model=model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            seed=seed,
            **kwargs
        )

        # Build request data for recording
        request_data = {
            "model": model,
            "messages": self._serialize_messages(messages),
            "temperature": temperature,
        }

        if tools:
            request_data["tools"] = tools

        if seed is not None:
            request_data["seed"] = seed

        # Add other kwargs
        for key, value in kwargs.items():
            request_data[key] = value

        # Save request
        self.recorder.save_request(hash_key, request_data)

        # Call real LLM
        completion = await self.real_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            seed=seed,
            **kwargs
        )

        # Convert response to dict for recording
        response_data = self._serialize_response(completion)

        # Save response
        self.recorder.save_response(hash_key, response_data)

        # Log recording
        print(f"  📹 Recorded LLM call #{self.call_count}: {hash_key}")

        return completion

    def _serialize_messages(self, messages: list) -> list:
        """Serialize messages to dict format.

        Args:
            messages: List of message objects or dicts

        Returns:
            List of message dicts
        """
        serialized = []
        for msg in messages:
            if hasattr(msg, 'model_dump'):
                # OpenAI message object
                msg_dict = msg.model_dump(exclude_none=True)
            elif isinstance(msg, dict):
                msg_dict = msg
            else:
                # Convert to dict
                msg_dict = {
                    "role": getattr(msg, 'role', str(msg)),
                    "content": getattr(msg, 'content', None),
                }
                # Add tool_calls if present
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    msg_dict["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in msg.tool_calls
                    ]
                # Add tool_call_id if present
                if hasattr(msg, 'tool_call_id'):
                    msg_dict["tool_call_id"] = msg.tool_call_id

            serialized.append(msg_dict)

        return serialized

    def _serialize_response(self, completion: Any) -> Dict[str, Any]:
        """Serialize ChatCompletion response to dict.

        Args:
            completion: ChatCompletion response object

        Returns:
            Dictionary representation of response
        """
        # Handle both response types
        if hasattr(completion, 'model_dump'):
            # Pydantic model
            return completion.model_dump(exclude_none=True)
        else:
            # Convert to dict manually
            response_dict = {
                "id": completion.id,
                "object": completion.object,
                "created": completion.created,
                "model": completion.model,
                "choices": []
            }

            for choice in completion.choices:
                choice_dict = {
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content,
                    },
                    "finish_reason": choice.finish_reason
                }

                # Add tool_calls if present
                if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                    choice_dict["message"]["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in choice.message.tool_calls
                    ]

                response_dict["choices"].append(choice_dict)

            # Add usage if present
            if hasattr(completion, 'usage') and completion.usage:
                response_dict["usage"] = {
                    "prompt_tokens": completion.usage.prompt_tokens,
                    "completion_tokens": completion.usage.completion_tokens,
                    "total_tokens": completion.usage.total_tokens,
                }

            return response_dict


class _ChatNamespace:
    """Namespace for chat.completions methods."""

    def __init__(self, recording_client: RecordingLLMClient):
        self.completions = _CompletionsNamespace(recording_client)


class _CompletionsNamespace:
    """Namespace for chat.completions.create method."""

    def __init__(self, recording_client: RecordingLLMClient):
        self._recording_client = recording_client

    async def create(
        self,
        model: str,
        messages: list,
        tools: Optional[list] = None,
        temperature: float = 0.0,
        seed: Optional[int] = None,
        **kwargs
    ) -> Any:
        """Create chat completion with recording.

        Args:
            model: Model name
            messages: Conversation messages
            tools: Function tool definitions
            temperature: Temperature setting
            seed: Random seed
            **kwargs: Other OpenAI parameters

        Returns:
            ChatCompletion response
        """
        return await self._recording_client._record_and_call(
            model=model,
            messages=messages,
            tools=tools,
            temperature=temperature,
            seed=seed,
            **kwargs
        )
