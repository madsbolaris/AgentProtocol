# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Testing wrapper for OpenAI AsyncOpenAI that supports recording and playback of LLM interactions.
This enables deterministic testing by recording real LLM responses and playing them back.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class TestingChatClient:
    """Testing wrapper for AsyncOpenAI that supports recording and playback of LLM interactions."""

    def __init__(
        self,
        real_client: Optional[Any],
        recordings_dir: str,
        model_id: str,
        record_mode: bool = False,
        playback_mode: bool = False
    ):
        """Initialize TestingChatClient.

        Args:
            real_client: Real AsyncOpenAI client (required for normal and recording mode)
            recordings_dir: Directory for storing/loading recordings
            model_id: Model identifier
            record_mode: If True, records LLM interactions to disk
            playback_mode: If True, replays recorded LLM interactions

        Raises:
            ValueError: If both record_mode and playback_mode are enabled
            ValueError: If record_mode is enabled without a real_client
            FileNotFoundError: If playback_mode is enabled but recordings_dir doesn't exist
        """
        if record_mode and playback_mode:
            raise ValueError("Cannot enable both record and playback mode simultaneously")

        if record_mode and real_client is None:
            raise ValueError("Real client required for recording mode")

        recordings_path = Path(recordings_dir)
        if playback_mode and not recordings_path.exists():
            raise FileNotFoundError(f"Recordings directory not found: {recordings_dir}")

        self._real_client = real_client
        self._recordings_dir = recordings_path
        self._model_id = model_id
        self._record_mode = record_mode
        self._playback_mode = playback_mode
        self._call_count = 0

        if self._record_mode:
            self._recordings_dir.mkdir(parents=True, exist_ok=True)
            print(f"📹 LLM Recording enabled: {self._recordings_dir}")
        elif self._playback_mode:
            print(f"▶️  LLM Playback enabled: {self._recordings_dir}")
            print("   Using recorded LLM responses (test mode)")

    async def create_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        """Create a chat completion, either by calling the real LLM or replaying a recording.

        Args:
            messages: List of conversation messages
            tools: Optional list of tool definitions
            **kwargs: Additional arguments (ignored for hashing compatibility)

        Returns:
            Chat completion response (either real or replayed)
        """
        self._call_count += 1
        call_id = self._call_count
        hash_key = self._compute_request_hash(messages, tools)

        if self._playback_mode:
            return await self._playback_response(call_id, hash_key, messages, tools)

        # Call real LLM (works in both normal and recording mode)
        if self._real_client is None:
            raise ValueError("Real client not available. Use recording mode with a valid AsyncOpenAI client.")

        response = await self._real_client.chat.completions.create(
            model=self._model_id,
            messages=messages,
            tools=tools if tools else None,
            **kwargs
        )

        if self._record_mode:
            await self._record_interaction(call_id, hash_key, messages, tools, response)

        return response

    async def _playback_response(
        self,
        call_id: int,
        hash_key: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]]
    ):
        """Replay a recorded LLM response.

        Args:
            call_id: Sequential call number
            hash_key: Hash of the request
            messages: Request messages
            tools: Request tools

        Returns:
            Mock completion object matching the recorded response

        Raises:
            FileNotFoundError: If no recording exists for this hash
        """
        response_file = self._recordings_dir / f"{hash_key}.response.json"

        if not response_file.exists():
            raise FileNotFoundError(
                f"No recorded LLM response found for request hash: {hash_key}\n"
                f"Expected file: {response_file}\n\n"
                f"This usually means:\n"
                f"1. Tests need to be run in generation mode first: RECORD_LLM=true\n"
                f"2. The request parameters have changed (different hash)\n"
                f"3. The recording file was deleted\n\n"
                f"Request details:\n"
                f"  Messages: {len(messages)} messages\n"
                f"  Tools: {'provided' if tools else 'null'}\n"
            )

        print(f"  ▶️  Replaying LLM call #{call_id}: {hash_key}")

        with open(response_file, 'r') as f:
            recording = json.load(f)

        response_data = recording["response"]
        return self._deserialize_completion(response_data)

    async def _record_interaction(
        self,
        call_id: int,
        hash_key: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        response: Any
    ):
        """Record an LLM interaction to disk.

        Args:
            call_id: Sequential call number
            hash_key: Hash of the request
            messages: Request messages
            tools: Request tools
            response: LLM response to record
        """
        print(f"  📹 Recording LLM call #{call_id}: {hash_key}")

        # Save request
        request_file = self._recordings_dir / f"{hash_key}.request.json"
        request_data = {
            "callId": call_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "hash": hash_key,
            "model": self._model_id,
            "messages": self._normalize_messages(messages),
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": t["function"]["name"],
                        "description": t["function"].get("description", ""),
                        "parameters": t["function"].get("parameters", {})
                    }
                }
                for t in (tools or [])
            ] if tools else None
        }

        with open(request_file, 'w') as f:
            json.dump(request_data, f, indent=2)

        # Save response
        response_file = self._recordings_dir / f"{hash_key}.response.json"
        choice = response.choices[0]

        # Extract content
        content_list = []
        if choice.message.content:
            content_list.append({"text": choice.message.content})

        # Extract tool calls
        tool_calls_list = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls_list.append({
                    "id": tc.id,
                    "type": "Function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })

        response_data = {
            "callId": call_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "hash": hash_key,
            "response": {
                "id": response.id,
                "model": response.model,
                "created": response.created,
                "finishReason": choice.finish_reason.title() if choice.finish_reason else "Stop",
                "content": content_list,
                "toolCalls": tool_calls_list
            }
        }

        with open(response_file, 'w') as f:
            json.dump(response_data, f, indent=2)

    def _compute_request_hash(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Compute SHA256 hash of request parameters.

        Uses exact same algorithm as C# TestingChatClient for compatibility.

        Args:
            messages: Conversation messages
            tools: Tool definitions

        Returns:
            First 16 characters of SHA256 hash (lowercase hex)
        """
        # Build request dict matching C# format exactly
        request_dict = {
            "model": self._model_id,
            "messages": self._normalize_messages(messages),
            "temperature": 0.0
        }

        if tools:
            request_dict["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t["function"]["name"],
                        "description": t["function"].get("description", ""),
                        "parameters": json.dumps(t["function"].get("parameters", {}), separators=(',', ':'))
                    }
                }
                for t in tools
            ]

        # Serialize to JSON with sorted keys
        # IMPORTANT: ensure_ascii=False keeps Unicode characters (emojis, arrows) unescaped
        # This matches C# JSON serialization for consistent cross-language hashing
        json_str = json.dumps(request_dict, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

        # Log the JSON being hashed for debugging
        print(f"🔍 [Python] Computing hash for:")
        print(f"   JSON length: {len(json_str)} chars")
        print(f"   FULL JSON: {json_str}")
        with open('/tmp/python_json.txt', 'w') as f:
            f.write(json_str)

        # Hash and truncate (SHA256, first 16 chars)
        hash_obj = hashlib.sha256(json_str.encode('utf-8'))
        hash_str = hash_obj.hexdigest()[:16].lower()
        print(f"   Hash: {hash_str}")
        return hash_str

    def _normalize_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize messages for consistent hashing.

        Args:
            messages: Raw message list

        Returns:
            Normalized message list matching C# format
        """
        normalized = []
        for msg in messages:
            norm_msg = {"role": msg["role"]}

            # Add content if present
            if "content" in msg and msg["content"] is not None:
                norm_msg["content"] = msg["content"]

            # Add tool_calls if present
            if "tool_calls" in msg and msg["tool_calls"]:
                norm_msg["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": tc.get("type", "function"),
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"]
                        }
                    }
                    for tc in msg["tool_calls"]
                ]

            # Add tool_call_id if present
            if "tool_call_id" in msg:
                norm_msg["tool_call_id"] = msg["tool_call_id"]

            normalized.append(norm_msg)

        return normalized

    def _deserialize_completion(self, response_element: Dict[str, Any]):
        """Deserialize recorded completion data into a mock completion object.

        Args:
            response_element: Recorded response data

        Returns:
            Mock completion object compatible with OpenAI response format
        """
        completion_id = response_element.get("id", "mock-completion")
        model = response_element.get("model", "unknown")
        finish_reason_str = response_element.get("finishReason", "Stop")

        # Map finish reason
        finish_reason_map = {
            "ToolCalls": "tool_calls",
            "Stop": "stop",
            "Length": "length"
        }
        finish_reason = finish_reason_map.get(finish_reason_str, "stop")

        # Parse content
        content = None
        content_array = response_element.get("content", [])
        if content_array and len(content_array) > 0:
            content = content_array[0].get("text", "")

        # Parse tool calls
        tool_calls = None
        tool_calls_array = response_element.get("toolCalls", [])
        if tool_calls_array:
            class MockFunction:
                def __init__(self, name: str, arguments: str):
                    self.name = name
                    self.arguments = arguments

            class MockToolCall:
                def __init__(self, tc_data: Dict[str, Any]):
                    self.id = tc_data["id"]
                    self.type = tc_data.get("type", "function").lower()
                    func_data = tc_data["function"]
                    self.function = MockFunction(
                        func_data["name"],
                        func_data["arguments"]
                    )

            tool_calls = [MockToolCall(tc) for tc in tool_calls_array]

        # Build mock completion object
        class MockMessage:
            def __init__(self, content, tool_calls):
                self.content = content
                self.tool_calls = tool_calls
                self.role = "assistant"

        class MockChoice:
            def __init__(self, finish_reason, message):
                self.finish_reason = finish_reason
                self.message = message
                self.index = 0

        class MockCompletion:
            def __init__(self, completion_id, model, choices):
                self.id = completion_id
                self.model = model
                self.choices = choices
                self.created = int(datetime.utcnow().timestamp())

        message = MockMessage(content, tool_calls)
        choice = MockChoice(finish_reason, message)
        return MockCompletion(completion_id, model, [choice])
