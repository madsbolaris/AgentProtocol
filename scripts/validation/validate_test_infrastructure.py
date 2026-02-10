#!/usr/bin/env python3
"""
Validate test infrastructure setup.

Checks for:
- Required directory structure
- Test input files
- Test implementation files
- Path configurations
- Golden files and LLM recordings
"""

import argparse
import sys
from pathlib import Path


def check_directory(path: Path, name: str) -> bool:
    """Check if a directory exists."""
    if path.exists() and path.is_dir():
        print(f"   ✅ {name} exists")
        return True
    else:
        print(f"   ❌ {name} missing")
        return False


def check_file(path: Path, name: str) -> bool:
    """Check if a file exists."""
    if path.exists() and path.is_file():
        print(f"   ✅ {name} exists")
        return True
    else:
        print(f"   ❌ {name} missing")
        return False


def check_file_content(path: Path, pattern: str, description: str) -> bool:
    """Check if a file contains a pattern."""
    if not path.exists():
        print(f"   ⚠️  {path.name} not found")
        return False

    content = path.read_text()
    if pattern in content:
        print(f"   ✅ {description}")
        return True
    else:
        print(f"   ❌ {description}")
        return False


def validate_infrastructure():
    """Validate test infrastructure."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent

    print("🔍 Validating Test Infrastructure")
    print("=" * 34)
    print()
    print(f"📁 Repository root: {repo_root}")
    print()

    errors = []

    # Check directory structure
    print("📂 Checking directory structure...")

    directories = [
        (repo_root / "test-data", "test-data/"),
        (repo_root / "test-data" / "input", "test-data/input/"),
        (repo_root / "test-data" / "results" / "function-tools" / "json",
         "test-data/results/function-tools/json/"),
        (repo_root / "test-data" / "results" / "function-tools" / "xml",
         "test-data/results/function-tools/xml/"),
        (repo_root / "test-data" / "llm-recordings" / "function-tools",
         "test-data/llm-recordings/function-tools/"),
    ]

    for path, name in directories:
        if not check_directory(path, name):
            errors.append(f"Missing directory: {name}")

    print()

    # Check input files
    print("📄 Checking input files...")
    threads_dir = repo_root / "test-data" / "input" / "threads"
    if threads_dir.exists():
        # Get all XML files recursively, excluding invalid subdirectory
        all_input_files = list(threads_dir.rglob("*.xml"))
        input_files = [f for f in all_input_files if "invalid" not in f.parts]
        input_count = len(input_files)
        invalid_count = len(all_input_files) - input_count
        print(f"   Found {input_count} valid input test files")
        print(f"   Found {invalid_count} invalid test files (for negative testing)")

        if input_count >= 80:
            print("   ✅ Expected number of test files present (80+)")
        else:
            print(f"   ⚠️  Expected 80+ input files, found {input_count}")

    print()

    # Check test files
    print("🧪 Checking test files...")

    test_files = [
        (repo_root / "python" / "microsoft-agents-protocol" / "tests" / "integration" /
         "test_function_tools_generation.py", "test_function_tools_generation.py"),
        (repo_root / "python" / "microsoft-agents-protocol" / "tests" / "integration" /
         "test_function_tools_integration.py", "test_function_tools_integration.py"),
        (repo_root / "python" / "microsoft-agents-protocol" / "tests" / "utils" /
         "test_helpers.py", "test_helpers.py"),
    ]

    for path, name in test_files:
        if not check_file(path, name):
            errors.append(f"Missing test file: {name}")

    print()

    # Verify path updates
    print("🔧 Verifying path updates...")

    check_file_content(
        repo_root / "python" / "microsoft-agents-protocol" / "tests" / "utils" / "test_helpers.py",
        'pattern: Literal["json", "xml"]',
        "test_helpers.py uses 'json' pattern"
    )

    # Note: Some scripts may have been moved/renamed, skip if not found
    test_script = repo_root / "scripts" / "test_function_tools.sh"
    if test_script.exists():
        check_file_content(
            test_script,
            "results/function-tools/json",
            "test_function_tools.sh uses json path"
        )

    gen_script = repo_root / "scripts" / "generate_function_tools_golden_files.sh"
    if gen_script.exists():
        check_file_content(
            gen_script,
            "results/function-tools/json",
            "generate_function_tools_golden_files.sh uses json path"
        )

    print()

    # Check golden files and recordings
    print("📊 Checking golden files and recordings...")

    json_dir = repo_root / "test-data" / "results" / "function-tools" / "json"
    xml_dir = repo_root / "test-data" / "results" / "function-tools" / "xml"
    recordings_dir = repo_root / "test-data" / "llm-recordings" / "function-tools"

    json_count = len(list(json_dir.glob("*.json"))) if json_dir.exists() else 0
    xml_count = len(list(xml_dir.glob("*.xml"))) if xml_dir.exists() else 0
    recording_count = len(list(recordings_dir.glob("*.response.json"))) if recordings_dir.exists() else 0

    print(f"   JSON golden files: {json_count}")
    print(f"   XML golden files: {xml_count}")
    print(f"   LLM recordings: {recording_count}")

    if json_count == 0 and recording_count == 0:
        print()
        print("   ℹ️  No golden files or recordings yet")
        print("   Run generation to create them:")
        print("      python scripts/testgen/generate_golden_datasets.py")
    else:
        print("   ✅ Golden files and/or recordings exist")

    print()
    print("=" * 34)

    if errors:
        print("❌ Infrastructure validation failed!")
        print()
        print("Errors found:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("✅ Infrastructure validation complete!")
        print()
        print("Next steps:")
        print("  1. Generate golden files:")
        print("     python scripts/testgen/generate_golden_datasets.py")
        print()
        print("  2. Run tests:")
        print("     pytest python/microsoft-agents-protocol/tests/")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate test infrastructure setup"
    )
    parser.parse_args()
    validate_infrastructure()


if __name__ == "__main__":
    main()
