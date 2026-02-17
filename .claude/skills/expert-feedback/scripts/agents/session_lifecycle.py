#!/usr/bin/env python3
"""
Session Lifecycle Management for Claude Agent SDK.

This module provides proper cleanup of sub-agent sessions when the parent
process is interrupted or terminated. It ensures that:

1. All spawned sub-agents are tracked in a global registry
2. Signal handlers (SIGINT, SIGTERM) trigger cancellation of all sessions
3. Asyncio tasks are properly cancelled on shutdown
4. No orphaned API sessions continue running after parent exits

Usage:
    from session_lifecycle import SessionManager

    async def main():
        manager = SessionManager()

        # Spawn agents - they'll be automatically tracked and cleaned up
        tasks = [
            manager.spawn_with_cleanup(expert1_coroutine()),
            manager.spawn_with_cleanup(expert2_coroutine()),
        ]

        try:
            results = await asyncio.gather(*tasks)
        finally:
            await manager.cleanup()

    # Run with signal handlers
    SessionManager.run_with_lifecycle(main())
"""
import asyncio
import signal
import sys
import atexit
from typing import Set, Optional, Coroutine, Any
from contextlib import asynccontextmanager


class SessionManager:
    """
    Manages lifecycle of Claude Agent SDK sessions with proper cleanup.

    This class tracks all running sub-agent tasks and ensures they are
    cancelled when the parent process terminates, preventing orphaned
    API sessions from continuing to consume tokens.
    """

    _instance: Optional['SessionManager'] = None
    _shutdown_in_progress: bool = False

    def __init__(self):
        self.active_tasks: Set[asyncio.Task] = set()
        self.session_ids: Set[str] = set()
        self._cleanup_done = False

        # Register as singleton
        SessionManager._instance = self

    @classmethod
    def get_instance(cls) -> 'SessionManager':
        """Get or create the singleton SessionManager instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def track_session(self, session_id: str) -> None:
        """Track a Claude API session ID for cleanup."""
        if session_id:
            self.session_ids.add(session_id)
            print(f"🔍 Tracking session: {session_id[:8]}...", file=sys.stderr)

    def untrack_session(self, session_id: str) -> None:
        """Remove session from tracking (e.g., when it completes normally)."""
        if session_id in self.session_ids:
            self.session_ids.discard(session_id)
            print(f"✅ Session completed: {session_id[:8]}...", file=sys.stderr)

    async def spawn_with_cleanup(self, coro: Coroutine[Any, Any, Any]) -> Any:
        """
        Spawn a coroutine as a task and track it for cleanup.

        The task will be automatically cancelled if the parent process
        is interrupted or terminated.

        Args:
            coro: The coroutine to execute

        Returns:
            The result of the coroutine
        """
        task = asyncio.create_task(coro)
        self.active_tasks.add(task)

        try:
            result = await task
            return result
        except asyncio.CancelledError:
            print(f"⚠️  Task cancelled: {task.get_name()}", file=sys.stderr)
            raise
        finally:
            self.active_tasks.discard(task)

    async def cleanup(self) -> None:
        """
        Cancel all tracked tasks and sessions.

        This should be called when the parent process is exiting,
        either normally or due to interruption.
        """
        if self._cleanup_done or SessionManager._shutdown_in_progress:
            return

        SessionManager._shutdown_in_progress = True
        self._cleanup_done = True

        print(f"\n🧹 Cleaning up {len(self.active_tasks)} active tasks...", file=sys.stderr)

        # Cancel all active asyncio tasks
        for task in self.active_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to finish cancelling (with timeout)
        if self.active_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.active_tasks, return_exceptions=True),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                print("⚠️  Some tasks did not cancel within timeout", file=sys.stderr)

        # Note: Claude Agent SDK sessions are automatically cancelled when
        # the async generator is closed or the task is cancelled.
        # The SDK handles cleanup of the underlying API connections.

        if self.session_ids:
            print(f"🛑 Stopped {len(self.session_ids)} sub-agent session(s)", file=sys.stderr)
            self.session_ids.clear()

        self.active_tasks.clear()
        print("✅ Cleanup complete", file=sys.stderr)

    @staticmethod
    def setup_signal_handlers(loop: asyncio.AbstractEventLoop) -> None:
        """
        Install signal handlers for graceful shutdown.

        Handles SIGINT (Ctrl+C) and SIGTERM to ensure cleanup runs
        before the process exits.
        """
        def signal_handler(signum, frame):
            """Handle termination signals."""
            signame = signal.Signals(signum).name
            print(f"\n⚠️  Received {signame}, shutting down...", file=sys.stderr)

            # Schedule cleanup in the event loop
            manager = SessionManager.get_instance()
            if not SessionManager._shutdown_in_progress:
                asyncio.ensure_future(manager.cleanup(), loop=loop)
                # Give cleanup a moment to run, then exit
                loop.call_later(6.0, lambda: sys.exit(0))

        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        print("🛡️  Signal handlers installed (SIGINT, SIGTERM)", file=sys.stderr)

    @staticmethod
    def run_with_lifecycle(main_coro: Coroutine[Any, Any, Any]) -> Any:
        """
        Run an async main function with proper lifecycle management.

        This is the recommended way to run scripts that spawn sub-agents.
        It ensures cleanup happens on normal exit, exceptions, and signals.

        Args:
            main_coro: The main async function to execute

        Returns:
            The result of main_coro

        Example:
            async def main():
                manager = SessionManager()
                # ... spawn agents ...
                await manager.cleanup()

            SessionManager.run_with_lifecycle(main())
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        manager = SessionManager.get_instance()
        SessionManager.setup_signal_handlers(loop)

        # Also register atexit cleanup as last resort
        atexit.register(lambda: None)  # Placeholder for sync cleanup

        try:
            return loop.run_until_complete(main_coro)
        except KeyboardInterrupt:
            print("\n⚠️  Keyboard interrupt, cleaning up...", file=sys.stderr)
            loop.run_until_complete(manager.cleanup())
        except Exception as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            loop.run_until_complete(manager.cleanup())
            raise
        finally:
            # Ensure cleanup runs even if not explicitly called
            if not manager._cleanup_done:
                try:
                    loop.run_until_complete(manager.cleanup())
                except Exception:
                    pass

            # Close the loop
            try:
                loop.close()
            except Exception:
                pass


@asynccontextmanager
async def managed_session():
    """
    Context manager for automatic session cleanup.

    Usage:
        async with managed_session() as manager:
            await manager.spawn_with_cleanup(agent1())
            await manager.spawn_with_cleanup(agent2())
        # Cleanup happens automatically here
    """
    manager = SessionManager()
    try:
        yield manager
    finally:
        await manager.cleanup()


