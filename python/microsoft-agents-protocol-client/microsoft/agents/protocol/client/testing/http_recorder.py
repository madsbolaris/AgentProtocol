# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
HTTP recording and playback for Agent Protocol Client SDK tests.
Follows the same pattern as TestingChatClient from emoji-chat samples.
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class HttpRecorder:
    """Records HTTP interactions for Agent Protocol Client SDK tests."""

    def __init__(self, scenario_name: str, recordings_base_dir: Optional[str] = None):
        """Initialize HttpRecorder.

        Args:
            scenario_name: Name of the test scenario (used as subdirectory)
            recordings_base_dir: Base directory for recordings (defaults to test-data/llm-recordings/docs)
        """
        if recordings_base_dir is None:
            # Default to shared cross-language recordings directory
            repo_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
            recordings_base_dir = repo_root / "test-data" / "llm-recordings" / "docs"

        self.recordings_dir = Path(recordings_base_dir) / scenario_name
        self.scenario_name = scenario_name
        self.call_count = 0

        # Check if we're in recording mode
        self.record_mode = os.getenv("RECORD_HTTP", "").lower() in ("true", "1")

        if self.record_mode:
            self.recordings_dir.mkdir(parents=True, exist_ok=True)
            print(f"📹 HTTP Recording enabled: {self.recordings_dir}")
        else:
            print(f"▶️  HTTP Playback enabled: {self.recordings_dir}")
            if not self.recordings_dir.exists():
                print(f"⚠️  Warning: Recordings directory does not exist: {self.recordings_dir}")

    def hash_request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> str:
        """Compute SHA256 hash of HTTP request.

        Uses exact same algorithm as C# RecordingHttpMessageHandler for cross-language compatibility.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            body: Request body (optional)

        Returns:
            First 16 characters of SHA256 hash (lowercase hex)
        """
        # Normalize request data
        normalized = {
            "method": method.upper(),
            "path": path,
            "body": body if body is not None else None
        }

        # Serialize to JSON with sorted keys
        # IMPORTANT: ensure_ascii=False keeps Unicode characters unescaped
        # This matches C# JSON serialization for consistent cross-language hashing
        json_str = json.dumps(normalized, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

        # Hash and truncate (SHA256, first 16 chars)
        hash_obj = hashlib.sha256(json_str.encode('utf-8'))
        hash_str = hash_obj.hexdigest()[:16].lower()

        return hash_str

    async def record_interaction(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]],
        response: Dict[str, Any]
    ):
        """Record an HTTP interaction to disk.

        Args:
            method: HTTP method
            path: Request path
            body: Request body
            response: HTTP response to record
        """
        self.call_count += 1
        call_id = self.call_count
        hash_key = self.hash_request(method, path, body)

        print(f"  📹 Recording HTTP call #{call_id}: {hash_key}")

        # Save request (for debugging)
        request_file = self.recordings_dir / f"{hash_key}.request.json"
        request_data = {
            "callId": call_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "hash": hash_key,
            "method": method.upper(),
            "path": path,
            "body": body
        }

        with open(request_file, 'w', encoding='utf-8') as f:
            json.dump(request_data, f, indent=2, ensure_ascii=False)

        # Save response (used by tests)
        response_file = self.recordings_dir / f"{hash_key}.response.json"
        response_data = {
            "callId": call_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "hash": hash_key,
            "response": response
        }

        with open(response_file, 'w', encoding='utf-8') as f:
            json.dump(response_data, f, indent=2, ensure_ascii=False)


class HttpPlayer:
    """Plays back recorded HTTP interactions for Agent Protocol Client SDK tests."""

    def __init__(self, scenario_name: str, recordings_base_dir: Optional[str] = None):
        """Initialize HttpPlayer.

        Args:
            scenario_name: Name of the test scenario
            recordings_base_dir: Base directory for recordings (defaults to test-data/llm-recordings/docs)
        """
        if recordings_base_dir is None:
            # Default to shared cross-language recordings directory
            repo_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
            recordings_base_dir = repo_root / "test-data" / "llm-recordings" / "docs"

        self.recordings_dir = Path(recordings_base_dir) / scenario_name
        self.scenario_name = scenario_name
        self.call_count = 0

        if not self.recordings_dir.exists():
            raise FileNotFoundError(
                f"Recordings directory not found: {self.recordings_dir}\n\n"
                f"This usually means:\n"
                f"1. Tests need to be run in recording mode first: RECORD_HTTP=true\n"
                f"2. The scenario name doesn't match any recorded scenario\n\n"
                f"To generate recordings, run:\n"
                f"  RECORD_HTTP=true pytest tests/test_quickstart.py\n"
            )

    async def playback_response(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Playback a recorded HTTP response.

        Args:
            method: HTTP method
            path: Request path
            body: Request body

        Returns:
            Recorded HTTP response

        Raises:
            FileNotFoundError: If no recording exists for this request
        """
        self.call_count += 1
        call_id = self.call_count

        # Compute hash using same algorithm as recorder
        hash_key = self._hash_request(method, path, body)

        response_file = self.recordings_dir / f"{hash_key}.response.json"

        if not response_file.exists():
            raise FileNotFoundError(
                f"No recorded HTTP response found for request hash: {hash_key}\n"
                f"Expected file: {response_file}\n\n"
                f"This usually means:\n"
                f"1. Tests need to be run in recording mode first: RECORD_HTTP=true\n"
                f"2. The request parameters have changed (different hash)\n"
                f"3. The recording file was deleted\n\n"
                f"Request details:\n"
                f"  Method: {method}\n"
                f"  Path: {path}\n"
                f"  Body: {body is not None}\n\n"
                f"To generate this recording, run:\n"
                f"  RECORD_HTTP=true pytest tests/test_quickstart.py -k {self.scenario_name}\n"
            )

        print(f"  ▶️  Replaying HTTP call #{call_id}: {hash_key}")

        with open(response_file, 'r', encoding='utf-8') as f:
            recording = json.load(f)

        return recording["response"]

    def _hash_request(self, method: str, path: str, body: Optional[Dict[str, Any]] = None) -> str:
        """Compute SHA256 hash of HTTP request (same as HttpRecorder)."""
        normalized = {
            "method": method.upper(),
            "path": path,
            "body": body if body is not None else None
        }

        json_str = json.dumps(normalized, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
        hash_obj = hashlib.sha256(json_str.encode('utf-8'))
        return hash_obj.hexdigest()[:16].lower()
