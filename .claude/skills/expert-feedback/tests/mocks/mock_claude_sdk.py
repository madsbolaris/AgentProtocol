"""
Mock implementation of Claude Agent SDK for testing.

This module provides a mock version of the claude_agent_sdk that can record
and replay LLM interactions, enabling fast and deterministic tests.
"""

import asyncio
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from .sdk_recorder import SDKRecorder


class MockClaudeAgentSDK:
    """
    Mock implementation of Claude Agent SDK for testing.

    Supports two modes:
    - replay: Uses recorded responses (fast, no API calls)
    - record: Makes real API calls and saves responses

    Example:
        mock_sdk = MockClaudeAgentSDK(Path("tests/recordings"), mode="replay")

        # Replace real SDK
        import sys
        sys.modules['claude_agent_sdk'] = mock_sdk

        # Use in tests - calls are automatically mocked
        from claude_agent_sdk import query
        async for event in query(prompt="Test", options=options):
            print(event)
    """

    def __init__(
        self,
        recordings_dir: Path,
        mode: str = "replay",
        real_sdk_module: Optional[Any] = None
    ):
        """
        Initialize mock SDK.

        Args:
            recordings_dir: Directory for storing/loading recordings
            mode: "replay" (use recordings) or "record" (make real calls + save)
            real_sdk_module: Real claude_agent_sdk module (required for record mode)

        Raises:
            ValueError: If mode is invalid or real_sdk missing in record mode
        """
        if mode not in ("replay", "record"):
            raise ValueError(f"Invalid mode: {mode}. Must be 'replay' or 'record'")

        # In record mode, we need the real SDK
        if mode == "record" and real_sdk_module is None:
            raise ValueError(
                "real_sdk_module is required when mode='record'. "
                "Import the real claude_agent_sdk before creating the mock."
            )

        self.mode = mode
        self.recorder = SDKRecorder(recordings_dir)
        self.call_count = 0
        self._real_sdk = real_sdk_module  # Store real SDK reference

        # Track simulated errors for testing
        self._timeout_experts: List[str] = []
        self._failure_experts: List[str] = []

        print(f"  🎭 MockClaudeAgentSDK initialized in {mode} mode")
        print(f"     Recordings: {recordings_dir}")
        if mode == "record" and real_sdk_module:
            print(f"     Real SDK: {getattr(real_sdk_module, '__name__', real_sdk_module)}")

    @property
    def ClaudeAgentOptions(self):
        """Return ClaudeAgentOptions class (mock or real depending on mode)."""
        # Import from conftest to get the mock version
        # This will be used by tests that need to create options
        from tests.conftest import _MockClaudeAgentOptions
        return _MockClaudeAgentOptions

    @property
    def types(self):
        """Return mock types module."""
        from tests.conftest import _MockTypesModule
        return _MockTypesModule()

    async def query(
        self,
        prompt: Optional[str] = None,
        system: Optional[List[Any]] = None,
        messages: Optional[List[Any]] = None,
        options: Optional[Any] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Mock query function that records or replays LLM interactions.

        Args:
            prompt: User prompt text
            system: System messages/blocks
            messages: Conversation messages
            options: ClaudeAgentOptions

        Yields:
            Stream events (dict format)
        """
        import sys
        self.call_count += 1

        # Debug output
        print(f"  🔍 MockSDK.query() called (mode={self.mode}):", file=sys.stderr)
        print(f"     prompt type: {type(prompt).__name__}", file=sys.stderr)
        print(f"     options type: {type(options).__name__ if options else 'None'}", file=sys.stderr)

        # Generate request hash
        print(f"  🔑 Generating request hash...", file=sys.stderr)
        request_hash = self.recorder.hash_request(prompt, system, messages, options)
        print(f"  🔑 Hash: {request_hash[:16]}...", file=sys.stderr)

        if self.mode == "record":
            # Record mode: make real call and save
            print(f"  🎬 Entering record mode, calling _record_interaction...", file=sys.stderr)
            async for event in self._record_interaction(
                request_hash, prompt, system, messages, options
            ):
                print(f"  📤 Yielding event from _record_interaction: {type(event)}", file=sys.stderr)
                yield event
            print(f"  ✅ _record_interaction completed", file=sys.stderr)
        else:
            # Replay mode: use recorded response
            print(f"  ▶️  Entering replay mode, calling _replay_interaction...", file=sys.stderr)
            async for event in self._replay_interaction(
                request_hash, prompt, system, messages, options
            ):
                yield event

    async def _record_interaction(
        self,
        request_hash: str,
        prompt: Optional[str],
        system: Optional[List[Any]],
        messages: Optional[List[Any]],
        options: Optional[Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Make real API call and record the response.

        Args:
            request_hash: Hash of the request
            prompt: User prompt
            system: System messages
            messages: Conversation messages
            options: Request options

        Yields:
            Stream events
        """
        import sys
        import os
        print(f"  🎬 _record_interaction() called, hash={request_hash[:8]}", file=sys.stderr)

        # Check authentication
        api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        if api_key:
            print(f"  ✅ ANTHROPIC_API_KEY is set: {api_key[:15]}...", file=sys.stderr)
        else:
            print(f"  ❌ ANTHROPIC_API_KEY is NOT set!", file=sys.stderr)

        # Use stored real SDK (no import needed - prevents infinite recursion!)
        if self._real_sdk is None:
            raise RuntimeError(
                "Real claude_agent_sdk module not available for recording. "
                "This should not happen - mock was initialized incorrectly."
            )

        print(f"  ✅ Real SDK available: {type(self._real_sdk)}", file=sys.stderr)

        real_query = self._real_sdk.query  # Use stored reference
        print(f"  ✅ Got real_query: {type(real_query)}", file=sys.stderr)

        print(f"  🔴 Recording LLM call #{self.call_count}: {request_hash}", file=sys.stderr)

        # Collect events
        events = []

        # Make real call to claude_agent_sdk.query()
        # Real SDK signature: query(*, prompt, options)
        # prompt can be a string or list of system blocks
        real_prompt = prompt if prompt is not None else (system if system is not None else messages)

        # CRITICAL FIX: Convert list prompts to strings to avoid SubprocessCLI transport
        # List prompts trigger SubprocessCLI which hangs in test context
        if isinstance(real_prompt, list):
            print(f"  🔄 Converting list prompt ({len(real_prompt)} blocks) to string", file=sys.stderr)
            # Concatenate all text blocks into a single string
            text_parts = []
            for block in real_prompt:
                if isinstance(block, dict) and block.get('type') == 'text':
                    text_parts.append(block['text'])
            real_prompt = "\n\n".join(text_parts)
            print(f"  ✅ Converted to string prompt ({len(real_prompt)} chars)", file=sys.stderr)

        print(f"  📝 Prepared real_prompt (type: {type(real_prompt)})", file=sys.stderr)

        # Create REAL ClaudeAgentOptions for real SDK call (not our mock!)
        # Extract parameters from mock options
        real_options = None
        if options:
            # Get the REAL ClaudeAgentOptions class from the stored real SDK module
            RealClaudeAgentOptions = self._real_sdk.ClaudeAgentOptions
            kwargs = {}
            if hasattr(options, 'allowed_tools'):
                kwargs['allowed_tools'] = options.allowed_tools
            if hasattr(options, 'resume') and options.resume:
                kwargs['resume'] = options.resume

            # CRITICAL: Pass env dict with API key and Claude vars removed
            import os
            api_key = os.environ.get('ANTHROPIC_API_KEY')

            print(f"  🔍 Environment check before env prep:", file=sys.stderr)
            print(f"     ANTHROPIC_API_KEY: {'SET (' + api_key[:15] + '...' + api_key[-4:] + ')' if api_key else 'NOT SET'}", file=sys.stderr)
            print(f"     CLAUDECODE: {os.environ.get('CLAUDECODE', 'unset')}", file=sys.stderr)
            print(f"     CLAUDE_CODE_ENTRYPOINT: {os.environ.get('CLAUDE_CODE_ENTRYPOINT', 'unset')}", file=sys.stderr)

            if api_key:
                # Prepare clean environment for subprocess
                env_dict = {}
                # Copy essential vars but exclude Claude Code vars
                claude_vars = {'CLAUDECODE', 'CLAUDE_CODE_ENTRYPOINT', 'CLAUDE_CODE_ENABLE_SDK_FILE_CHECKPOINTING'}
                for key, value in os.environ.items():
                    if key not in claude_vars:
                        env_dict[key] = value
                # Ensure API key is set
                env_dict['ANTHROPIC_API_KEY'] = api_key
                kwargs['env'] = env_dict
                print(f"  🔑 Prepared env dict with {len(env_dict)} vars, API key set", file=sys.stderr)

            # Add debug_stderr to capture subprocess errors
            kwargs['debug_stderr'] = sys.stderr

            # Add other parameters as needed
            print(f"  🔧 Creating real ClaudeAgentOptions with kwargs: {list(kwargs.keys())}", file=sys.stderr)
            real_options = RealClaudeAgentOptions(**kwargs)
            print(f"  🔧 Created real options: {type(real_options)}", file=sys.stderr)
            # Debug: print what's in the real options
            if hasattr(real_options, '__dict__'):
                print(f"  🔍 Real options attributes: {list(vars(real_options).keys())[:10]}", file=sys.stderr)

        try:
            print(f"  🎬 About to call real claude_agent_sdk.query()", file=sys.stderr)
            print(f"  🎬 Calling real_query(prompt={type(real_prompt)}, options={type(real_options)})", file=sys.stderr)
            # DOUBLE CHECK: Verify API key is STILL set right before SDK call
            import os
            final_check = os.environ.get('ANTHROPIC_API_KEY')
            if final_check:
                print(f"  ✅ FINAL CHECK: API key still set: {final_check[:15]}...{final_check[-4:]}", file=sys.stderr)
            else:
                print(f"  ❌ FINAL CHECK: API key is NOT SET!", file=sys.stderr)
                raise RuntimeError("ANTHROPIC_API_KEY not set at SDK call time")

            # Call real SDK query function
            async for event in real_query(prompt=real_prompt, options=real_options):
                # Convert event to serializable dict
                print(f"  📥 Got event from real SDK: {type(event).__name__}", file=sys.stderr)
                event_dict = self._serialize_event(event)
                events.append(event_dict)
                yield event

            print(f"  ✅ Real SDK query completed", file=sys.stderr)
        except Exception as e:
            import traceback
            print(f"\n{'='*80}", file=sys.stderr)
            print(f"ERROR in real SDK call:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            print(f"options type: {type(options)}", file=sys.stderr)
            print(f"options attributes: {vars(options) if hasattr(options, '__dict__') else 'no __dict__'}", file=sys.stderr)
            print(f"{'='*80}\n", file=sys.stderr)
            raise
        finally:
            # ALWAYS save recording, even if consumer breaks early
            if events:
                print(f"  💾 Saving recording with {len(events)} events...", file=sys.stderr)
                request_data = {
                    "prompt": prompt,
                    "system": self._serialize_messages(system) if system else None,
                    "messages": self._serialize_messages(messages) if messages else None,
                    "options": self._serialize_options(options) if options else None,
                }

                self.recorder.save_interaction(request_hash, request_data, events)
                print(f"  ✅ Recording saved to {request_hash}.response.json", file=sys.stderr)

    async def _replay_interaction(
        self,
        request_hash: str,
        prompt: Optional[str],
        system: Optional[List[Any]],
        messages: Optional[List[Any]],
        options: Optional[Any]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Replay recorded response.

        Args:
            request_hash: Hash of the request
            prompt: User prompt (for error messages)
            system: System messages (for error messages)
            messages: Conversation messages (for error messages)
            options: Request options (for error messages)

        Yields:
            Recorded stream events
        """
        print(f"  ▶️  Replaying LLM call #{self.call_count}: {request_hash}")

        # Load recorded events
        try:
            events = self.recorder.load_response(request_hash)
        except FileNotFoundError:
            # Provide helpful error with request details
            raise FileNotFoundError(
                f"No recording found for request hash: {request_hash}\n"
                f"\n"
                f"Request details:\n"
                f"  Prompt: {prompt[:100] if prompt else None}...\n"
                f"  System blocks: {len(system) if system else 0}\n"
                f"  Messages: {len(messages) if messages else 0}\n"
                f"  Options: {options}\n"
                f"\n"
                f"To generate this recording, run:\n"
                f"  EXPERT_FEEDBACK_TEST_MODE=record pytest <your_test> -v\n"
            )

        # Replay events with small delay to simulate streaming
        for event in events:
            # Convert back to objects if needed
            yield event
            await asyncio.sleep(0.001)  # Small delay for realism

    def _serialize_event(self, event: Any) -> Dict[str, Any]:
        """
        Convert stream event to serializable dict.

        Args:
            event: StreamEvent object

        Returns:
            Serialized event dict
        """
        if hasattr(event, 'model_dump'):
            return event.model_dump()
        elif hasattr(event, 'to_dict'):
            return event.to_dict()
        elif isinstance(event, dict):
            return event
        else:
            return {"raw": str(event)}

    def _serialize_messages(
        self, messages: Optional[List[Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Convert messages to serializable format.

        Args:
            messages: List of message objects

        Returns:
            Serialized messages
        """
        if not messages:
            return None

        serialized = []
        for msg in messages:
            if hasattr(msg, 'model_dump'):
                serialized.append(msg.model_dump())
            elif hasattr(msg, 'to_dict'):
                serialized.append(msg.to_dict())
            elif isinstance(msg, dict):
                serialized.append(msg)
            else:
                serialized.append({"content": str(msg)})

        return serialized

    def _serialize_options(self, options: Optional[Any]) -> Optional[Dict[str, Any]]:
        """
        Convert options to serializable format.

        Args:
            options: ClaudeAgentOptions object

        Returns:
            Serialized options
        """
        if not options:
            return None

        if hasattr(options, 'model_dump'):
            return options.model_dump()
        elif hasattr(options, 'to_dict'):
            return options.to_dict()
        elif isinstance(options, dict):
            return options
        else:
            return {}

    # Test utility methods

    def set_timeout_for(self, expert: str) -> None:
        """
        Configure mock to simulate timeout for an expert.

        Args:
            expert: Expert name to timeout
        """
        self._timeout_experts.append(expert)

    def set_failure_for(self, experts: Union[str, List[str]]) -> None:
        """
        Configure mock to simulate failure for expert(s).

        Args:
            experts: Expert name or list of names to fail
        """
        if isinstance(experts, str):
            experts = [experts]
        self._failure_experts.extend(experts)

    def reset_test_state(self) -> None:
        """Reset test simulation state."""
        self._timeout_experts = []
        self._failure_experts = []
        self.call_count = 0


# Module-level mock for monkeypatch usage

# These will be set when the module is used as a mock
query = None
types = None


def init_module_mock(mock_sdk: MockClaudeAgentSDK):
    """
    Initialize module-level mocks for easy monkeypatching.

    Args:
        mock_sdk: Configured MockClaudeAgentSDK instance
    """
    global query, types

    # Set query function
    query = mock_sdk.query

    # Mock types module (for imports like: from claude_agent_sdk.types import ...)
    types = _MockTypesModule()


class _MockTypesModule:
    """Mock types module for claude_agent_sdk.types imports."""

    def __getattr__(self, name: str):
        """
        Return mock for any type requested.

        This allows code like:
            from claude_agent_sdk.types import AssistantMessage

        To work without errors.
        """
        # Return a simple mock class
        return type(name, (), {})


class ClaudeAgentOptions:
    """
    Mock ClaudeAgentOptions for testing.

    This is a simplified version that supports the most common options.
    """

    def __init__(
        self,
        resume: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        model: str = "claude-sonnet-4",
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
    ):
        self.resume = resume
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = model
        self.top_p = top_p
        self.top_k = top_k
        self.stop_sequences = stop_sequences

    def model_dump(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        result = {
            "resume": self.resume,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "model": self.model,
        }

        if self.top_p is not None:
            result["top_p"] = self.top_p
        if self.top_k is not None:
            result["top_k"] = self.top_k
        if self.stop_sequences is not None:
            result["stop_sequences"] = self.stop_sequences

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Alias for model_dump."""
        return self.model_dump()
