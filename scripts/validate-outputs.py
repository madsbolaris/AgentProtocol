#!/usr/bin/env python3
"""
Validate that Python and .NET tests produce equivalent outputs.

This script compares test outputs from Python and .NET implementations
to ensure cross-platform consistency.

Usage:
    python scripts/validate-outputs.py
    python scripts/validate-outputs.py --test-id basic-serialization
    python scripts/validate-outputs.py --fail-fast
    python scripts/validate-outputs.py --verbose
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class OutputValidator:
    """Validate cross-platform test outputs"""

    def __init__(self, results_dir: Path, verbose: bool = False):
        self.results_dir = results_dir
        self.python_dir = results_dir / "python"
        self.dotnet_dir = results_dir / "dotnet"
        self.validation_dir = results_dir / "validation"
        self.verbose = verbose

        # Create validation directory
        self.validation_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(message)

    def validate_all(self, test_id: Optional[str] = None, fail_fast: bool = False) -> List[Dict]:
        """
        Validate all test outputs or specific test ID.

        Args:
            test_id: Optional specific test ID to validate
            fail_fast: If True, stop on first mismatch

        Returns:
            List of mismatch dictionaries
        """
        mismatches = []

        # Ensure directories exist
        if not self.python_dir.exists():
            print(f"⚠️  Python results directory not found: {self.python_dir}")
            return []

        if not self.dotnet_dir.exists():
            print(f"⚠️  .NET results directory not found: {self.dotnet_dir}")
            return []

        # Find all Python results
        python_files = list(self.python_dir.glob("*.json"))
        if not python_files:
            print(f"⚠️  No Python result files found in {self.python_dir}")
            return []

        self.log(f"Found {len(python_files)} Python result files")

        for python_file in python_files:
            file_test_id = python_file.stem

            # Skip if filtering by specific test ID
            if test_id and file_test_id != test_id:
                continue

            self.log(f"\nValidating: {file_test_id}")

            # Load Python result
            try:
                python_result = self._load_result(python_file)
            except Exception as e:
                mismatches.append({
                    "testId": file_test_id,
                    "issue": "python_load_error",
                    "message": f"Failed to load Python result: {e}"
                })
                if fail_fast:
                    break
                continue

            # Check for corresponding .NET result
            dotnet_file = self.dotnet_dir / f"{file_test_id}.json"
            if not dotnet_file.exists():
                self.log(f"  ⚠️  No .NET result found")
                mismatches.append({
                    "testId": file_test_id,
                    "issue": "missing_dotnet",
                    "message": f"No .NET result found for {file_test_id}"
                })
                if fail_fast:
                    break
                continue

            # Load .NET result
            try:
                dotnet_result = self._load_result(dotnet_file)
            except Exception as e:
                mismatches.append({
                    "testId": file_test_id,
                    "issue": "dotnet_load_error",
                    "message": f"Failed to load .NET result: {e}"
                })
                if fail_fast:
                    break
                continue

            # Compare outputs
            if not self._outputs_match(python_result, dotnet_result):
                self.log(f"  ✗ Outputs don't match!")
                mismatch = {
                    "testId": file_test_id,
                    "issue": "output_mismatch",
                    "python": {
                        "hash": python_result["output"].get("hash", ""),
                        "normalized": python_result["output"].get("normalized", "")[:200]
                    },
                    "dotnet": {
                        "hash": dotnet_result["output"].get("hash", ""),
                        "normalized": dotnet_result["output"].get("normalized", "")[:200]
                    }
                }
                mismatches.append(mismatch)
                if fail_fast:
                    break
            else:
                self.log(f"  ✓ Outputs match")

        return mismatches

    def _load_result(self, file_path: Path) -> Dict:
        """Load result from JSON file"""
        return json.loads(file_path.read_text())

    def _outputs_match(self, python_result: Dict, dotnet_result: Dict) -> bool:
        """
        Check if outputs match using normalized hash.

        Args:
            python_result: Python test result
            dotnet_result: .NET test result

        Returns:
            True if outputs match
        """
        py_hash = python_result.get("output", {}).get("hash", "")
        cs_hash = dotnet_result.get("output", {}).get("hash", "")

        if not py_hash or not cs_hash:
            # If no hashes, can't validate
            return False

        return py_hash == cs_hash

    def generate_report(self, mismatches: List[Dict]) -> bool:
        """
        Generate validation report.

        Args:
            mismatches: List of mismatches found

        Returns:
            True if validation passed (no mismatches)
        """
        # Count total tests
        python_count = len(list(self.python_dir.glob("*.json")))
        dotnet_count = len(list(self.dotnet_dir.glob("*.json")))

        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "totalPythonTests": python_count,
            "totalDotnetTests": dotnet_count,
            "mismatches": len(mismatches),
            "details": mismatches
        }

        # Save report
        report_file = self.validation_dir / "report.json"
        report_file.write_text(json.dumps(report, indent=2))

        # Print summary
        print("\n" + "=" * 60)
        print("Cross-Platform Validation Report")
        print("=" * 60)
        print(f"Python tests: {python_count}")
        print(f".NET tests: {dotnet_count}")
        print(f"Mismatches: {len(mismatches)}")

        if mismatches:
            print("\n⚠️  Validation FAILED")
            print("\nMismatches:")
            for mismatch in mismatches:
                print(f"\n  Test: {mismatch['testId']}")
                print(f"  Issue: {mismatch['issue']}")
                if 'message' in mismatch:
                    print(f"  Message: {mismatch['message']}")
                if 'python' in mismatch and 'dotnet' in mismatch:
                    print(f"  Python hash: {mismatch['python']['hash']}")
                    print(f"  .NET hash: {mismatch['dotnet']['hash']}")
        else:
            print("\n✅ Validation PASSED")
            print("All outputs match across Python and .NET implementations!")

        print(f"\nDetailed report saved to: {report_file}")

        return len(mismatches) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Validate cross-platform test outputs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate all outputs
  python scripts/validate-outputs.py

  # Validate specific test
  python scripts/validate-outputs.py --test-id basic-serialization

  # Fail on first mismatch
  python scripts/validate-outputs.py --fail-fast

  # Verbose output
  python scripts/validate-outputs.py --verbose
        """
    )
    parser.add_argument(
        "--test-id",
        help="Validate only specific test ID"
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Exit on first mismatch"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    results_dir = repo_root / "test-data" / "results"

    validator = OutputValidator(results_dir, verbose=args.verbose)
    mismatches = validator.validate_all(
        test_id=args.test_id,
        fail_fast=args.fail_fast
    )

    success = validator.generate_report(mismatches)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
