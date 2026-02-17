#!/usr/bin/env python3
"""
Test coverage agent for autonomous test generation.

This agent runs after autonomous execution completes to ensure 90%+ test coverage.
It analyzes current coverage, identifies gaps, and writes tests iteratively until
the target coverage is met.
"""

import asyncio
import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.conversational_session import ConversationalSession
from state.manager import StateManager
from config import get_config


async def run_test_coverage_phase(
    workspace: Path,
    target_coverage: float = 90.0,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Entry point for test coverage phase.

    Args:
        workspace: Workspace directory path
        target_coverage: Target coverage percentage (default: 90%)
        correlation_id: Optional correlation ID for logging

    Returns:
        Coverage result dictionary
    """
    config = get_config()

    if not config.enable_test_coverage_agent:
        return {
            "status": "skipped",
            "message": "Test coverage agent disabled in config"
        }

    print(f"\n{'='*70}", file=sys.stderr)
    print("TEST COVERAGE PHASE", file=sys.stderr)
    print(f"{'='*70}\n", file=sys.stderr)

    # Initialize state
    state_manager = StateManager(workspace, correlation_id=correlation_id)
    state_manager.initialize_test_coverage_state()

    # Analyze initial coverage
    print(f"📊 Analyzing current test coverage...", file=sys.stderr)
    initial_coverage = analyze_current_coverage(workspace)

    if initial_coverage.get("status") == "error":
        return {
            "status": "error",
            "error": f"Failed to analyze coverage: {initial_coverage.get('error')}"
        }

    current = initial_coverage.get("overall_coverage", 0.0)
    print(f"   Current coverage: {current}%", file=sys.stderr)
    print(f"   Target coverage: {target_coverage}%", file=sys.stderr)

    # Check if already at target
    if current >= target_coverage:
        print(f"\n✅ Coverage target already met!", file=sys.stderr)
        state_manager.update_test_coverage_progress(
            status="completed",
            current_coverage=current,
            iterations=0,
            tests_written=0
        )
        return {
            "status": "complete",
            "final_coverage": current,
            "target_coverage": target_coverage,
            "iterations": 0,
            "tests_written": 0,
            "unit_coverage": initial_coverage.get("unit_test_coverage"),
            "integration_coverage": initial_coverage.get("integration_test_coverage")
        }

    # Save initial coverage report
    coverage_dir = workspace / "test-coverage"
    coverage_dir.mkdir(parents=True, exist_ok=True)
    initial_report_file = coverage_dir / "initial-coverage-report.json"
    initial_report_file.write_text(json.dumps(initial_coverage, indent=2))
    print(f"   Saved initial report: {initial_report_file.name}", file=sys.stderr)

    # Create or resume test agent session
    try:
        session = ConversationalSession.load(
            agent_id="test-agent",
            workspace=workspace
        )
        print(f"📝 Resuming test agent session (turn {session.turn_count + 1})...", file=sys.stderr)
    except ValueError:
        session = ConversationalSession(
            agent_type="test-agent",
            agent_id="test-agent",
            workspace=workspace
        )
        print("📝 Created new test agent session", file=sys.stderr)

    # Update state
    state_manager.update_test_coverage_progress(
        status="running",
        initial_coverage=current,
        current_coverage=current,
        target_coverage=target_coverage,
        session_id=session.session_id
    )

    # Run test generation loop
    result = await generate_tests_loop(
        session=session,
        workspace=workspace,
        initial_coverage=initial_coverage,
        target_coverage=target_coverage,
        state_manager=state_manager,
        max_iterations=config.test_coverage_max_iterations,
        correlation_id=correlation_id
    )

    # Update final state
    final_status = "completed" if result["status"] == "complete" else "failed"
    state_manager.update_test_coverage_progress(
        status=final_status,
        current_coverage=result.get("final_coverage", current),
        iterations=result.get("iterations", 0),
        tests_written=result.get("tests_written", 0)
    )

    return result


async def generate_tests_loop(
    session: ConversationalSession,
    workspace: Path,
    initial_coverage: Dict[str, Any],
    target_coverage: float,
    state_manager: StateManager,
    max_iterations: int = 20,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Continuously generates tests until coverage target met.

    Args:
        session: Conversational session for test agent
        workspace: Workspace path
        initial_coverage: Initial coverage analysis
        target_coverage: Target coverage percentage
        state_manager: State manager
        max_iterations: Maximum test generation iterations
        correlation_id: Optional correlation ID

    Returns:
        Coverage result dictionary
    """
    iteration = 0
    tests_written_total = 0

    while iteration < max_iterations:
        iteration += 1

        print(f"\n🧪 Test Generation Iteration {iteration}/{max_iterations}", file=sys.stderr)

        # Analyze current coverage
        coverage = analyze_current_coverage(workspace)

        if coverage.get("status") == "error":
            print(f"❌ Coverage analysis failed: {coverage.get('error')}", file=sys.stderr)
            return {
                "status": "error",
                "error": f"Coverage analysis failed: {coverage.get('error')}",
                "iterations": iteration,
                "final_coverage": 0.0
            }

        current = coverage.get("overall_coverage", 0.0)
        print(f"   Current coverage: {current}%", file=sys.stderr)

        # Check if target met
        if current >= target_coverage:
            print(f"\n✅ Coverage target met: {current}% >= {target_coverage}%", file=sys.stderr)

            # Save final coverage report
            coverage_dir = workspace / "test-coverage"
            final_report_file = coverage_dir / "final-coverage-report.json"
            final_report_file.write_text(json.dumps(coverage, indent=2))

            return {
                "status": "complete",
                "final_coverage": current,
                "target_coverage": target_coverage,
                "iterations": iteration,
                "tests_written": tests_written_total,
                "unit_coverage": coverage.get("unit_test_coverage"),
                "integration_coverage": coverage.get("integration_test_coverage")
            }

        # Determine prompt template
        if iteration == 1:
            prompt_template = "01-analyze-coverage.jinja2"
            context = {
                "coverage_report": coverage,
                "target_coverage": target_coverage,
                "initial_coverage": initial_coverage.get("overall_coverage", 0.0)
            }
            print(f"   🔍 Analyzing coverage gaps...", file=sys.stderr)
        else:
            # Prioritize coverage gaps
            gaps = prioritize_coverage_gaps(coverage.get("coverage_gaps", []))
            prompt_template = "02-write-tests.jinja2"
            context = {
                "coverage_gaps": gaps[:5],  # Focus on top 5 gaps
                "existing_patterns": coverage.get("existing_test_patterns", {}),
                "current_coverage": current,
                "target_coverage": target_coverage,
                "remaining": target_coverage - current,
                "iteration": iteration
            }
            print(f"   ✍️  Writing tests for {len(gaps[:5])} gap(s)...", file=sys.stderr)

        # Send turn to agent
        try:
            response = await session.send_turn(
                prompt_template=prompt_template,
                context=context,
                timeout=600  # 10 minutes per turn
            )
        except Exception as e:
            print(f"\n❌ Agent call failed: {e}", file=sys.stderr)
            return {
                "status": "error",
                "error": f"Agent call failed: {e}",
                "iterations": iteration,
                "final_coverage": current
            }

        # Parse response
        try:
            agent_output = json.loads(response["content"])
        except json.JSONDecodeError as e:
            print(f"\n⚠️ Could not parse agent response as JSON: {e}", file=sys.stderr)
            print(f"Response content preview: {response['content'][:200]}...", file=sys.stderr)
            agent_output = {
                "status": "in_progress",
                "tests_written": []
            }

        # Track tests written
        tests_written = agent_output.get("tests_written", [])
        if tests_written:
            tests_written_total += len(tests_written)
            print(f"   📝 {len(tests_written)} test suite(s) written", file=sys.stderr)

        # Run tests to validate
        print(f"   🧪 Running tests...", file=sys.stderr)
        test_result = run_tests(workspace)
        if not test_result.get("all_passed", True):
            print(f"   ⚠️  Some tests failing", file=sys.stderr)
            # Continue - agent will see failures in next iteration

        # Update state
        state_manager.update_test_coverage_progress(
            status="running",
            current_coverage=current,
            iterations=iteration,
            tests_written=tests_written_total
        )

        # Check status
        status = agent_output.get("status", "in_progress")
        if status == "done":
            # Run final validation
            print(f"\n🔍 Running final validation...", file=sys.stderr)
            validation_coverage = analyze_current_coverage(workspace)
            final_coverage = validation_coverage.get("overall_coverage", 0.0)

            if final_coverage >= target_coverage:
                print(f"✅ Validation passed: {final_coverage}% >= {target_coverage}%", file=sys.stderr)
                return {
                    "status": "complete",
                    "final_coverage": final_coverage,
                    "target_coverage": target_coverage,
                    "iterations": iteration,
                    "tests_written": tests_written_total,
                    "unit_coverage": validation_coverage.get("unit_test_coverage"),
                    "integration_coverage": validation_coverage.get("integration_test_coverage")
                }
            else:
                print(f"⚠️  Validation failed: {final_coverage}% < {target_coverage}%", file=sys.stderr)
                # Continue for one more iteration

        print(f"   Progress: {current}% → {target_coverage}% (gap: {target_coverage - current:.1f}%)", file=sys.stderr)

    # Max iterations reached
    print(f"\n⚠️ Max iterations reached ({max_iterations})", file=sys.stderr)

    # Final coverage check
    final_coverage_result = analyze_current_coverage(workspace)
    final_coverage = final_coverage_result.get("overall_coverage", 0.0)

    return {
        "status": "incomplete",
        "reason": "Maximum iterations reached",
        "final_coverage": final_coverage,
        "target_coverage": target_coverage,
        "iterations": iteration,
        "tests_written": tests_written_total,
        "unit_coverage": final_coverage_result.get("unit_test_coverage"),
        "integration_coverage": final_coverage_result.get("integration_test_coverage")
    }


def analyze_current_coverage(workspace: Path) -> Dict[str, Any]:
    """
    Runs coverage tools and identifies gaps.

    Returns:
        {
            "overall_coverage": 67.5,
            "unit_test_coverage": 72.0,
            "integration_test_coverage": 45.0,
            "coverage_gaps": [...],
            "existing_test_patterns": {...},
            "status": "success" | "error"
        }
    """
    config = get_config()

    # Detect project type and run appropriate coverage tool
    coverage_result = {
        "overall_coverage": 0.0,
        "unit_test_coverage": None,
        "integration_test_coverage": None,
        "coverage_gaps": [],
        "existing_test_patterns": {},
        "status": "success"
    }

    # Try Python coverage (pytest-cov)
    if (workspace / "pytest.ini").exists() or (workspace / "pyproject.toml").exists():
        print(f"   Detected Python project", file=sys.stderr)
        python_coverage = run_python_coverage(workspace)
        if python_coverage.get("status") == "success":
            coverage_result["overall_coverage"] = python_coverage.get("coverage", 0.0)
            coverage_result["coverage_gaps"] = python_coverage.get("gaps", [])
            coverage_result["existing_test_patterns"]["framework"] = "pytest"
            return coverage_result

    # Try TypeScript/JavaScript coverage (jest)
    if (workspace / "jest.config.js").exists() or (workspace / "jest.config.ts").exists():
        print(f"   Detected Jest project", file=sys.stderr)
        jest_coverage = run_jest_coverage(workspace)
        if jest_coverage.get("status") == "success":
            coverage_result["overall_coverage"] = jest_coverage.get("coverage", 0.0)
            coverage_result["coverage_gaps"] = jest_coverage.get("gaps", [])
            coverage_result["existing_test_patterns"]["framework"] = "jest"
            return coverage_result

    # Try Node.js coverage (nyc)
    if (workspace / "package.json").exists():
        print(f"   Detected Node.js project", file=sys.stderr)
        nyc_coverage = run_nyc_coverage(workspace)
        if nyc_coverage.get("status") == "success":
            coverage_result["overall_coverage"] = nyc_coverage.get("coverage", 0.0)
            coverage_result["coverage_gaps"] = nyc_coverage.get("gaps", [])
            coverage_result["existing_test_patterns"]["framework"] = "nyc"
            return coverage_result

    # No coverage tool found
    print(f"   ⚠️  No coverage tool configured", file=sys.stderr)
    return {
        "status": "error",
        "error": "No coverage tool found (tried pytest-cov, jest, nyc)"
    }


def run_python_coverage(workspace: Path) -> Dict[str, Any]:
    """Run pytest with coverage."""
    try:
        result = subprocess.run(
            ["pytest", "--cov", "--cov-report", "json", "--cov-report", "term"],
            cwd=workspace,
            capture_output=True,
            timeout=300,  # 5 minutes
            text=True
        )

        # Load coverage.json if it exists
        coverage_file = workspace / "coverage.json"
        if coverage_file.exists():
            coverage_data = json.loads(coverage_file.read_text())
            overall = coverage_data.get("totals", {}).get("percent_covered", 0.0)

            # Extract gaps
            gaps = []
            for file_path, file_data in coverage_data.get("files", {}).items():
                missing_lines = file_data.get("missing_lines", [])
                if missing_lines:
                    gaps.append({
                        "file": file_path,
                        "uncovered_lines": missing_lines,
                        "coverage": file_data.get("summary", {}).get("percent_covered", 0.0),
                        "priority": "high" if file_data.get("summary", {}).get("percent_covered", 0.0) < 50 else "medium"
                    })

            return {
                "status": "success",
                "coverage": overall,
                "gaps": gaps
            }

        # Fallback: parse terminal output
        output = result.stdout + result.stderr
        # Look for "TOTAL" line with coverage percentage
        for line in output.split("\n"):
            if "TOTAL" in line:
                parts = line.split()
                for part in parts:
                    if "%" in part:
                        try:
                            coverage = float(part.replace("%", ""))
                            return {"status": "success", "coverage": coverage, "gaps": []}
                        except ValueError:
                            pass

        return {"status": "error", "error": "Could not parse coverage output"}

    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Coverage analysis timed out"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_jest_coverage(workspace: Path) -> Dict[str, Any]:
    """Run jest with coverage."""
    try:
        result = subprocess.run(
            ["npm", "test", "--", "--coverage", "--coverageReporters=json"],
            cwd=workspace,
            capture_output=True,
            timeout=300,
            text=True
        )

        # Load coverage/coverage-final.json
        coverage_file = workspace / "coverage" / "coverage-final.json"
        if coverage_file.exists():
            coverage_data = json.loads(coverage_file.read_text())
            # Parse Jest coverage format
            # TODO: Implement Jest coverage parsing
            return {"status": "success", "coverage": 0.0, "gaps": []}

        return {"status": "error", "error": "Jest coverage file not found"}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_nyc_coverage(workspace: Path) -> Dict[str, Any]:
    """Run nyc with coverage."""
    try:
        result = subprocess.run(
            ["nyc", "npm", "test"],
            cwd=workspace,
            capture_output=True,
            timeout=300,
            text=True
        )

        # Parse nyc output
        # TODO: Implement nyc coverage parsing
        return {"status": "success", "coverage": 0.0, "gaps": []}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def prioritize_coverage_gaps(gaps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prioritize coverage gaps by importance.

    Args:
        gaps: List of coverage gap dictionaries

    Returns:
        Sorted list of gaps (highest priority first)
    """
    def priority_score(gap: Dict[str, Any]) -> int:
        score = 0

        # High priority files
        file = gap.get("file", "")
        if "src/" in file or "lib/" in file:
            score += 10
        if "api" in file or "core" in file:
            score += 5

        # Priority field
        priority = gap.get("priority", "medium")
        if priority == "high":
            score += 20
        elif priority == "medium":
            score += 10

        # Coverage percentage (lower is higher priority)
        coverage = gap.get("coverage", 100.0)
        score += int((100 - coverage) / 10)

        return score

    return sorted(gaps, key=priority_score, reverse=True)


def run_tests(workspace: Path) -> Dict[str, Any]:
    """
    Run test suite to validate tests pass.

    Returns:
        {
            "all_passed": true/false,
            "tests_run": 10,
            "tests_passed": 10,
            "tests_failed": 0
        }
    """
    # Look for test commands
    test_commands = [
        (workspace / "pytest.ini", ["pytest", "-q"]),
        (workspace / "package.json", ["npm", "test"]),
        (workspace / "Makefile", ["make", "test"])
    ]

    for config_file, command in test_commands:
        if config_file.exists():
            try:
                result = subprocess.run(
                    command,
                    cwd=workspace,
                    capture_output=True,
                    timeout=180,  # 3 minutes
                    text=True
                )

                return {
                    "all_passed": result.returncode == 0,
                    "exit_code": result.returncode,
                    "output": result.stdout + result.stderr
                }

            except subprocess.TimeoutExpired:
                return {
                    "all_passed": False,
                    "error": "Tests timed out"
                }
            except Exception as e:
                return {
                    "all_passed": False,
                    "error": str(e)
                }

    # No test command found
    return {
        "all_passed": True,  # Assume passing if no tests
        "message": "No test command found"
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run test coverage phase")
    parser.add_argument("--workspace", required=True, type=Path, help="Workspace path")
    parser.add_argument("--target", type=float, default=90.0, help="Target coverage percentage")
    parser.add_argument("--correlation-id", help="Optional correlation ID for logging")

    args = parser.parse_args()

    # Run coverage phase
    result = asyncio.run(run_test_coverage_phase(
        workspace=args.workspace,
        target_coverage=args.target,
        correlation_id=args.correlation_id
    ))

    # Output result as JSON
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result.get("status") in ["complete", "skipped"] else 1)
