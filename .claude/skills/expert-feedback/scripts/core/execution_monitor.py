#!/usr/bin/env python3
"""
Execution monitor for autonomous execution phase.

Tracks progress, validates implementation health, and provides status reporting.
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class ExecutionMetrics:
    """Metrics tracked during execution."""
    iterations: int = 0
    steps_completed: int = 0
    files_modified: List[str] = field(default_factory=list)
    files_created: List[str] = field(default_factory=list)
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    deferred_questions: int = 0
    answered_questions: int = 0
    errors_encountered: int = 0
    started_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None


class ExecutionMonitor:
    """
    Monitor and track autonomous execution progress.

    Provides:
    - Progress tracking (steps, files, time)
    - Health checks (tests, syntax, security)
    - Status reporting (human-readable summaries)
    """

    def __init__(self, workspace: Path):
        """
        Initialize execution monitor.

        Args:
            workspace: Workspace directory path
        """
        self.workspace = workspace
        self.execution_dir = workspace / "execution"
        self.execution_dir.mkdir(parents=True, exist_ok=True)

        self.metrics = ExecutionMetrics()
        self.progress_log_file = self.execution_dir / "progress-log.jsonl"

        # Load existing metrics if resuming
        self._load_metrics()

    def _load_metrics(self):
        """Load existing metrics from state."""
        from state.manager import StateManager

        try:
            state_manager = StateManager(self.workspace)
            exec_state = state_manager.get_execution_state()

            self.metrics.iterations = exec_state.get("iterations", 0)
            self.metrics.steps_completed = exec_state.get("steps_completed", 0)
            self.metrics.files_modified = exec_state.get("files_modified", [])
            self.metrics.deferred_questions = exec_state.get("deferred_questions_count", 0)
            self.metrics.answered_questions = exec_state.get("answered_questions_count", 0)

            if exec_state.get("started_at"):
                self.metrics.started_at = datetime.fromisoformat(exec_state["started_at"])
            if exec_state.get("last_activity"):
                self.metrics.last_activity = datetime.fromisoformat(exec_state["last_activity"])

        except Exception as e:
            print(f"⚠️ Could not load existing metrics: {e}", file=sys.stderr)

    def start_execution(self):
        """Mark execution as started."""
        if self.metrics.started_at is None:
            self.metrics.started_at = datetime.utcnow()
            self.metrics.last_activity = datetime.utcnow()
            print(f"▶️  Execution started at {self.metrics.started_at.isoformat()}", file=sys.stderr)

    def update_progress(
        self,
        steps_completed: List[str] = None,
        files_modified: List[str] = None,
        files_created: List[str] = None
    ):
        """
        Update progress metrics.

        Args:
            steps_completed: New steps completed in this iteration
            files_modified: Files modified in this iteration
            files_created: Files created in this iteration
        """
        self.metrics.last_activity = datetime.utcnow()

        if steps_completed:
            self.metrics.steps_completed += len(steps_completed)

        if files_modified:
            for file in files_modified:
                if file not in self.metrics.files_modified:
                    self.metrics.files_modified.append(file)

        if files_created:
            self.metrics.files_created.extend(files_created)

        # Log progress
        self._log_progress_entry({
            "timestamp": datetime.utcnow().isoformat(),
            "iteration": self.metrics.iterations,
            "steps_completed": steps_completed or [],
            "files_modified": files_modified or [],
            "files_created": files_created or []
        })

    def increment_iteration(self):
        """Increment iteration counter."""
        self.metrics.iterations += 1

    def add_deferred_question(self):
        """Increment deferred questions counter."""
        self.metrics.deferred_questions += 1

    def add_answered_question(self):
        """Increment answered questions counter."""
        self.metrics.answered_questions += 1

    def record_error(self, error_msg: str):
        """
        Record an error encountered during execution.

        Args:
            error_msg: Error message
        """
        self.metrics.errors_encountered += 1
        self._log_progress_entry({
            "timestamp": datetime.utcnow().isoformat(),
            "type": "error",
            "message": error_msg
        })

    def _log_progress_entry(self, entry: Dict[str, Any]):
        """
        Append entry to progress log (JSONL format).

        Args:
            entry: Progress entry dictionary
        """
        with open(self.progress_log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def get_elapsed_time(self) -> str:
        """
        Get elapsed time since execution started.

        Returns:
            Human-readable time string (e.g., "2h 15m")
        """
        if self.metrics.started_at is None:
            return "0m"

        elapsed = datetime.utcnow() - self.metrics.started_at
        hours = int(elapsed.total_seconds() // 3600)
        minutes = int((elapsed.total_seconds() % 3600) // 60)

        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"

    def get_progress_percent(self, total_steps: int = None) -> int:
        """
        Estimate progress percentage.

        Args:
            total_steps: Total expected steps (optional)

        Returns:
            Progress percentage (0-100)
        """
        if total_steps and total_steps > 0:
            return min(100, int((self.metrics.steps_completed / total_steps) * 100))

        # Heuristic estimate if no total provided
        # Based on typical implementation patterns
        if self.metrics.steps_completed < 10:
            return 20
        elif self.metrics.steps_completed < 25:
            return 40
        elif self.metrics.steps_completed < 50:
            return 60
        elif self.metrics.steps_completed < 75:
            return 80
        else:
            return 95  # Never claim 100% until validation

    def generate_progress_report(self) -> str:
        """
        Generate human-readable progress report.

        Returns:
            Formatted progress report string
        """
        report = []
        report.append("=" * 70)
        report.append("EXECUTION PROGRESS REPORT")
        report.append("=" * 70)

        report.append(f"\n⏱️  Time Elapsed: {self.get_elapsed_time()}")
        report.append(f"🔄 Iterations: {self.metrics.iterations}")
        report.append(f"✅ Steps Completed: {self.metrics.steps_completed}")
        report.append(f"📝 Files Modified: {len(self.metrics.files_modified)}")

        if self.metrics.files_created:
            report.append(f"✨ Files Created: {len(self.metrics.files_created)}")

        if self.metrics.deferred_questions > 0:
            report.append(f"❓ Deferred Questions: {self.metrics.deferred_questions}")

        if self.metrics.answered_questions > 0:
            report.append(f"💬 Answered Questions: {self.metrics.answered_questions}")

        if self.metrics.errors_encountered > 0:
            report.append(f"❌ Errors: {self.metrics.errors_encountered}")

        # Recent files
        if self.metrics.files_modified:
            report.append(f"\n📂 Recently Modified Files:")
            for file in self.metrics.files_modified[-5:]:
                report.append(f"   - {file}")

        report.append(f"\n📊 Progress: {self.get_progress_percent()}%")
        report.append("=" * 70)

        return "\n".join(report)

    def check_implementation_health(self) -> Dict[str, Any]:
        """
        Validate implementation health.

        Checks:
        - Syntax validity
        - Tests passing (if available)
        - File count reasonable
        - No obvious security issues

        Returns:
            Health check results dictionary
        """
        health = {
            "overall_status": "healthy",
            "checks": {},
            "warnings": [],
            "errors": []
        }

        # Check 1: Reasonable file count
        file_count = len(self.metrics.files_modified)
        if file_count > 100:
            health["warnings"].append(f"High number of modified files: {file_count}")
            health["checks"]["file_count"] = "warning"
        else:
            health["checks"]["file_count"] = "ok"

        # Check 2: Syntax validation (Python files)
        syntax_valid = self._check_python_syntax()
        health["checks"]["syntax"] = "ok" if syntax_valid else "error"
        if not syntax_valid:
            health["errors"].append("Python syntax errors detected")
            health["overall_status"] = "unhealthy"

        # Check 3: Run tests if available
        test_results = self._run_tests_if_available()
        if test_results:
            health["checks"]["tests"] = test_results["status"]
            health["tests"] = test_results

            if test_results["status"] == "failed":
                health["warnings"].append(f"{test_results['failed']} test(s) failing")
                if test_results["failed"] > 5:
                    health["overall_status"] = "degraded"

        # Check 4: Look for obvious security issues
        security_check = self._basic_security_scan()
        health["checks"]["security"] = security_check["status"]
        if security_check["issues"]:
            health["warnings"].extend(security_check["issues"])

        return health

    def _check_python_syntax(self) -> bool:
        """
        Check syntax of Python files.

        Returns:
            True if all Python files have valid syntax
        """
        python_files = [
            f for f in self.metrics.files_modified
            if f.endswith('.py')
        ]

        if not python_files:
            return True  # No Python files to check

        all_valid = True

        for file_path in python_files:
            full_path = self.workspace / file_path
            if not full_path.exists():
                continue

            try:
                subprocess.run(
                    ["python3", "-m", "py_compile", str(full_path)],
                    check=True,
                    capture_output=True,
                    timeout=10
                )
            except subprocess.CalledProcessError:
                print(f"❌ Syntax error in {file_path}", file=sys.stderr)
                all_valid = False
            except subprocess.TimeoutExpired:
                print(f"⏱️ Syntax check timeout for {file_path}", file=sys.stderr)
            except Exception as e:
                print(f"⚠️ Could not check syntax for {file_path}: {e}", file=sys.stderr)

        return all_valid

    def _run_tests_if_available(self) -> Optional[Dict[str, Any]]:
        """
        Run test suite if tests are available.

        Returns:
            Test results dictionary or None if no tests
        """
        # Look for common test configurations
        test_commands = [
            (self.workspace / "pytest.ini", ["pytest", "--tb=short", "-q"]),
            (self.workspace / "package.json", ["npm", "test"]),
            (self.workspace / "Makefile", ["make", "test"])
        ]

        for config_file, command in test_commands:
            if config_file.exists():
                try:
                    result = subprocess.run(
                        command,
                        cwd=self.workspace,
                        capture_output=True,
                        timeout=120,  # 2 minute timeout
                        text=True
                    )

                    # Parse output (simplified)
                    output = result.stdout + result.stderr

                    return {
                        "status": "passed" if result.returncode == 0 else "failed",
                        "exit_code": result.returncode,
                        "output_summary": output[:500],
                        "passed": "extracted_from_output",  # TODO: Parse actual counts
                        "failed": "extracted_from_output"
                    }

                except subprocess.TimeoutExpired:
                    return {
                        "status": "timeout",
                        "message": "Tests took too long to run"
                    }
                except Exception as e:
                    print(f"⚠️ Could not run tests: {e}", file=sys.stderr)
                    return None

        return None  # No test suite found

    def _basic_security_scan(self) -> Dict[str, Any]:
        """
        Basic security checks on modified files.

        Returns:
            Security scan results
        """
        issues = []

        # Check for obvious patterns
        dangerous_patterns = [
            ("eval(", "Potentially dangerous eval() usage"),
            ("exec(", "Potentially dangerous exec() usage"),
            ("pickle.loads", "Unsafe pickle deserialization"),
            ("yaml.load(", "Unsafe YAML loading (use safe_load)"),
            ("subprocess.call", "Potential command injection risk"),
            ("os.system", "Potential command injection risk"),
        ]

        for file_path in self.metrics.files_modified:
            full_path = self.workspace / file_path
            if not full_path.exists() or not full_path.is_file():
                continue

            try:
                content = full_path.read_text()

                for pattern, warning in dangerous_patterns:
                    if pattern in content:
                        issues.append(f"{file_path}: {warning}")

            except Exception as e:
                pass  # Skip files we can't read

        return {
            "status": "warning" if issues else "ok",
            "issues": issues
        }


if __name__ == "__main__":
    # Test the monitor
    import tempfile

    print("Execution Monitor Test\n" + "="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)

        # Create monitor
        monitor = ExecutionMonitor(workspace)
        monitor.start_execution()

        # Simulate progress
        print("\n1. Simulating progress updates...")
        monitor.increment_iteration()
        monitor.update_progress(
            steps_completed=["Created API endpoint", "Added validation"],
            files_modified=["src/api.py", "tests/test_api.py"]
        )

        monitor.increment_iteration()
        monitor.update_progress(
            steps_completed=["Added error handling", "Updated docs"],
            files_modified=["src/api.py", "README.md"]
        )

        monitor.add_deferred_question()
        monitor.add_deferred_question()

        # Generate report
        print("\n2. Progress Report:")
        print(monitor.generate_progress_report())

        # Check health
        print("\n3. Health Check:")
        health = monitor.check_implementation_health()
        print(f"   Overall Status: {health['overall_status']}")
        print(f"   Checks: {health['checks']}")
        if health['warnings']:
            print(f"   Warnings: {len(health['warnings'])}")

        print("\n✅ Test complete!")
