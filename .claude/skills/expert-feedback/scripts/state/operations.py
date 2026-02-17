"""
Atomic state operations for expert-feedback skill.

This module provides low-level atomic operations for state file updates
with file locking and retry logic to handle concurrent access.
"""
import fcntl
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Callable


def update_state_atomic(
    state_path: Path,
    update_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    max_retries: int = 10,  # Increased from 5 to handle more parallel experts
    retry_delay: float = 0.5  # Increased from 0.1 for better backoff
) -> Dict[str, Any]:
    """
    Atomically update state.json with file locking and retry logic.

    Total retry window with exponential backoff:
    - Previous: 0.1 + 0.2 + 0.4 + 0.8 + 1.6 = 3.1 seconds (5 retries)
    - Current: 0.5 + 1.0 + 2.0 + 4.0 + 8.0 = 15.5 seconds (10 retries max)

    This handles high parallelism (7+ experts) more gracefully.

    Args:
        state_path: Path to state.json file
        update_fn: Function that takes current state and returns updates to merge
        max_retries: Maximum number of lock acquisition attempts (default: 10)
        retry_delay: Initial retry delay in seconds (default: 0.5s)

    Returns:
        Updated state dict

    Raises:
        IOError: If unable to acquire lock after max_retries

    Example:
        def add_session(state):
            if "expert_sessions" not in state:
                state["expert_sessions"] = {}
            state["expert_sessions"]["typescript"] = "sess_123"
            return state

        updated = update_state_atomic(state_path, add_session)
    """
    logger = logging.getLogger(__name__)
    start_time = time.time()

    for attempt in range(max_retries):
        try:
            with open(state_path, 'r+') as f:
                # Try to acquire exclusive lock (non-blocking after first attempt)
                lock_mode = fcntl.LOCK_EX | (fcntl.LOCK_NB if attempt > 0 else 0)
                try:
                    fcntl.flock(f.fileno(), lock_mode)
                except BlockingIOError:
                    if attempt == max_retries - 1:
                        raise IOError(f"Could not acquire lock on {state_path} after {max_retries} attempts")
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue

                try:
                    # Read current state
                    state = json.load(f)

                    # Apply updates
                    state = update_fn(state)

                    # Write back atomically
                    f.seek(0)
                    f.truncate()
                    json.dump(state, f, indent=2)

                    # Log slow lock acquisitions for monitoring
                    lock_duration = time.time() - start_time
                    if lock_duration > 1.0:
                        logger.warning(
                            f"Lock acquisition took {lock_duration:.2f}s "
                            f"(attempts: {attempt + 1}/{max_retries})"
                        )

                    return state
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        except BlockingIOError:
            # Lock acquisition failed, retry
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (2 ** attempt))
            else:
                raise IOError(f"Could not acquire lock on {state_path} after {max_retries} attempts")

    raise IOError(f"Failed to update {state_path} after {max_retries} attempts")
