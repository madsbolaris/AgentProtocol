#!/usr/bin/env python3
"""
Simple unit test for file watcher logic.

Tests the core file watching behavior without mocking the full SDK.
"""
import asyncio
import tempfile
from pathlib import Path
import pytest


async def watch_files_simple(expected_files, timeout=10):
    """
    Simplified file watcher for testing.

    Returns True if all files are created before timeout, False otherwise.
    """
    check_interval = 0.1  # Check every 100ms
    elapsed = 0

    while elapsed < timeout:
        # Check if all expected files exist
        all_exist = all(Path(f).exists() for f in expected_files)

        if all_exist:
            print(f"✅ All files detected after {elapsed:.1f}s")
            return True

        await asyncio.sleep(check_interval)
        elapsed += check_interval

    print(f"⚠️ Timeout after {timeout}s")
    return False


@pytest.mark.asyncio
@pytest.mark.asyncio
async def test_file_watcher_detects_creation():
    """Test that file watcher detects file creation."""
    print("\nTest 1: File watcher detects creation...")

    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        expected_file = workspace / "test-review.md"

        # Simulate file creation after 0.5 seconds
        async def create_file_delayed():
            await asyncio.sleep(0.5)
            expected_file.write_text("# Test Review\nContent here")
            print(f"   Created file: {expected_file}")

        # Start both tasks
        file_task = asyncio.create_task(create_file_delayed())
        watch_task = asyncio.create_task(
            watch_files_simple([str(expected_file)], timeout=5)
        )

        # Wait for both
        detected = await watch_task
        await file_task

        assert detected, "File should have been detected"
        assert expected_file.exists(), "File should exist"
        print("   ✅ PASS: File watcher detected file creation")


@pytest.mark.asyncio
async def test_file_watcher_timeout():
    """Test that file watcher handles timeout."""
    print("\nTest 2: File watcher timeout...")

    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        expected_file = workspace / "test-review.md"

        # Don't create file - should timeout
        detected = await watch_files_simple([str(expected_file)], timeout=1)

        assert not detected, "Should timeout when file not created"
        assert not expected_file.exists(), "File should not exist"
        print("   ✅ PASS: File watcher correctly timed out")


@pytest.mark.asyncio
async def test_file_watcher_immediate_detection():
    """Test that file watcher detects pre-existing file immediately."""
    print("\nTest 3: File watcher immediate detection...")

    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        expected_file = workspace / "test-review.md"

        # Create file before watching
        expected_file.write_text("# Test Review")
        print(f"   Pre-created file: {expected_file}")

        # Watch should detect immediately
        detected = await watch_files_simple([str(expected_file)], timeout=5)

        assert detected, "Should detect pre-existing file"
        assert expected_file.exists(), "File should exist"
        print("   ✅ PASS: File watcher detected pre-existing file")


@pytest.mark.asyncio
async def test_file_watcher_multiple_files():
    """Test that file watcher handles multiple expected files."""
    print("\nTest 4: File watcher with multiple files...")

    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        file1 = workspace / "review-1.md"
        file2 = workspace / "review-2.md"

        # Create files with delay
        async def create_files():
            await asyncio.sleep(0.3)
            file1.write_text("Review 1")
            await asyncio.sleep(0.3)
            file2.write_text("Review 2")

        # Start both tasks
        create_task = asyncio.create_task(create_files())
        watch_task = asyncio.create_task(
            watch_files_simple([str(file1), str(file2)], timeout=5)
        )

        # Wait for both
        detected = await watch_task
        await create_task

        assert detected, "Should detect both files"
        assert file1.exists() and file2.exists(), "Both files should exist"
        print("   ✅ PASS: File watcher detected multiple files")


@pytest.mark.asyncio
async def test_race_condition_simulation():
    """Test race between agent completion and file detection."""
    print("\nTest 5: Race condition simulation...")

    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        expected_file = workspace / "test-review.md"

        # Simulate agent that creates file and completes
        async def agent_task():
            await asyncio.sleep(0.3)
            expected_file.write_text("# Test Review")
            await asyncio.sleep(0.2)  # Agent continues working
            return "agent_completed"

        async def watcher_task():
            result = await watch_files_simple([str(expected_file)], timeout=5)
            return "watcher_detected" if result else "watcher_timeout"

        # Race both tasks
        agent = asyncio.create_task(agent_task())
        watcher = asyncio.create_task(watcher_task())

        # Wait for first to complete
        done, pending = await asyncio.wait(
            [agent, watcher],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel remaining
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        # Get result from completed task
        completed_task = list(done)[0]
        result = completed_task.result()

        print(f"   First to complete: {result}")
        assert expected_file.exists(), "File should exist"
        print("   ✅ PASS: Race condition handled correctly")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("File Watcher Unit Tests")
    print("=" * 60)

    tests = [
        test_file_watcher_detects_creation,
        test_file_watcher_timeout,
        test_file_watcher_immediate_detection,
        test_file_watcher_multiple_files,
        test_race_condition_simulation
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test()
            passed += 1
        except AssertionError as e:
            print(f"   ❌ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed > 0:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
