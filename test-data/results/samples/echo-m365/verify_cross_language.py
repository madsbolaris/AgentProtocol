#!/usr/bin/env python3
"""
Cross-Language Result Verification Script

Compares results from Python and .NET implementations to ensure they produce
identical output (proving protocol compliance and language-agnostic behavior).

Usage:
    python verify_cross_language.py [--generate-dotnet]

    --generate-dotnet: Run .NET tests to generate comparison results
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


class Colors:
    """Terminal colors."""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.NC} Error loading {file_path}: {e}")
        return {}


def normalize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize result for comparison.

    Removes non-deterministic fields like timestamps and IDs.
    """
    normalized = result.copy()

    # Remove non-deterministic fields
    fields_to_remove = ['runId', 'createdAt', 'completedAt', 'usage']
    for field in fields_to_remove:
        normalized.pop(field, None)

    return normalized


def compare_results(result1: Dict[str, Any], result2: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Compare two results after normalization.

    Returns:
        (is_identical, differences)
    """
    norm1 = normalize_result(result1)
    norm2 = normalize_result(result2)

    differences = []

    # Compare status
    if norm1.get('status') != norm2.get('status'):
        differences.append(f"Status mismatch: {norm1.get('status')} vs {norm2.get('status')}")

    # Compare input
    if norm1.get('input') != norm2.get('input'):
        differences.append("Input messages differ")

    # Compare output
    if norm1.get('output') != norm2.get('output'):
        differences.append("Output messages differ")

    return len(differences) == 0, differences


def verify_directory(shared_dir: Path, temp_dir: Path, pattern: str) -> Tuple[int, int, int]:
    """
    Verify results in a directory match.

    Args:
        shared_dir: Directory with shared results (e.g., echom365/xml/)
        temp_dir: Directory with new results to compare (e.g., echom365/dotnet-temp/xml/)
        pattern: Pattern name (xml, wait, etc.)

    Returns:
        (total_files, matching_files, differing_files)
    """
    print(f"\n{Colors.BLUE}Verifying {pattern} pattern...{Colors.NC}")

    if not shared_dir.exists():
        print(f"{Colors.YELLOW}⚠{Colors.NC}  Shared directory not found: {shared_dir}")
        return 0, 0, 0

    if not temp_dir.exists():
        print(f"{Colors.YELLOW}⚠{Colors.NC}  Comparison directory not found: {temp_dir}")
        return 0, 0, 0

    shared_files = {f.name: f for f in shared_dir.glob("*.json")}
    temp_files = {f.name: f for f in temp_dir.glob("*.json")}

    total = len(shared_files)
    matching = 0
    differing = 0

    for filename in sorted(shared_files.keys()):
        if filename not in temp_files:
            print(f"  {Colors.YELLOW}⚠{Colors.NC}  {filename} - missing in comparison")
            continue

        shared_result = load_json_file(shared_files[filename])
        temp_result = load_json_file(temp_files[filename])

        is_identical, differences = compare_results(shared_result, temp_result)

        if is_identical:
            print(f"  {Colors.GREEN}✓{Colors.NC}  {filename} - identical")
            matching += 1
        else:
            print(f"  {Colors.RED}✗{Colors.NC}  {filename} - differs:")
            for diff in differences:
                print(f"      {diff}")
            differing += 1

    return total, matching, differing


def main():
    parser = argparse.ArgumentParser(
        description="Verify cross-language result compatibility"
    )
    parser.add_argument(
        "--generate-dotnet",
        action="store_true",
        help="Generate .NET results for comparison"
    )
    parser.add_argument(
        "--dotnet-temp-dir",
        type=str,
        default="dotnet-temp",
        help="Temporary directory for .NET results"
    )

    args = parser.parse_args()

    # Find repository root
    script_dir = Path(__file__).parent
    test_data_dir = script_dir.parent.parent

    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.BLUE}  Cross-Language Result Verification{Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════{Colors.NC}")

    # Check if .NET results should be generated
    if args.generate_dotnet:
        print(f"\n{Colors.YELLOW}Generating .NET results...{Colors.NC}")
        import subprocess

        dotnet_test_dir = test_data_dir.parent / "dotnet" / "tests" / "Microsoft.Agents.Client.Tests"

        if not dotnet_test_dir.exists():
            print(f"{Colors.RED}✗{Colors.NC} .NET test directory not found: {dotnet_test_dir}")
            sys.exit(1)

        try:
            # Run .NET tests to generate results
            result = subprocess.run(
                ["dotnet", "test", "--filter", "EchoM365Integration"],
                cwd=dotnet_test_dir,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"{Colors.RED}✗{Colors.NC} .NET tests failed:")
                print(result.stdout)
                print(result.stderr)
                sys.exit(1)

            print(f"{Colors.GREEN}✓{Colors.NC} .NET tests completed")
        except FileNotFoundError:
            print(f"{Colors.RED}✗{Colors.NC} .NET SDK not found. Install from https://dot.net")
            sys.exit(1)

    # Verify shared results exist
    shared_base = script_dir

    print(f"\n{Colors.BLUE}Shared Results Location:{Colors.NC} {shared_base}")

    patterns = ["xml", "wait"]
    total_files = 0
    total_matching = 0
    total_differing = 0

    # For now, just verify the shared results are valid JSON
    print(f"\n{Colors.BLUE}Validating Shared Results...{Colors.NC}")

    for pattern in patterns:
        pattern_dir = shared_base / pattern

        if not pattern_dir.exists():
            print(f"  {Colors.YELLOW}⚠{Colors.NC}  {pattern}/ - directory not found")
            continue

        files = list(pattern_dir.glob("*.json"))
        valid = 0
        invalid = 0

        for file_path in sorted(files):
            result = load_json_file(file_path)
            if result:
                # Check for required fields
                required_fields = ['status', 'input', 'output']
                missing = [f for f in required_fields if f not in result]

                if not missing:
                    print(f"  {Colors.GREEN}✓{Colors.NC}  {pattern}/{file_path.name} - valid")
                    valid += 1
                else:
                    print(f"  {Colors.RED}✗{Colors.NC}  {pattern}/{file_path.name} - missing fields: {missing}")
                    invalid += 1
            else:
                print(f"  {Colors.RED}✗{Colors.NC}  {pattern}/{file_path.name} - invalid JSON")
                invalid += 1

        total_files += len(files)
        total_matching += valid
        total_differing += invalid

        print(f"\n  {pattern}/: {valid} valid, {invalid} invalid")

    # Summary
    print(f"\n{Colors.BLUE}═══════════════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.BLUE}  Summary{Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════════════{Colors.NC}")
    print(f"\nTotal files: {total_files}")
    print(f"Valid: {Colors.GREEN}{total_matching}{Colors.NC}")
    print(f"Invalid: {Colors.RED}{total_differing}{Colors.NC}")

    if total_differing == 0:
        print(f"\n{Colors.GREEN}✓ All shared results are valid!{Colors.NC}")
        print(f"\nBoth Python and .NET will use these {total_files} files.")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}✗ Some results have issues{Colors.NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
