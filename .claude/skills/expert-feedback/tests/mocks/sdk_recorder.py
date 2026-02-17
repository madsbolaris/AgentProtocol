"""
SDK Recorder for recording and replaying Claude Agent SDK interactions.

This module provides functionality to record LLM interactions during test generation
and replay them during test execution, eliminating the need for real API calls.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class SDKRecorder:
    """
    Records and replays Claude Agent SDK interactions.

    Uses request hashing to match requests with recorded responses,
    enabling deterministic and fast test execution.
    """

    def __init__(self, recordings_dir: Path):
        """
        Initialize SDK recorder.

        Args:
            recordings_dir: Directory where recordings are stored
        """
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)

    def hash_request(
        self,
        prompt: Optional[str] = None,
        system: Optional[List[Any]] = None,
        messages: Optional[List[Any]] = None,
        options: Optional[Any] = None
    ) -> str:
        """
        Generate consistent hash for a request.

        The hash is based on the content of the request, excluding:
        - Session IDs (vary between test runs)
        - Timestamps
        - Random elements

        Args:
            prompt: User prompt text
            system: System messages
            messages: Conversation messages
            options: Request options

        Returns:
            16-character hex hash
        """
        # Normalize request components
        normalized = self._normalize_request(prompt, system, messages, options)

        # Create stable JSON representation
        request_json = json.dumps(normalized, sort_keys=True, ensure_ascii=False)

        # Hash to get stable identifier
        hash_obj = hashlib.sha256(request_json.encode('utf-8'))
        return hash_obj.hexdigest()[:16]  # Use first 16 chars for readability

    def _normalize_request(
        self,
        prompt: Optional[str],
        system: Optional[List[Any]],
        messages: Optional[List[Any]],
        options: Optional[Any]
    ) -> Dict[str, Any]:
        """
        Normalize request for consistent hashing.

        Args:
            prompt: User prompt
            system: System messages
            messages: Conversation messages
            options: Request options

        Returns:
            Normalized dictionary
        """
        normalized = {}

        # Normalize prompt (handle both string and list)
        if prompt:
            if isinstance(prompt, str):
                normalized["prompt"] = prompt.strip()
            elif isinstance(prompt, list):
                # Prompt is a list of system blocks (cache-controlled prompts)
                normalized["prompt"] = self._normalize_messages(prompt)
            else:
                normalized["prompt"] = prompt

        # Normalize system messages
        if system:
            normalized["system"] = self._normalize_messages(system)

        # Normalize conversation messages
        if messages:
            normalized["messages"] = self._normalize_messages(messages)

        # Normalize options (exclude session IDs and non-deterministic fields)
        if options:
            normalized["options"] = self._normalize_options(options)

        return normalized

    def _normalize_messages(self, messages: List[Any]) -> List[Dict[str, Any]]:
        """
        Normalize message list for hashing.

        Args:
            messages: List of message objects or dicts

        Returns:
            Normalized message list
        """
        normalized = []

        for msg in messages:
            # Convert to dict if it's an object
            if hasattr(msg, 'model_dump'):
                msg_dict = msg.model_dump()
            elif hasattr(msg, 'to_dict'):
                msg_dict = msg.to_dict()
            elif isinstance(msg, dict):
                msg_dict = msg.copy()
            else:
                # String or other type
                msg_dict = {"content": str(msg)}

            # Keep only relevant fields for hashing
            normalized_msg = {}
            if "role" in msg_dict:
                normalized_msg["role"] = msg_dict["role"]
            if "content" in msg_dict:
                # Handle content blocks
                if isinstance(msg_dict["content"], list):
                    normalized_msg["content"] = self._normalize_content_blocks(
                        msg_dict["content"]
                    )
                elif isinstance(msg_dict["content"], str):
                    normalized_msg["content"] = msg_dict["content"].strip()
            if "tool_calls" in msg_dict and msg_dict["tool_calls"]:
                normalized_msg["tool_calls"] = msg_dict["tool_calls"]
            if "tool_use_id" in msg_dict:
                normalized_msg["tool_use_id"] = msg_dict["tool_use_id"]

            normalized.append(normalized_msg)

        return normalized

    def _normalize_content_blocks(self, blocks: List[Any]) -> List[Dict[str, Any]]:
        """
        Normalize content blocks (text, tool_use, etc.).

        Args:
            blocks: List of content blocks

        Returns:
            Normalized blocks
        """
        normalized = []

        for block in blocks:
            if hasattr(block, 'model_dump'):
                block_dict = block.model_dump()
            elif hasattr(block, 'to_dict'):
                block_dict = block.to_dict()
            elif isinstance(block, dict):
                block_dict = block.copy()
            else:
                continue

            # Keep only relevant fields
            normalized_block = {"type": block_dict.get("type")}

            if block_dict.get("type") == "text":
                normalized_block["text"] = block_dict.get("text", "").strip()
            elif block_dict.get("type") == "tool_use":
                normalized_block["name"] = block_dict.get("name")
                normalized_block["input"] = block_dict.get("input")

            normalized.append(normalized_block)

        return normalized

    def _normalize_options(self, options: Any) -> Dict[str, Any]:
        """
        Normalize request options for hashing.

        Excludes session IDs and other non-deterministic fields.

        Args:
            options: ClaudeAgentOptions object or dict

        Returns:
            Normalized options dict
        """
        if hasattr(options, 'model_dump'):
            options_dict = options.model_dump()
        elif hasattr(options, 'to_dict'):
            options_dict = options.to_dict()
        elif isinstance(options, dict):
            options_dict = options.copy()
        else:
            return {}

        # Include only deterministic options
        normalized = {}

        deterministic_fields = [
            "temperature",
            "max_tokens",
            "top_p",
            "top_k",
            "stop_sequences",
            "model"
        ]

        for field in deterministic_fields:
            if field in options_dict and options_dict[field] is not None:
                normalized[field] = options_dict[field]

        return normalized

    def save_interaction(
        self,
        request_hash: str,
        request_data: Dict[str, Any],
        events: List[Dict[str, Any]]
    ) -> None:
        """
        Save a recorded interaction.

        Args:
            request_hash: Hash of the request
            request_data: Original request data
            events: List of stream events from response
        """
        # Create llm-recordings subdirectory for organized storage
        llm_recordings_dir = self.recordings_dir / "llm-recordings"
        llm_recordings_dir.mkdir(parents=True, exist_ok=True)

        # Save request (in llm-recordings subdirectory)
        request_file = llm_recordings_dir / f"{request_hash}.request.json"
        with open(request_file, 'w', encoding='utf-8') as f:
            json.dump(request_data, f, indent=2, ensure_ascii=False)

        # Save response events (in llm-recordings subdirectory)
        response_file = llm_recordings_dir / f"{request_hash}.response.json"
        response_data = {"events": events}
        with open(response_file, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)

        print(f"  💾 Recorded interaction: {request_hash}")

    def load_response(self, request_hash: str) -> List[Dict[str, Any]]:
        """
        Load recorded response for a request.

        Args:
            request_hash: Hash of the request

        Returns:
            List of stream events

        Raises:
            FileNotFoundError: If no recording exists for this hash
        """
        # Try new location first (llm-recordings subdirectory)
        response_file = self.recordings_dir / "llm-recordings" / f"{request_hash}.response.json"

        # Fall back to old location (backward compatibility)
        if not response_file.exists():
            response_file = self.recordings_dir / f"{request_hash}.response.json"

        if not response_file.exists():
            raise FileNotFoundError(
                f"No recording found for request hash: {request_hash}\n"
                f"Expected file: {self.recordings_dir / 'llm-recordings' / f'{request_hash}.response.json'}\n"
                f"  or (old location): {self.recordings_dir / f'{request_hash}.response.json'}\n"
                f"\n"
                f"This usually means:\n"
                f"1. Tests need to be run in record mode first: EXPERT_FEEDBACK_TEST_MODE=record\n"
                f"2. The request parameters have changed (different hash)\n"
                f"3. The recording file was deleted\n"
                f"\n"
                f"To generate recordings, run:\n"
                f"  EXPERT_FEEDBACK_TEST_MODE=record pytest tests/integration/ -v\n"
            )

        with open(response_file, 'r', encoding='utf-8') as f:
            response_data = json.load(f)

        return response_data.get("events", [])

    def load_request(self, request_hash: str) -> Dict[str, Any]:
        """
        Load recorded request data.

        Args:
            request_hash: Hash of the request

        Returns:
            Original request data

        Raises:
            FileNotFoundError: If no recording exists
        """
        # Try new location first (llm-recordings subdirectory)
        request_file = self.recordings_dir / "llm-recordings" / f"{request_hash}.request.json"

        # Fall back to old location (backward compatibility)
        if not request_file.exists():
            request_file = self.recordings_dir / f"{request_hash}.request.json"

        if not request_file.exists():
            raise FileNotFoundError(f"No request recording found: {request_file}")

        with open(request_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def has_recording(self, request_hash: str) -> bool:
        """
        Check if recording exists for a request hash.

        Args:
            request_hash: Hash to check

        Returns:
            True if recording exists
        """
        # Try new location first (llm-recordings subdirectory)
        new_location = self.recordings_dir / "llm-recordings" / f"{request_hash}.response.json"
        if new_location.exists():
            return True

        # Fall back to old location (backward compatibility)
        old_location = self.recordings_dir / f"{request_hash}.response.json"
        return old_location.exists()

    def list_recordings(self) -> List[str]:
        """
        List all available recording hashes.

        Returns:
            List of request hashes
        """
        hashes = set()

        # Check new location (llm-recordings subdirectory)
        llm_recordings_dir = self.recordings_dir / "llm-recordings"
        if llm_recordings_dir.exists():
            for f in llm_recordings_dir.glob("*.response.json"):
                hashes.add(f.stem.replace(".response", ""))

        # Check old location (backward compatibility)
        for f in self.recordings_dir.glob("*.response.json"):
            hashes.add(f.stem.replace(".response", ""))

        return sorted(hashes)

    def clear_recordings(self) -> None:
        """Delete all recordings in the directory."""
        for file in self.recordings_dir.glob("*.json"):
            file.unlink()

        print(f"  🗑️  Cleared all recordings from {self.recordings_dir}")
