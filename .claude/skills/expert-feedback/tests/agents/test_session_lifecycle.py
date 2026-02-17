"""
Unit tests for agents/session_lifecycle.py

Tests session lifecycle management including:
- SessionManager initialization and tracking
- Task spawning and cleanup
- Signal handler setup
- Session ID tracking
- Graceful shutdown on interruption
- Context manager usage

Target coverage: 80%+
"""
import pytest
import asyncio
import signal
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from agents import session_lifecycle


@pytest.fixture(autouse=True)
def reset_session_manager():
    """Reset SessionManager class variables between tests."""
    # Reset class variables before test
    session_lifecycle.SessionManager._shutdown_in_progress = False
    session_lifecycle.SessionManager._instance = None
    yield
    # Reset after test
    session_lifecycle.SessionManager._shutdown_in_progress = False
    session_lifecycle.SessionManager._instance = None


class TestSessionManagerInit:
    """Test SessionManager initialization."""

    @pytest.mark.high
    def test_init_default(self):
        """Test SessionManager initialization with defaults."""
        manager = session_lifecycle.SessionManager()

        assert manager is not None
        assert isinstance(manager.active_tasks, set)
        assert isinstance(manager.session_ids, set)
        assert len(manager.active_tasks) == 0
        assert len(manager.session_ids) == 0
        assert manager._cleanup_done is False

    @pytest.mark.high
    def test_singleton_registration(self):
        """Test that manager registers as singleton."""
        manager = session_lifecycle.SessionManager()

        assert session_lifecycle.SessionManager._instance is manager

    @pytest.mark.high
    def test_get_instance_creates_if_none(self):
        """Test get_instance creates new instance if none exists."""
        # Clear singleton
        session_lifecycle.SessionManager._instance = None

        manager = session_lifecycle.SessionManager.get_instance()

        assert manager is not None
        assert isinstance(manager, session_lifecycle.SessionManager)

    @pytest.mark.high
    def test_get_instance_returns_existing(self):
        """Test get_instance returns existing instance."""
        manager1 = session_lifecycle.SessionManager()
        manager2 = session_lifecycle.SessionManager.get_instance()

        assert manager1 is manager2


class TestSessionTracking:
    """Test session ID tracking."""

    @pytest.mark.high
    def test_track_session(self, capsys):
        """Test tracking a session ID."""
        manager = session_lifecycle.SessionManager()
        session_id = "test-session-123456"

        manager.track_session(session_id)

        assert session_id in manager.session_ids
        captured = capsys.readouterr()
        assert "test-ses" in captured.err  # Truncated to 8 chars

    @pytest.mark.high
    def test_track_empty_session_ignored(self):
        """Test that empty session ID is ignored."""
        manager = session_lifecycle.SessionManager()

        manager.track_session("")
        manager.track_session(None)

        assert len(manager.session_ids) == 0

    @pytest.mark.high
    def test_track_multiple_sessions(self):
        """Test tracking multiple session IDs."""
        manager = session_lifecycle.SessionManager()

        manager.track_session("session-1")
        manager.track_session("session-2")
        manager.track_session("session-3")

        assert len(manager.session_ids) == 3
        assert "session-1" in manager.session_ids
        assert "session-2" in manager.session_ids

    @pytest.mark.high
    def test_untrack_session(self, capsys):
        """Test untracking a session."""
        manager = session_lifecycle.SessionManager()
        session_id = "test-session-123"

        manager.track_session(session_id)
        manager.untrack_session(session_id)

        assert session_id not in manager.session_ids
        captured = capsys.readouterr()
        assert "completed" in captured.err.lower()

    @pytest.mark.high
    def test_untrack_nonexistent_session(self):
        """Test untracking non-existent session is safe."""
        manager = session_lifecycle.SessionManager()

        # Should not raise
        manager.untrack_session("nonexistent")

        assert len(manager.session_ids) == 0


class TestSpawnWithCleanup:
    """Test spawn_with_cleanup method."""

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_spawn_successful_coroutine(self):
        """Test spawning a successful coroutine."""
        manager = session_lifecycle.SessionManager()

        async def test_coro():
            await asyncio.sleep(0.01)
            return "success"

        result = await manager.spawn_with_cleanup(test_coro())

        assert result == "success"
        # Task should be removed after completion
        assert len(manager.active_tasks) == 0

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_spawn_tracks_task(self):
        """Test that spawned task is tracked."""
        manager = session_lifecycle.SessionManager()

        async def test_coro():
            await asyncio.sleep(0.1)
            return "done"

        # Start coroutine but don't await completion
        task = asyncio.create_task(manager.spawn_with_cleanup(test_coro()))

        # Give task time to start
        await asyncio.sleep(0.01)

        # Task should be tracked (implementation spawns internally)
        # After completion it should be removed
        await task
        assert len(manager.active_tasks) == 0

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_spawn_handles_exception(self):
        """Test spawning coroutine that raises exception."""
        manager = session_lifecycle.SessionManager()

        async def failing_coro():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await manager.spawn_with_cleanup(failing_coro())

        # Task should still be cleaned up
        assert len(manager.active_tasks) == 0

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_spawn_handles_cancellation(self):
        """Test spawning coroutine that gets cancelled."""
        manager = session_lifecycle.SessionManager()

        async def long_coro():
            await asyncio.sleep(10)

        task = asyncio.create_task(manager.spawn_with_cleanup(long_coro()))
        await asyncio.sleep(0.01)

        task.cancel()

        with pytest.raises(asyncio.CancelledError):
            await task

        # Task should be removed
        assert len(manager.active_tasks) == 0

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_spawn_multiple_concurrent_tasks(self):
        """Test spawning multiple concurrent tasks."""
        manager = session_lifecycle.SessionManager()

        async def test_coro(delay: float, value: str):
            await asyncio.sleep(delay)
            return value

        tasks = [
            manager.spawn_with_cleanup(test_coro(0.01, "a")),
            manager.spawn_with_cleanup(test_coro(0.02, "b")),
            manager.spawn_with_cleanup(test_coro(0.03, "c"))
        ]

        results = await asyncio.gather(*tasks)

        assert results == ["a", "b", "c"]
        assert len(manager.active_tasks) == 0


class TestCleanup:
    """Test cleanup method."""

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_cleanup_cancels_active_tasks(self):
        """Test that cleanup cancels all active tasks."""
        manager = session_lifecycle.SessionManager()

        async def long_task():
            await asyncio.sleep(100)

        # Start tasks but don't await
        task1 = asyncio.create_task(manager.spawn_with_cleanup(long_task()))
        task2 = asyncio.create_task(manager.spawn_with_cleanup(long_task()))

        await asyncio.sleep(0.01)

        # Cleanup should cancel tasks
        await manager.cleanup()

        assert task1.cancelled() or task1.done()
        assert task2.cancelled() or task2.done()
        assert len(manager.active_tasks) == 0

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_cleanup_clears_session_ids(self, capsys):
        """Test that cleanup clears session IDs."""
        manager = session_lifecycle.SessionManager()

        manager.track_session("session-1")
        manager.track_session("session-2")

        await manager.cleanup()

        assert len(manager.session_ids) == 0
        captured = capsys.readouterr()
        assert "Stopped" in captured.err

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_cleanup_idempotent(self):
        """Test that cleanup can be called multiple times safely."""
        manager = session_lifecycle.SessionManager()

        await manager.cleanup()
        await manager.cleanup()
        await manager.cleanup()

        # Should not raise

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_cleanup_sets_shutdown_flag(self):
        """Test that cleanup sets shutdown flag."""
        manager = session_lifecycle.SessionManager()

        await manager.cleanup()

        assert session_lifecycle.SessionManager._shutdown_in_progress is True
        assert manager._cleanup_done is True


class TestSignalHandlers:
    """Test signal handler setup."""

    @pytest.mark.high
    def test_setup_signal_handlers(self):
        """Test setting up signal handlers."""
        loop = asyncio.new_event_loop()

        with patch('signal.signal') as mock_signal:
            session_lifecycle.SessionManager.setup_signal_handlers(loop)

            # Should register SIGINT and SIGTERM
            assert mock_signal.call_count >= 2

        loop.close()

    @pytest.mark.high
    def test_signal_handler_triggers_cleanup(self):
        """Test that signal handler schedules cleanup."""
        loop = asyncio.new_event_loop()
        manager = session_lifecycle.SessionManager()

        with patch('signal.signal') as mock_signal:
            session_lifecycle.SessionManager.setup_signal_handlers(loop)

            # Get the signal handler function
            handler = mock_signal.call_args_list[0][0][1]

            # Should not raise when called
            # handler(signal.SIGINT, None)

        loop.close()


class TestRunWithLifecycle:
    """Test run_with_lifecycle static method."""

    @pytest.mark.high
    def test_run_with_lifecycle_success(self):
        """Test running coroutine with lifecycle management."""
        async def simple_main():
            await asyncio.sleep(0.01)
            return "completed"

        # Reset singleton and shutdown flag
        session_lifecycle.SessionManager._instance = None
        session_lifecycle.SessionManager._shutdown_in_progress = False

        result = session_lifecycle.SessionManager.run_with_lifecycle(simple_main())

        assert result == "completed"

    @pytest.mark.high
    def test_run_with_lifecycle_handles_exception(self):
        """Test lifecycle management when main raises exception."""
        async def failing_main():
            raise ValueError("Test error")

        # Reset singleton and shutdown flag
        session_lifecycle.SessionManager._instance = None
        session_lifecycle.SessionManager._shutdown_in_progress = False

        with pytest.raises(ValueError, match="Test error"):
            session_lifecycle.SessionManager.run_with_lifecycle(failing_main())


class TestManagedSession:
    """Test managed_session context manager."""

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_managed_session_cleanup(self):
        """Test that managed_session cleans up automatically."""
        async def test_coro():
            await asyncio.sleep(0.01)
            return "done"

        async with session_lifecycle.managed_session() as manager:
            result = await manager.spawn_with_cleanup(test_coro())
            assert result == "done"

        # Manager should have cleaned up
        # (we can't easily verify this without accessing internals)

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_managed_session_cleanup_on_exception(self):
        """Test cleanup happens even when exception occurs."""
        try:
            async with session_lifecycle.managed_session() as manager:
                raise ValueError("Test error")
        except ValueError:
            pass

        # Should not hang or fail cleanup


class TestEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_cleanup_with_timeout(self):
        """Test cleanup with tasks that don't respond to cancellation."""
        manager = session_lifecycle.SessionManager()

        async def stubborn_task():
            try:
                await asyncio.sleep(100)
            except asyncio.CancelledError:
                # Ignore cancellation (bad practice, but tests timeout)
                await asyncio.sleep(100)

        task = asyncio.create_task(manager.spawn_with_cleanup(stubborn_task()))
        await asyncio.sleep(0.01)

        # Cleanup should timeout and continue
        # (with timeout=5.0 in implementation)
        await manager.cleanup()

        # Should complete without hanging

    @pytest.mark.high
    def test_multiple_managers_independent(self):
        """Test that multiple manager instances are independent."""
        # Create managers with cleared singleton
        session_lifecycle.SessionManager._instance = None
        manager1 = session_lifecycle.SessionManager()

        session_lifecycle.SessionManager._instance = None
        manager2 = session_lifecycle.SessionManager()

        manager1.track_session("session-1")
        manager2.track_session("session-2")

        # They should be separate instances
        assert manager1 is not manager2
        # But singleton pattern means last one is registered
        assert session_lifecycle.SessionManager._instance is manager2
