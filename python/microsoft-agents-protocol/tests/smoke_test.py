"""
Smoke test to verify test infrastructure can import and run.

This tests the infrastructure without requiring:
- Running agent
- Foundry credentials
- Golden files or recordings
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))


def test_imports():
    """Test that all test utilities can be imported."""
    print("Testing imports...")

    # Core utilities
    from utils.test_helpers import (
        get_test_mode,
        get_test_data_dir,
        load_input_file,
    )
    print("  ✅ test_helpers imports")

    # Mock infrastructure
    from mocks.mock_llm_client import MockLLMClient
    # Note: LLM recording is now done by .NET BasicM365Agent bot
    print("  ✅ mock infrastructure imports")


def test_test_mode():
    """Test mode detection."""
    print("Testing mode detection...")
    from utils.test_helpers import get_test_mode

    # Should default to "test" mode
    mode = get_test_mode()
    assert mode == "test", f"Expected 'test' mode, got '{mode}'"
    print(f"  ✅ Mode detection works (mode={mode})")


def test_paths():
    """Test path resolution."""
    print("Testing path resolution...")
    from utils.test_helpers import get_test_data_dir

    test_data_dir = get_test_data_dir()
    assert test_data_dir.exists(), f"test-data directory doesn't exist: {test_data_dir}"
    assert (test_data_dir / "input").exists(), "test-data/input doesn't exist"
    assert (test_data_dir / "results").exists(), "test-data/results doesn't exist"
    print(f"  ✅ Paths resolve correctly")
    print(f"     test-data: {test_data_dir}")


def test_input_files():
    """Test that input files can be loaded."""
    print("Testing input file loading...")
    from utils.test_helpers import load_input_file, get_test_data_dir

    test_data_dir = get_test_data_dir()
    input_dir = test_data_dir / "input" / "threads"

    # Check all 4 test input files exist
    test_files = [
        "50-weather-query",
        "51-time-query",
        "52-multi-function",
        "53-no-function"
    ]

    for test_file in test_files:
        xml_path = input_dir / f"{test_file}.xml"
        assert xml_path.exists(), f"Input file missing: {xml_path}"

        # Load it using the subdir parameter
        content = load_input_file(test_file, subdir="threads")
        assert content, f"Input file {test_file} is empty"
        assert isinstance(content, str), f"Input file should be string"

    print(f"  ✅ All {len(test_files)} input files load correctly")


def test_golden_file_paths():
    """Test that golden file paths are correct (json not wait)."""
    print("Testing golden file paths...")
    from utils.test_helpers import get_test_data_dir

    test_data_dir = get_test_data_dir()

    # JSON path should exist (renamed from wait)
    json_dir = test_data_dir / "results" / "basic-m365" / "json"
    assert json_dir.exists(), f"JSON directory doesn't exist: {json_dir}"
    print(f"  ✅ JSON golden files directory exists")

    # Wait path should NOT exist anymore
    wait_dir = test_data_dir / "results" / "basic-m365" / "wait"
    if wait_dir.exists():
        print(f"  ⚠️  Old 'wait' directory still exists: {wait_dir}")
    else:
        print(f"  ✅ Old 'wait' directory removed")

    # XML path should exist
    xml_dir = test_data_dir / "results" / "basic-m365" / "xml"
    assert xml_dir.exists(), f"XML directory doesn't exist: {xml_dir}"
    print(f"  ✅ XML golden files directory exists")


def test_mock_client():
    """Test that mock LLM client works."""
    print("Testing mock LLM client...")
    from mocks.mock_llm_client import MockLLMClient
    from pathlib import Path

    recordings_dir = Path("/tmp/test-recordings")
    recordings_dir.mkdir(exist_ok=True)

    # Should work even with empty recordings directory
    mock = MockLLMClient(recordings_dir)
    print(f"  ✅ Mock client instantiates")


def main():
    """Run all smoke tests."""
    print("\n🧪 Running Test Infrastructure Smoke Tests")
    print("=" * 60)
    print()

    tests = [
        ("Imports", test_imports),
        ("Mode Detection", test_test_mode),
        ("Path Resolution", test_paths),
        ("Input Files", test_input_files),
        ("Golden File Paths", test_golden_file_paths),
        ("Mock Client", test_mock_client),
    ]

    failed = []

    for name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"  ❌ {name} failed: {e}")
            failed.append(name)
            import traceback
            traceback.print_exc()
        print()

    print("=" * 60)
    if failed:
        print(f"❌ {len(failed)} test(s) failed: {', '.join(failed)}")
        return 1
    else:
        print(f"✅ All {len(tests)} smoke tests passed!")
        print()
        print("Infrastructure is ready! Next steps:")
        print("  1. Generate golden files: ./scripts/generate_basic_m365_golden_files.sh")
        print("  2. Run integration tests: ./scripts/test_basic_m365.sh")
        return 0


if __name__ == "__main__":
    sys.exit(main())
