"""
Agent spawning utilities for expert-feedback skill.

This module provides unified agent spawning logic with consistent configuration,
session management, token tracking, and file watching capabilities.
"""
import asyncio
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from claude_agent_sdk import query, ClaudeAgentOptions
print(f"  📦 spawn.py imported query: {query}", file=sys.stderr)
print(f"  📦 spawn.py imported ClaudeAgentOptions: {ClaudeAgentOptions}", file=sys.stderr)

from claude_agent_sdk.types import (
    AssistantMessage, SystemMessage, ResultMessage,
    TextBlock, ThinkingBlock, ToolUseBlock
)
from agent_logging.transcript import TranscriptLogger


@dataclass
class AgentSpawnConfig:
    """Configuration for unified agent spawning.

    This configuration object synthesizes all agent spawning parameters
    across different agent types (experts, synthesis, artifact-generation, etc.)
    to ensure consistent behavior and make feature addition easier.
    """

    # Required fields
    agent_type: str  # "expert", "synthesis", "artifact-generation", "artifact-review", "rejection"
    workspace: Path  # Workspace directory

    # Prompt configuration
    prompt: str  # String prompt

    # Agent identification
    agent_name: Optional[str] = None  # Name for logging (e.g., "typescript", "synthesis")
    correlation_id: Optional[str] = None  # Correlation ID for end-to-end workflow tracing

    # Session management
    session_id: Optional[str] = None  # Existing session to resume (if any)
    enable_session_reuse: bool = True  # Whether to enable session resumption

    # Timeout configuration
    timeout_seconds: int = 900  # Maximum execution time (15 minutes default)
    warning_first_seconds: int = 600  # When to issue first timeout warning (10 minutes)
    warning_interval_seconds: int = 60  # How often to repeat warnings

    # File watching (for early termination)
    expected_files: List[Path] = field(default_factory=list)  # Files that indicate completion
    enable_file_watching: bool = False  # Whether to monitor for file creation
    file_watch_delay_seconds: int = 1  # How often to check for files

    # Token tracking
    enable_token_tracking: bool = True  # Track input/output tokens
    separate_input_output_tokens: bool = True  # Track separately vs combined
    token_fallback_approximation: bool = True  # Use approximation if tracking fails

    # Logging
    enable_standard_logging: bool = True  # Standard logger output
    enable_transcript_logging: bool = True  # TranscriptLogger output
    log_tool_calls: bool = True  # Log tool usage
    log_full_prompts: bool = True  # Log complete prompts (not just previews)
    logger: Optional[Any] = None  # Optional pre-configured logger (uses default if None)

    # Tools
    allowed_tools: List[str] = field(default_factory=lambda: ["Read", "Grep", "Glob", "Write", "Bash"])

    # Progress tracking
    update_state_on_progress: bool = False  # Update workspace state.json during execution

    # Test control (for deterministic recording generation)
    test_control: Optional[Dict[str, Any]] = None  # Test control parameters for recording mode


@dataclass
class AgentResult:
    """Result from agent spawning.

    This standardized result object makes it easier to handle agent
    execution results consistently across all agent types.
    """

    # Status
    status: str  # "complete", "error", "timeout", "cancelled"
    agent_type: str  # Type of agent that was spawned
    agent_name: Optional[str] = None  # Name of the specific agent
    session_id: Optional[str] = None  # Session ID (for resumption)

    # Metrics
    duration_seconds: int = 0  # Total execution time
    tokens_used: int = 0  # Total tokens (input + output)
    input_tokens: int = 0  # Input tokens only
    output_tokens: int = 0  # Output tokens only
    token_tracking_approximated: bool = False  # Whether tokens were estimated
    accurate_cost: float = 0.0  # Accurate cost in USD

    # Output tracking
    files_created: List[Path] = field(default_factory=list)  # Files created by agent
    terminated_early: bool = False  # Whether agent was terminated before natural completion

    # Error handling
    error: Optional[str] = None  # Error message (if status == "error")
    error_type: Optional[str] = None  # Error type (e.g., "timeout", "file_not_found")

    # Additional data (flexible for agent-specific results)
    extra_data: Dict[str, Any] = field(default_factory=dict)


async def spawn_agent(
    config: AgentSpawnConfig,
    progress_callback: Optional[Callable[[str, str], None]] = None
) -> AgentResult:
    """Unified agent spawning function.

    This function synthesizes all agent spawning logic from the various
    scripts (spawn-all-experts, consolidate-feedback, generate_artifact, artifact-review,
    handle-rejection) into a single, consistent implementation.

    Args:
        config: AgentSpawnConfig with all spawning parameters
        progress_callback: Optional callback for progress updates (state, message)

    Returns:
        AgentResult with execution details

    Example:
        config = AgentSpawnConfig(
            agent_type="expert",
            agent_name="typescript",
            prompt=build_expert_prompt(...),
            workspace=workspace_path,
            expected_files=[review_file],
            enable_file_watching=True
        )
        result = await spawn_agent(config)

        if result.status == "complete":
            print(f"Success! Used {result.tokens_used} tokens in {result.duration_seconds}s")
        else:
            print(f"Failed: {result.error}")
    """
    start_time = time.time()
    session_id = config.session_id
    input_tokens = 0
    output_tokens = 0
    files_created = []
    terminated_early = False

    # Setup logging
    logger = config.logger  # Use provided logger
    if not logger and config.enable_standard_logging:
        # Fall back to module logger if no logger provided
        import logging
        logger = logging.getLogger(__name__)

    # Setup transcript logging
    transcript = None
    if config.enable_transcript_logging:
        agent_log_name = config.agent_name or config.agent_type
        transcript = TranscriptLogger(config.workspace, agent_log_name)

    try:
        # Determine if we're resuming or starting fresh
        if config.session_id and config.enable_session_reuse:
            if logger:
                logger.info(f"Resuming {config.agent_type} session: {config.session_id[:8]}...")
        else:
            if logger:
                logger.info(f"Starting new {config.agent_type} agent...")

        # Inject test controls if provided (only in recording mode)
        final_prompt = config.prompt
        if config.test_control:
            # Import test control module
            sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
            from test_control import inject_test_control
            final_prompt = inject_test_control(config.prompt, config.test_control)

            if logger and final_prompt != config.prompt:
                logger.info("Test controls injected (recording mode)")

        # Log full prompt if enabled
        if config.log_full_prompts and logger and config.enable_standard_logging:
            logger.info(f"Full prompt being sent to agent:\n{'='*80}\n{final_prompt}\n{'='*80}")

        # Setup file watching if enabled
        watcher_task = None
        agent_task = None

        async def watch_files():
            """Watch for expected files to be created."""
            if not config.expected_files:
                # No files to watch, wait indefinitely
                await asyncio.sleep(config.timeout_seconds)
                return False

            elapsed = 0
            while elapsed < config.timeout_seconds:
                # Check if all expected files exist
                all_exist = all(f.exists() for f in config.expected_files)

                if all_exist:
                    if logger:
                        logger.info(f"✅ All expected files created for {config.agent_name}, signaling completion")
                    return True

                await asyncio.sleep(config.file_watch_delay_seconds)
                elapsed += config.file_watch_delay_seconds

            # Timeout reached
            if logger:
                logger.warning(f"⚠️ File watcher timeout after {config.timeout_seconds}s")
            return False

        async def run_agent():
            """Run the agent conversation."""
            nonlocal session_id, input_tokens, output_tokens, final_prompt

            # Note: Removed error pattern detection as it caused false positives
            # when agents discussed error handling topics in their reviews.
            # Real errors are caught by SDK exceptions and proper error handling.

            # Build agent options
            print(f"  🔧 Building ClaudeAgentOptions for {config.agent_name}...", file=sys.stderr)
            if session_id and config.enable_session_reuse:
                # Resume existing session
                print(f"  🔧 Resuming session: {session_id[:8]}...", file=sys.stderr)
                agent_options = ClaudeAgentOptions(
                    allowed_tools=config.allowed_tools,
                    resume=session_id
                )
            else:
                # Start new session
                print(f"  🔧 Starting new session", file=sys.stderr)
                agent_options = ClaudeAgentOptions(
                    allowed_tools=config.allowed_tools
                )

            # Start agent conversation
            print(f"  🚀 Calling query() for {config.agent_name}...", file=sys.stderr)
            query_call = query(prompt=final_prompt, options=agent_options)

            # Process messages from agent
            print(f"  📨 Starting message iteration for {config.agent_name}...", file=sys.stderr)
            async for message in query_call:
                # Capture session ID from init or result messages
                # Use attribute checking instead of isinstance to work with both real and mock SDK events
                if hasattr(message, 'subtype') and message.subtype == "init":
                    # SystemMessage with init subtype
                    if hasattr(message, 'data') and isinstance(message.data, dict):
                        captured_session = message.data.get("session_id")
                        if captured_session:
                            session_id = captured_session
                            if logger:
                                logger.info(f"Agent session started: {session_id[:8]}...")
                elif hasattr(message, 'session_id') and message.session_id:
                    # ResultMessage with session_id
                    session_id = message.session_id

                # Log transcript activity
                if transcript and isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, ToolUseBlock):
                            transcript.log_tool(block.name, str(block.input))
                            if config.log_tool_calls and logger:
                                logger.debug(f"Tool: {block.name}")
                        elif isinstance(block, TextBlock):
                            transcript.log_message(block.text)
                        elif isinstance(block, ThinkingBlock):
                            transcript.log_think(block.thinking)

                # Track token usage
                if config.enable_token_tracking and isinstance(message, ResultMessage) and message.usage:
                    if config.separate_input_output_tokens:
                        input_tokens += message.usage.get("input_tokens", 0)
                        output_tokens += message.usage.get("output_tokens", 0)
                    else:
                        # Combined tracking
                        input_tokens += message.usage.get("total_tokens", 0)

                # Progress callback
                if progress_callback:
                    progress_callback("running", f"{config.agent_name} is working...")

            return {"completed_naturally": True}

        # Execute with or without file watching
        agent_result = None
        if config.enable_file_watching and config.expected_files:
            # Start both tasks
            agent_task = asyncio.create_task(run_agent())
            watcher_task = asyncio.create_task(watch_files())

            # Race: wait for either agent to complete OR files to be created
            done, pending = await asyncio.wait(
                [agent_task, watcher_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # Determine what completed first
            files_complete = watcher_task in done
            agent_complete = agent_task in done

            # Get agent result if it completed
            if agent_complete:
                agent_result = agent_task.result()

            # Cancel remaining tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            # Check if we terminated early due to file completion
            if files_complete and not agent_complete:
                terminated_early = True
                if logger:
                    logger.info(f"Agent terminated early after file completion")

                # Untrack session since we're terminating early
                if session_id:
                    try:
                        from agents.session_lifecycle import SessionManager
                        SessionManager.get_instance().untrack_session(session_id)
                    except ImportError:
                        pass
        else:
            # No file watching, just run the agent
            agent_result = await run_agent()

        # Calculate duration
        duration_seconds = int(time.time() - start_time)

        # Calculate total tokens
        total_tokens = input_tokens + output_tokens
        token_approximated = False

        # Fallback token approximation if tracking failed
        if config.token_fallback_approximation and total_tokens == 0 and config.enable_token_tracking:
            if logger:
                logger.warning(f"⚠️ Token usage is 0, using approximation")

            # Approximate input tokens from prompt length
            if config.prompt:
                input_tokens = len(config.prompt) // 4

            # Approximate output tokens from created files
            for file_path in config.expected_files:
                if file_path.exists():
                    try:
                        output_tokens += len(file_path.read_text()) // 4
                    except Exception:
                        pass  # Ignore errors reading files

            token_approximated = True
            total_tokens = input_tokens + output_tokens

        # Track files created
        if config.expected_files:
            files_created = [f for f in config.expected_files if f.exists()]

        # Log completion in transcript
        if transcript:
            transcript.log_complete(duration_seconds, total_tokens)

        # Progress callback
        if progress_callback:
            progress_callback("complete", f"{config.agent_name} finished")

        # Return successful result
        return AgentResult(
            status="complete",
            agent_type=config.agent_type,
            agent_name=config.agent_name,
            session_id=session_id,
            duration_seconds=duration_seconds,
            tokens_used=total_tokens,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            token_tracking_approximated=token_approximated,
            files_created=files_created,
            terminated_early=terminated_early
        )

    except asyncio.TimeoutError:
        duration_seconds = int(time.time() - start_time)
        error_msg = f"Agent exceeded timeout of {config.timeout_seconds} seconds"

        if transcript:
            transcript.log_error(error_msg)

        if logger:
            logger.error(error_msg)

        if progress_callback:
            progress_callback("timeout", error_msg)

        return AgentResult(
            status="timeout",
            agent_type=config.agent_type,
            agent_name=config.agent_name,
            session_id=session_id,
            duration_seconds=duration_seconds,
            tokens_used=input_tokens + output_tokens,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error=error_msg,
            error_type="timeout"
        )

    except Exception as e:
        duration_seconds = int(time.time() - start_time)
        error_msg = str(e)

        if transcript:
            transcript.log_error(error_msg)

        if logger:
            logger.error(f"Agent failed: {error_msg}", exc_info=True)

        if progress_callback:
            progress_callback("error", error_msg)

        return AgentResult(
            status="error",
            agent_type=config.agent_type,
            agent_name=config.agent_name,
            session_id=session_id,
            duration_seconds=duration_seconds,
            tokens_used=input_tokens + output_tokens,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error=error_msg,
            error_type=type(e).__name__
        )
