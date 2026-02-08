"""
LLM Recorder for capturing and storing LLM interactions.

Records request/response pairs with deterministic hashing for replay in tests.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import fcntl
import os


class LLMRecorder:
    """Records LLM request/response pairs for test replay.

    Features:
    - Deterministic request hashing (SHA256)
    - File-based storage with atomic writes
    - Metadata tracking (timestamp, model, etc.)
    - Duplicate detection

    Example:
        recorder = LLMRecorder(Path("test-data/llm-recordings/function-tools"))
        hash_key = recorder.hash_request(model, messages, tools)
        recorder.save_request(hash_key, request_data)
        recorder.save_response(hash_key, response_data)
    """

    def __init__(self, recordings_dir: Path):
        """Initialize recorder.

        Args:
            recordings_dir: Directory to store recordings
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
        """Generate deterministic hash from request parameters.

        Args:
            model: Model name (e.g., "gpt-5-nano")
            messages: Conversation messages
            tools: Function tool definitions
            temperature: Temperature setting
            seed: Random seed for determinism
            **kwargs: Other parameters to include in hash

        Returns:
            16-character hash string (truncated SHA256)
        """
        # Build canonical request representation
        request_dict = {
            "model": model,
            "messages": self._normalize_messages(messages),
            "temperature": temperature,
        }

        if tools:
            request_dict["tools"] = tools

        if seed is not None:
            request_dict["seed"] = seed

        # Add any other relevant kwargs
        for key in ["max_tokens", "top_p", "frequency_penalty", "presence_penalty"]:
            if key in kwargs:
                request_dict[key] = kwargs[key]

        # Serialize to stable JSON (sorted keys, no whitespace)
        json_str = json.dumps(
            request_dict,
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=True
        )

        # Hash and truncate
        hash_full = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
        return hash_full[:16]  # 16 chars is enough, collision probability negligible

    def _normalize_messages(self, messages: list) -> list:
        """Normalize message format for consistent hashing.

        Handles both dict format and OpenAI message objects.
        """
        normalized = []
        for msg in messages:
            if hasattr(msg, 'model_dump'):
                # OpenAI message object
                msg_dict = msg.model_dump(exclude_none=True)
            elif isinstance(msg, dict):
                msg_dict = msg
            else:
                # Try to convert to dict
                msg_dict = dict(msg)

            normalized.append(msg_dict)

        return normalized

    def save_request(self, hash_key: str, request_data: Dict[str, Any]) -> Path:
        """Save request to file.

        Args:
            hash_key: Hash identifying this request
            request_data: Full request data to save

        Returns:
            Path to saved file
        """
        request_path = self.recordings_dir / f"{hash_key}.request.json"

        # Add metadata
        recording = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hash": hash_key,
            "request": request_data,
        }

        # Atomic write with file locking
        self._atomic_write(request_path, recording)

        return request_path

    def save_response(self, hash_key: str, response_data: Dict[str, Any]) -> Path:
        """Save response to file.

        Args:
            hash_key: Hash identifying this request/response pair
            response_data: Full response data to save

        Returns:
            Path to saved file
        """
        response_path = self.recordings_dir / f"{hash_key}.response.json"

        # Add metadata
        recording = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hash": hash_key,
            "response": response_data,
        }

        # Atomic write with file locking
        self._atomic_write(response_path, recording)

        return response_path

    def recording_exists(self, hash_key: str) -> bool:
        """Check if recording exists for this hash.

        Args:
            hash_key: Hash to check

        Returns:
            True if both request and response files exist
        """
        request_path = self.recordings_dir / f"{hash_key}.request.json"
        response_path = self.recordings_dir / f"{hash_key}.response.json"
        return request_path.exists() and response_path.exists()

    def load_request(self, hash_key: str) -> Dict[str, Any]:
        """Load recorded request.

        Args:
            hash_key: Hash identifying the request

        Returns:
            Request data dictionary

        Raises:
            FileNotFoundError: If recording doesn't exist
        """
        request_path = self.recordings_dir / f"{hash_key}.request.json"
        if not request_path.exists():
            raise FileNotFoundError(
                f"No recorded request found for hash: {hash_key}\n"
                f"Expected file: {request_path}"
            )

        with open(request_path, 'r') as f:
            recording = json.load(f)

        return recording.get("request", recording)

    def load_response(self, hash_key: str) -> Dict[str, Any]:
        """Load recorded response.

        Args:
            hash_key: Hash identifying the response

        Returns:
            Response data dictionary

        Raises:
            FileNotFoundError: If recording doesn't exist
        """
        response_path = self.recordings_dir / f"{hash_key}.response.json"
        if not response_path.exists():
            raise FileNotFoundError(
                f"No recorded response found for hash: {hash_key}\n"
                f"Expected file: {response_path}\n"
                f"Run tests with TEST_MODE=generate to create recordings."
            )

        with open(response_path, 'r') as f:
            recording = json.load(f)

        return recording.get("response", recording)

    def _atomic_write(self, path: Path, data: Dict[str, Any]):
        """Write JSON file atomically with file locking.

        Args:
            path: File path to write
            data: Data to serialize as JSON
        """
        # Write to temporary file first
        temp_path = path.with_suffix('.tmp')

        try:
            with open(temp_path, 'w') as f:
                # Acquire exclusive lock
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                try:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    f.flush()
                    os.fsync(f.fileno())
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Atomic rename
            temp_path.replace(path)
        except Exception:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get recording statistics.

        Returns:
            Dictionary with recording counts and disk usage
        """
        request_files = list(self.recordings_dir.glob("*.request.json"))
        response_files = list(self.recordings_dir.glob("*.response.json"))

        total_size = sum(f.stat().st_size for f in request_files + response_files)

        return {
            "recording_count": len(request_files),
            "paired_recordings": len([f for f in request_files
                                     if f.with_suffix('.response.json').exists()]),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "recordings_dir": str(self.recordings_dir),
        }
