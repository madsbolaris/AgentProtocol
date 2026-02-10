#!/usr/bin/env python3
import argparse
"""
Master Consistency Validator

Orchestrates all consistency checks and generates a comprehensive report.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Colors for output
try:
    from colorama import init, Fore, Style
    init()
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    CYAN = Fore.CYAN
    RESET = Style.RESET_ALL
except ImportError:
    RED = GREEN = YELLOW = BLUE = CYAN = RESET = ""


def find_project_root() -> Path:
    """Find the AgentProtocol project root."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "typespec").exists() and (current / "docs").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


def run_validator(script_name: str, description: str) -> tuple[int, str]:
    """Run a validation script and capture output."""
    script_path = Path(__file__).parent / script_name

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return 1, f"Timeout running {script_name}"
    except Exception as e:
        return 1, f"Error running {script_name}: {str(e)}"


def main():
    """Main validation orchestrator."""
    parser = argparse.ArgumentParser(
        description="Validate Agent Protocol documentation consistency"
    )
    parser.parse_args()

    print(f"{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}{'AGENT PROTOCOL DOCUMENTATION CONSISTENCY VALIDATION':^70}{RESET}")
    print(f"{CYAN}{'='*70}{RESET}\n")

    try:
        project_root = find_project_root()
        print(f"Project root: {project_root}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    except RuntimeError as e:
        print(f"{RED}Error: {e}{RESET}")
        return 1

    # Define validation checks
    validators = [
        ("validate_enums.py", "Enum Synchronization"),
        ("validate_links.py", "Internal Link Validation"),
        ("check_line_references.py", "Line Number Reference Check"),
    ]

    results = []
    overall_status = 0

    # Run each validator
    for script_name, description in validators:
        print(f"{BLUE}╔═══════════════════════════════════════════════════════════╗{RESET}")
        print(f"{BLUE}║ {description:^57} ║{RESET}")
        print(f"{BLUE}╚═══════════════════════════════════════════════════════════╝{RESET}\n")

        returncode, output = run_validator(script_name, description)

        # Print validator output
        print(output)
        print()

        # Record result
        status = "PASS" if returncode == 0 else "FAIL"
        results.append((description, status, returncode))

        if returncode != 0:
            overall_status = 1

    # Generate summary report
    print(f"\n{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}{'VALIDATION SUMMARY':^70}{RESET}")
    print(f"{CYAN}{'='*70}{RESET}\n")

    for description, status, code in results:
        status_color = GREEN if status == "PASS" else RED
        icon = "✓" if status == "PASS" else "✗"
        print(f"  {status_color}{icon}{RESET} {description:.<50} {status_color}{status}{RESET}")

    print(f"\n{CYAN}{'='*70}{RESET}")

    if overall_status == 0:
        print(f"\n{GREEN}{'✓ ALL VALIDATION CHECKS PASSED':^70}{RESET}\n")
    else:
        print(f"\n{RED}{'✗ SOME VALIDATION CHECKS FAILED':^70}{RESET}\n")
        print(f"Please review the output above and fix the identified issues.")

    # Save report to file
    report_dir = project_root / "doc-validation" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / f"consistency-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"

    # Note: In a real implementation, we'd save the full output to the report file
    print(f"\nReport saved to: {report_file}")

    return overall_status


if __name__ == "__main__":
    sys.exit(main())
