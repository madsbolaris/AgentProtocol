"""
LLM Recording and Replay functionality.

Handles deterministic hash generation and loading of recorded LLM responses.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class LLMRecorder:
    """Records and replays LLM API interactions for deterministic testing.

    Uses content-based hashing to match requests to recorded responses.
    """

    def __init__(self, recordings_dir: Path):
        """Initialize recorder.

        Args:
            recordings_dir: Directory containing recorded interactions
        """
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

    def hash_request(
        self,
        model: str,
        messages: list,
        tools: Optional[list] = None,
        temperature: float = 0.0,
        seed: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate deterministic hash for LLM request.

        The hash is based on:
        - Model name
        - Message content (roles and content)
        - Tool definitions (names and parameters)
        - Temperature
        - Seed

        Args:
            model: Model name
            messages: Conversation messages
            tools: Function tool definitions
            temperature: Temperature setting
            seed: Random seed
            **kwargs: Other parameters

        Returns:
            Hex-encoded SHA256 hash of request
        """
        # Normalize request for hashing
        normalized = {
            "model": model,
            "messages": self._normalize_messages(messages),
            "tools": self._normalize_tools(tools) if tools else None,
            "temperature": temperature,
            "seed": seed,
        }

        # Convert to JSON string for hashing
        json_str = json.dumps(normalized, sort_keys=True, ensure_ascii=True)

        # Generate hash
        hash_obj = hashlib.sha256(json_str.encode("utf-8"))
        return hash_obj.hexdigest()[:16]  # Use first 16 chars for readability

    def _normalize_messages(self, messages: list) -> List[Dict[str, Any]]:
        """Normalize messages for consistent hashing.

        Args:
            messages: Raw message list

        Returns:
            Normalized message list
        """
        normalized = []
        for msg in messages:
            norm_msg = {
                "role": msg.get("role"),
                "content": msg.get("content"),
            }

            # Include tool calls if present
            if "tool_calls" in msg and msg["tool_calls"]:
                norm_msg["tool_calls"] = [
                    {
                        "id": tc.get("id"),
                        "type": tc.get("type"),
                        "function": {
                            "name": tc.get("function", {}).get("name"),
                            "arguments": tc.get("function", {}).get("arguments"),
                        }
                    }
                    for tc in msg["tool_calls"]
                ]

            # Include tool_call_id if present (for tool responses)
            if "tool_call_id" in msg:
                norm_msg["tool_call_id"] = msg["tool_call_id"]

            # Include name if present
            if "name" in msg:
                norm_msg["name"] = msg["name"]

            normalized.append(norm_msg)

        return normalized

    def _normalize_tools(self, tools: list) -> List[Dict[str, Any]]:
        """Normalize tool definitions for consistent hashing.

        Args:
            tools: Raw tool list

        Returns:
            Normalized tool list
        """
        normalized = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool.get("function", {})
                norm_tool = {
                    "type": "function",
                    "function": {
                        "name": func.get("name"),
                        "description": func.get("description"),
                        "parameters": func.get("parameters"),
                    }
                }
                normalized.append(norm_tool)

        return normalized

    def load_response(self, hash_key: str) -> Dict[str, Any]:
        """Load recorded response for hash key.

        Args:
            hash_key: Request hash from hash_request()

        Returns:
            Recorded response data

        Raises:
            FileNotFoundError: If no recording exists
        """
        response_path = self.recordings_dir / f"{hash_key}.response.json"

        if not response_path.exists():
            raise FileNotFoundError(f"No recording found: {response_path}")

        with open(response_path, "r") as f:
            return json.load(f)

    def save_response(self, hash_key: str, response_data: Dict[str, Any]):
        """Save LLM response for future replay.

        Args:
            hash_key: Request hash from hash_request()
            response_data: Response data to save
        """
        response_path = self.recordings_dir / f"{hash_key}.response.json"

        with open(response_path, "w") as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)

        print(f"  💾 Saved recording: {hash_key}.response.json")

    def save_request(self, hash_key: str, request_data: Dict[str, Any]):
        """Save request data for debugging.

        Args:
            hash_key: Request hash from hash_request()
            request_data: Request data to save
        """
        request_path = self.recordings_dir / f"{hash_key}.request.json"

        with open(request_path, "w") as f:
            json.dump(request_data, f, indent=2, ensure_ascii=False)
