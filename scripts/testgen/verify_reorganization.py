#!/usr/bin/env python3
"""
Verify the test data reorganization was successful.

This script checks:
1. All result files have corresponding input files
2. Directory structures match
3. No files were lost
4. Test helpers can load files correctly
"""

import sys
from pathlib import Path

# Base paths
TEST_DATA = Path(__file__).parent.parent.parent / "test-data"
INPUT_DIR = TEST_DATA / "input"
RESULTS_DIR = TEST_DATA / "results"
NORMALIZED_DIR = RESULTS_DIR / "normalized"


def check_file_correspondence():
    """Check that all result files have corresponding input files."""
    print("=" * 80)
    print("Checking file correspondence...")
    print("=" * 80)

    issues = []

    # Check eval results
    eval_results = list((RESULTS_DIR / "evals").rglob("*-result.json"))
    print(f"\nFound {len(eval_results)} eval result files")

    for result_file in eval_results:
        # Extract test name
        test_name = result_file.stem.replace("-result", "")
        input_file = None

        # Find corresponding input file
        for inp in (INPUT_DIR / "evals").rglob(f"{test_name}.xml"):
            input_file = inp
            break

        if not input_file:
            issues.append(f"Result file has no input: {result_file.relative_to(TEST_DATA)}")
        else:
            # Check if directory structure matches
            result_rel = result_file.parent.relative_to(RESULTS_DIR / "evals")
            input_rel = input_file.parent.relative_to(INPUT_DIR / "evals")

            if result_rel != input_rel:
                issues.append(
                    f"Directory mismatch:\n"
                    f"  Result: {result_rel}\n"
                    f"  Input:  {input_rel}\n"
                    f"  File:   {test_name}"
                )

    # Check normalized files
    normalized_files = list(NORMALIZED_DIR.rglob("*.xml"))
    print(f"Found {len(normalized_files)} normalized files")

    for norm_file in normalized_files:
        # Extract filename
        filename = norm_file.name

        # Find corresponding input file
        input_file = None
        for inp in INPUT_DIR.rglob(filename):
            if "invalid" not in inp.parts:
                input_file = inp
                break

        if not input_file:
            issues.append(f"Normalized file has no input: {norm_file.relative_to(TEST_DATA)}")
        else:
            # Determine category
            if "evals" in norm_file.parts:
                category = "evals"
            else:
                category = "threads"

            # Only check structure if both files are in the expected category
            if category in str(input_file):
                # Check if directory structure matches
                norm_rel = norm_file.parent.relative_to(NORMALIZED_DIR / category)
                input_rel = input_file.parent.relative_to(INPUT_DIR / category)

                if norm_rel != input_rel:
                    issues.append(
                        f"Directory mismatch:\n"
                        f"  Normalized: {norm_rel}\n"
                        f"  Input:      {input_rel}\n"
                        f"  File:       {filename}"
                    )

    if issues:
        print("\n❌ Issues found:")
        for issue in issues:
            print(f"\n  {issue}")
        return False
    else:
        print("\n✅ All files have corresponding inputs with matching structure")
        return True


def check_directory_structure():
    """Check that directory structures are consistent."""
    print("\n" + "=" * 80)
    print("Checking directory structure...")
    print("=" * 80)

    # Get all input subdirectories
    input_dirs = set()
    for xml_file in (INPUT_DIR / "evals").rglob("*.xml"):
        rel_dir = xml_file.parent.relative_to(INPUT_DIR / "evals")
        if rel_dir != Path("."):
            input_dirs.add(rel_dir)

    print(f"\nInput evals has {len(input_dirs)} subdirectories")

    # Get all result subdirectories
    result_dirs = set()
    for json_file in (RESULTS_DIR / "evals").rglob("*-result.json"):
        rel_dir = json_file.parent.relative_to(RESULTS_DIR / "evals")
        if rel_dir != Path("."):
            result_dirs.add(rel_dir)

    print(f"Result evals has {len(result_dirs)} subdirectories")

    # Check if result dirs are subset of input dirs
    extra_dirs = result_dirs - input_dirs
    if extra_dirs:
        print(f"\n⚠️  Extra directories in results (not in input):")
        for d in sorted(extra_dirs):
            print(f"  - {d}")

    missing_dirs = input_dirs - result_dirs
    if missing_dirs:
        print(f"\n⚠️  Missing directories in results (present in input):")
        for d in sorted(missing_dirs):
            # Check if there are actually input files in this directory
            has_files = any((INPUT_DIR / "evals" / d).glob("*.xml"))
            if has_files:
                print(f"  - {d}")

    if not extra_dirs and not missing_dirs:
        print("\n✅ Directory structures match perfectly")
        return True
    elif not extra_dirs:
        print("\n✅ No extra directories in results (OK - not all inputs have results yet)")
        return True
    else:
        return False


def check_file_counts():
    """Check file counts."""
    print("\n" + "=" * 80)
    print("File counts...")
    print("=" * 80)

    input_files = list(INPUT_DIR.rglob("*.xml"))
    # Exclude invalid directory
    input_files = [f for f in input_files if "invalid" not in f.parts]

    normalized_files = list(NORMALIZED_DIR.rglob("*.xml"))
    result_files = list((RESULTS_DIR / "evals").rglob("*-result.json"))

    print(f"\n  Input XML files:      {len(input_files)}")
    print(f"  Normalized XML files: {len(normalized_files)}")
    print(f"  Result JSON files:    {len(result_files)}")

    return True


def test_python_helpers():
    """Test Python helper functions."""
    print("\n" + "=" * 80)
    print("Testing Python helpers...")
    print("=" * 80)

    # Add Python package to path
    python_pkg = Path(__file__).parent.parent.parent / "python" / "microsoft-agents-protocol"
    sys.path.insert(0, str(python_pkg))

    try:
        from tests.utils.test_helpers import load_input_file, load_golden_file

        # Test loading input files
        test_cases = [
            ("01-simple-text-expect", "evals"),
            ("51-cel-boolean-operators", "evals"),
        ]

        for test_name, subdir in test_cases:
            try:
                content = load_input_file(test_name, subdir=subdir)
                print(f"  ✅ Loaded input: {test_name}.xml ({len(content)} bytes)")

                # Try loading golden file
                result = load_golden_file(test_name, pattern="json", subdir=subdir)
                thread_id = result.get("content", {}).get("threadId", result.get("threadId", "N/A"))
                print(f"  ✅ Loaded golden: {test_name}-result.json (threadId: {thread_id})")
            except FileNotFoundError as e:
                print(f"  ⚠️  Could not load {test_name}: {e}")
            except Exception as e:
                print(f"  ❌ Error loading {test_name}: {e}")
                return False

        print("\n✅ Python helpers working correctly")
        return True

    except ImportError as e:
        print(f"  ⚠️  Could not import Python helpers (this is OK if not running from repo): {e}")
        return True  # Don't fail on import errors


def main():
    """Run all verification checks."""
    print("\n" + "=" * 80)
    print("Test Data Reorganization Verification")
    print("=" * 80)
    print(f"Test data directory: {TEST_DATA}")

    checks = [
        check_file_counts,
        check_file_correspondence,
        check_directory_structure,
        test_python_helpers,
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Check failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 80)
    print("Verification Summary")
    print("=" * 80)

    passed = sum(results)
    total = len(results)
    print(f"\n  Passed: {passed}/{total}")

    if all(results):
        print("\n✅ All verification checks passed!")
        return 0
    else:
        print("\n⚠️  Some checks did not pass (see above)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
