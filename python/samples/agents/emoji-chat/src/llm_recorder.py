# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
LLM Recording and Replay functionality for deterministic testing.
Based on the .NET LLMRecorder implementation.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class LLMRecorder:
    """Records LLM request/response pairs for test replay."""

    def __init__(self, recordings_dir: str):
        """Initialize recorder.

        Args:
            recordings_dir: Directory to store recorded interactions
        """
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.call_count = 0

    def hash_request(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.0
    ) -> str:
        """Generate deterministic hash for LLM request.

        Args:
            model: Model name
            messages: Conversation messages
            tools: Optional tool definitions
            temperature: Temperature setting

        Returns:
            Hex-encoded SHA256 hash of request (first 16 chars)
        """
        # Normalize request for hashing
        normalized = {
            "model": model,
            "messages": self._normalize_messages(messages),
            "temperature": temperature
        }

        if tools:
            normalized["tools"] = self._normalize_tools(tools)

        # Convert to JSON string for hashing (sorted keys for determinism)
        json_str = json.dumps(normalized, sort_keys=True, ensure_ascii=True)

        # Generate hash
        hash_obj = hashlib.sha256(json_str.encode("utf-8"))
        return hash_obj.hexdigest()[:16]  # First 16 chars for readability

    def _normalize_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize messages for consistent hashing."""
        normalized = []
        for msg in messages:
            if hasattr(msg, 'model_dump'):  # Pydantic model
                msg = msg.model_dump()

            norm_msg = {
                "role": msg.get("role"),
                "content": msg.get("content") or ""
            }
            normalized.append(norm_msg)
        return normalized

    def _normalize_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize tool definitions for consistent hashing."""
        normalized = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                norm_tool = {
                    "type": "function",
                    "function": {
                        "name": func.get("name"),
                        "description": func.get("description"),
                        "parameters": func.get("parameters")
                    }
                }
                normalized.append(norm_tool)
        return normalized

    async def record_async(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        response: Any
    ):
        """Record an LLM interaction.

        Args:
            model: Model name
            messages: Request messages
            tools: Optional tools
            response: LLM response object
        """
        hash_key = self.hash_request(model, messages, tools)
        self.call_count += 1

        # Save request for debugging
        request_path = self.recordings_dir / f"{hash_key}.request.json"
        with open(request_path, "w") as f:
            json.dump({
                "model": model,
                "messages": self._normalize_messages(messages),
                "tools": self._normalize_tools(tools) if tools else None,
                "call_number": self.call_count
            }, f, indent=2)

        # Save response
        response_path = self.recordings_dir / f"{hash_key}.response.json"

        # Extract response content
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
        else:
            content = str(response)

        with open(response_path, "w") as f:
            json.dump({
                "content": content,
                "call_number": self.call_count
            }, f, indent=2)

        print(f"  💾 Saved recording #{self.call_count}: {hash_key}")


class LLMPlayer:
    """Replays recorded LLM responses for deterministic testing."""

    def __init__(self, recordings_dir: str):
        """Initialize player.

        Args:
            recordings_dir: Directory containing recorded interactions
        """
        self.recordings_dir = Path(recordings_dir)
        self.call_count = 0

    def hash_request(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate hash - same as recorder."""
        recorder = LLMRecorder(str(self.recordings_dir))
        return recorder.hash_request(model, messages, tools)

    async def replay_async(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Replay a recorded LLM response.

        Args:
            model: Model name
            messages: Request messages
            tools: Optional tools

        Returns:
            Recorded response content

        Raises:
            FileNotFoundError: If no recording exists
        """
        hash_key = self.hash_request(model, messages, tools)
        self.call_count += 1

        response_path = self.recordings_dir / f"{hash_key}.response.json"

        if not response_path.exists():
            raise FileNotFoundError(
                f"No recording found for request. "
                f"Expected: {response_path}\n"
                f"Run with RECORD_LLM=true to create recordings."
            )

        with open(response_path, "r") as f:
            response_data = json.load(f)

        print(f"  ▶️  Replayed recording #{self.call_count}: {hash_key}")
        return response_data["content"]
