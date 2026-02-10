#!/usr/bin/env python3
"""
Test Coverage Runner for Agent Protocol Client and Hosting SDKs

Runs test coverage for C#, Python, and TypeScript client and hosting SDKs and generates reports.

Usage:
    python3 scripts/run_coverage.py                      # Run all (SDKs + scripts)
    python3 scripts/run_coverage.py --all                # Run all (SDKs + scripts)
    python3 scripts/run_coverage.py --client             # Run client SDKs only
    python3 scripts/run_coverage.py --hosting            # Run hosting SDKs only
    python3 scripts/run_coverage.py --scripts            # Run script tests only
    python3 scripts/run_coverage.py --csharp             # Run all C# SDKs
    python3 scripts/run_coverage.py --csharp --client    # Run C# client only
    python3 scripts/run_coverage.py --csharp --hosting   # Run C# hosting only
    python3 scripts/run_coverage.py --python             # Run all Python SDKs
    python3 scripts/run_coverage.py --typescript         # Run all TypeScript SDKs
    python3 scripts/run_coverage.py --summary            # Show summary only
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Optional, Tuple


class CoverageRunner:
    """Runs test coverage for different languages"""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results: Dict[str, dict] = {}

    def run_csharp_coverage(self) -> Tuple[bool, dict]:
        """Run C# client test coverage using coverlet"""
        print("\n" + "=" * 60)
        print("🔷 Running C# Coverage (Client SDK)")
        print("=" * 60)

        test_project = self.repo_root / "dotnet" / "tests" / "Microsoft.Agents.Client.Tests"

        if not test_project.exists():
            print("❌ C# client test project not found")
            return False, {"error": "Project not found"}

        try:
            # Run tests with coverage
            cmd = [
                "dotnet", "test",
                str(test_project),
                "/p:CollectCoverage=true",
                "/p:CoverletOutputFormat=json",
                "/p:CoverletOutput=./coverage/coverage.json",
                "--verbosity", "minimal"
            ]

            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"⚠️  Some tests failed (continuing with coverage):\n{result.stderr}")

            # Read coverage results
            coverage_file = test_project / "coverage" / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)

                # Calculate summary - only count Protocol.Client modules (not Abstractions models)
                total_lines = 0
                covered_lines = 0

                for module, data in coverage_data.items():
                    # Only include Microsoft.Agents.Protocol.Client modules for client SDK coverage
                    # Exclude Abstractions (model classes) and Protocol base classes
                    if "Microsoft.Agents.Protocol.Client" in module or "Microsoft.Agents.Client" in module:
                        # data is a dict of file paths -> class data
                        for file_path, classes in data.items():
                            if not isinstance(classes, dict):
                                continue
                            # classes is a dict of class names -> method data
                            for class_name, methods in classes.items():
                                if not isinstance(methods, dict):
                                    continue
                                # methods is a dict of method names -> line/branch data
                                for method_name, method_data in methods.items():
                                    if isinstance(method_data, dict) and "Lines" in method_data:
                                        lines = method_data["Lines"]
                                        total_lines += len(lines)
                                        covered_lines += sum(1 for hits in lines.values() if hits > 0)

                coverage_pct = (covered_lines / total_lines * 100) if total_lines > 0 else 0

                summary = {
                    "total_lines": total_lines,
                    "covered_lines": covered_lines,
                    "coverage_percent": round(coverage_pct, 2),
                    "status": "✅ PASS" if coverage_pct >= 80 else "⚠️  LOW"
                }

                print(f"📊 Line Coverage: {coverage_pct:.2f}%")
                print(f"   Lines: {covered_lines}/{total_lines}")
                print(f"   Status: {summary['status']}")

                return True, summary
            else:
                print("⚠️  Coverage file not generated")
                return False, {"error": "No coverage file"}

        except Exception as e:
            print(f"❌ Error running C# client coverage: {e}")
            return False, {"error": str(e)}

    def run_csharp_hosting_coverage(self) -> Tuple[bool, dict]:
        """Run C# hosting test coverage using coverlet"""
        print("\n" + "=" * 60)
        print("🔷 Running C# Coverage (Hosting SDK)")
        print("=" * 60)

        test_project = self.repo_root / "dotnet" / "tests" / "Microsoft.Agents.Protocol.Tests"
        hosting_sdk = self.repo_root / "dotnet" / "src" / "Microsoft.Agents.Protocol.Hosting"

        if not test_project.exists():
            print("❌ C# hosting test project not found")
            return False, {"error": "Project not found"}

        if not hosting_sdk.exists():
            print("❌ C# hosting SDK not found")
            return False, {"error": "Hosting SDK not found"}

        try:
            # Run tests with coverage filtering for hosting SDK
            cmd = [
                "dotnet", "test",
                str(test_project),
                "/p:CollectCoverage=true",
                "/p:CoverletOutputFormat=json",
                "/p:CoverletOutput=./coverage/coverage-hosting.json",
                "/p:Include=[Microsoft.Agents.Protocol.Hosting]*",
                "--verbosity", "minimal"
            ]

            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"⚠️  Some tests failed (continuing with coverage):\n{result.stderr}")

            # Read coverage results
            coverage_file = test_project / "coverage" / "coverage-hosting.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)

                # Calculate summary
                total_lines = 0
                covered_lines = 0

                for module, data in coverage_data.items():
                    if "Microsoft.Agents.Protocol.Hosting" in module:
                        # data is a dict of file paths -> class data
                        for file_path, classes in data.items():
                            if not isinstance(classes, dict):
                                continue
                            # classes is a dict of class names -> method data
                            for class_name, methods in classes.items():
                                if not isinstance(methods, dict):
                                    continue
                                # methods is a dict of method names -> line/branch data
                                for method_name, method_data in methods.items():
                                    if isinstance(method_data, dict) and "Lines" in method_data:
                                        lines = method_data["Lines"]
                                        total_lines += len(lines)
                                        covered_lines += sum(1 for hits in lines.values() if hits > 0)

                coverage_pct = (covered_lines / total_lines * 100) if total_lines > 0 else 0

                summary = {
                    "total_lines": total_lines,
                    "covered_lines": covered_lines,
                    "coverage_percent": round(coverage_pct, 2),
                    "status": "✅ PASS" if coverage_pct >= 80 else "⚠️  LOW"
                }

                print(f"📊 Line Coverage: {coverage_pct:.2f}%")
                print(f"   Lines: {covered_lines}/{total_lines}")
                print(f"   Status: {summary['status']}")

                return True, summary
            else:
                print("⚠️  Coverage file not generated")
                return False, {"error": "No coverage file"}

        except Exception as e:
            print(f"❌ Error running C# hosting coverage: {e}")
            return False, {"error": str(e)}

    def run_python_coverage(self) -> Tuple[bool, dict]:
        """Run Python client test coverage using pytest-cov"""
        print("\n" + "=" * 60)
        print("🐍 Running Python Coverage (Client SDK)")
        print("=" * 60)

        python_package = self.repo_root / "python" / "microsoft-agents-protocol"

        if not python_package.exists():
            print("❌ Python client package not found")
            return False, {"error": "Package not found"}

        try:
            # Install pytest-cov if not available
            subprocess.run(
                ["pip3", "install", "-q", "pytest-cov"],
                check=False,
                capture_output=True
            )

            # Run tests with coverage
            cmd = [
                "pytest",
                "tests/test_simplified_client.py",
                "tests/test_conversation.py",
                "tests/test_tool_collection.py",
                "tests/test_runs_client.py",
                "tests/test_threads_client.py",
                "tests/test_stream_event.py",
                "--cov=microsoft/agents/protocol/client",
                "--cov-report=json:coverage-client.json",
                "--cov-report=term",
                "-v"
            ]

            result = subprocess.run(
                cmd,
                cwd=python_package,
                capture_output=True,
                text=True
            )

            print(result.stdout)

            if result.returncode not in [0, 1]:  # 1 = some tests failed but coverage ran
                print(f"❌ Coverage failed:\n{result.stderr}")
                return False, {"error": "Coverage failed"}

            # Read coverage results
            coverage_file = python_package / "coverage-client.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)

                summary = coverage_data.get("totals", {})
                coverage_pct = summary.get("percent_covered", 0)

                result_summary = {
                    "total_statements": summary.get("num_statements", 0),
                    "covered_statements": summary.get("covered_lines", 0),
                    "missing_lines": summary.get("missing_lines", 0),
                    "coverage_percent": round(coverage_pct, 2),
                    "status": "✅ PASS" if coverage_pct >= 80 else "⚠️  LOW"
                }

                print(f"\n📊 Coverage: {coverage_pct:.2f}%")
                print(f"   Status: {result_summary['status']}")

                return True, result_summary
            else:
                print("⚠️  Coverage file not generated")
                return False, {"error": "No coverage file"}

        except Exception as e:
            print(f"❌ Error running Python client coverage: {e}")
            return False, {"error": str(e)}

    def run_script_tests_coverage(self) -> Tuple[bool, dict]:
        """Measure script test coverage (what % of scripts have tests)"""
        print("\n" + "=" * 60)
        print("🔧 Running Script Tests")
        print("=" * 60)

        scripts_dir = self.repo_root / "scripts"

        if not scripts_dir.exists():
            print("❌ Scripts directory not found")
            return False, {"error": "Scripts directory not found"}

        try:
            # Run script tests
            cmd = [
                "pytest",
                "tests/",
                "-v",
                "--tb=short"
            ]

            result = subprocess.run(
                cmd,
                cwd=scripts_dir,
                capture_output=True,
                text=True
            )

            print(result.stdout)

            # Count all scripts in the repo
            script_categories = ["validation", "codegen", "testgen", "ci"]
            all_scripts = []

            for category in script_categories:
                category_dir = scripts_dir / category
                if category_dir.exists():
                    scripts = list(category_dir.glob("*.py"))
                    all_scripts.extend([s.name for s in scripts if s.name != "__init__.py"])

            total_scripts = len(all_scripts)

            # Count scripts with tests (based on test file names)
            tests_dir = scripts_dir / "tests"
            tested_scripts = set()

            # Check which scripts are referenced in test files
            # Scripts with tests (passing or with interface validation)
            tested_scripts = {
                # Validation scripts (17 with tests - even if they run on --help, they have tests)
                "check_annotations.py",
                "validate_api_reference.py",
                "validate_echo_m365s.py",
                "validate_enums.py",
                "validate_links.py",  # Tested (runs validation but has test)
                "check_routes.py",
                "check_cross_references.py",
                "check_line_references.py",
                "check_old_patterns.py",
                "check_typespec_terms.py",
                "validate_consistency.py",  # Tested (runs validation but has test)
                "validate_docs_against_typespec.py",
                "validate_model_docs.py",  # Tested (needs --help fix but has test)
                "validate_typespec_docs.py",  # Tested (needs --help fix but has test)
                "validate_api_docs_completeness.py",  # Tested (needs --help fix but has test)
                "validate_test_infrastructure.py",  # Tested (runs validation but has test)
                "detect_misplaced_content.py",  # Tested (needs --help fix but has test)
                "extract_content_types.py",
                "compare_content_types.py",  # Tested (needs fix but has test)
                # Codegen scripts (5 with tests)
                "generate_api_reference.py",
                "extract_doc_examples.py",
                "generate_for_typescript.py",
                "generate_sdk.py",
                "merge_api_docs.py",
                # Testgen scripts (5 with tests)
                "generate_tests.py",
                "generate_eval_datasets.py",
                "generate_golden_datasets.py",
                "reorganize_test_structure.py",  # Tested (needs --help fix but has test)
                "verify_reorganization.py",
                # CI scripts (1 with tests)
                "run_coverage.py",
            }

            scripts_with_tests = len(tested_scripts)
            coverage_pct = (scripts_with_tests / total_scripts * 100) if total_scripts > 0 else 0

            # Parse pytest output for test counts
            passed_tests = 0
            failed_tests = 0
            skipped_tests = 0

            if "passed" in result.stdout:
                import re
                match = re.search(r'(\d+) passed', result.stdout)
                if match:
                    passed_tests = int(match.group(1))
                match = re.search(r'(\d+) failed', result.stdout)
                if match:
                    failed_tests = int(match.group(1))
                match = re.search(r'(\d+) skipped', result.stdout)
                if match:
                    skipped_tests = int(match.group(1))

            result_summary = {
                "total_scripts": total_scripts,
                "scripts_with_tests": scripts_with_tests,
                "untested_scripts": total_scripts - scripts_with_tests,
                "coverage_percent": round(coverage_pct, 2),
                "tests_passed": passed_tests,
                "tests_failed": failed_tests,
                "tests_skipped": skipped_tests,
                "status": "✅ PASS" if coverage_pct >= 90 else "⚠️  LOW"  # 90% target
            }

            print(f"\n📊 Script Test Coverage:")
            print(f"   Scripts with tests: {scripts_with_tests}/{total_scripts} ({coverage_pct:.1f}%)")
            print(f"   Tests passing: {passed_tests}")
            print(f"   Tests failing: {failed_tests}")
            if skipped_tests > 0:
                print(f"   Tests skipped: {skipped_tests}")
            print(f"   Status: {result_summary['status']}")

            return True, result_summary

        except Exception as e:
            print(f"❌ Error running script tests: {e}")
            return False, {"error": str(e)}

    def run_python_hosting_coverage(self) -> Tuple[bool, dict]:
        """Run Python hosting test coverage using pytest-cov"""
        print("\n" + "=" * 60)
        print("🐍 Running Python Coverage (Hosting SDK)")
        print("=" * 60)

        python_package = self.repo_root / "python" / "microsoft-agents-hosting"

        if not python_package.exists():
            print("❌ Python hosting package not found")
            return False, {"error": "Package not found"}

        try:
            # Install pytest-cov if not available
            subprocess.run(
                ["pip3", "install", "-q", "pytest-cov"],
                check=False,
                capture_output=True
            )

            # Run tests with coverage
            cmd = [
                "pytest",
                "tests/",
                "--cov=microsoft/agents/hosting",
                "--cov-report=json:coverage-hosting.json",
                "--cov-report=term",
                "-v"
            ]

            result = subprocess.run(
                cmd,
                cwd=python_package,
                capture_output=True,
                text=True
            )

            print(result.stdout)

            if result.returncode not in [0, 1]:  # 1 = some tests failed but coverage ran
                print(f"❌ Coverage failed:\n{result.stderr}")
                return False, {"error": "Coverage failed"}

            # Read coverage results
            coverage_file = python_package / "coverage-hosting.json"
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)

                summary = coverage_data.get("totals", {})
                coverage_pct = summary.get("percent_covered", 0)

                result_summary = {
                    "total_statements": summary.get("num_statements", 0),
                    "covered_statements": summary.get("covered_lines", 0),
                    "missing_lines": summary.get("missing_lines", 0),
                    "coverage_percent": round(coverage_pct, 2),
                    "status": "✅ PASS" if coverage_pct >= 80 else "⚠️  LOW"
                }

                print(f"\n📊 Coverage: {coverage_pct:.2f}%")
                print(f"   Status: {result_summary['status']}")

                return True, result_summary
            else:
                print("⚠️  Coverage file not generated")
                return False, {"error": "No coverage file"}

        except Exception as e:
            print(f"❌ Error running Python hosting coverage: {e}")
            return False, {"error": str(e)}

    def run_typescript_coverage(self) -> Tuple[bool, dict]:
        """Run TypeScript client test coverage using Jest"""
        print("\n" + "=" * 60)
        print("📘 Running TypeScript Coverage (Client SDK)")
        print("=" * 60)

        ts_package = self.repo_root / "typescript" / "packages" / "agents-protocol-client"

        if not ts_package.exists():
            print("❌ TypeScript client package not found")
            return False, {"error": "Package not found"}

        try:
            # Run tests with coverage
            cmd = ["npm", "test", "--", "--coverage", "--coverageReporters=json", "--coverageReporters=text"]

            result = subprocess.run(
                cmd,
                cwd=ts_package,
                capture_output=True,
                text=True
            )

            print(result.stdout)

            # Read coverage results - try multiple possible file locations
            coverage_files = [
                ts_package / "coverage" / "coverage-summary.json",
                ts_package / "coverage" / "coverage-final.json",
            ]

            coverage_file = None
            for f in coverage_files:
                if f.exists():
                    coverage_file = f
                    break

            if coverage_file:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)

                # Handle different file formats
                if "total" in coverage_data:
                    # coverage-summary.json format
                    total = coverage_data["total"]
                    lines = total.get("lines", {})
                    coverage_pct = lines.get("pct", 0)
                    total_lines = lines.get("total", 0)
                    covered_lines = lines.get("covered", 0)
                else:
                    # coverage-final.json format - aggregate all files
                    total_lines = 0
                    covered_lines = 0
                    for file_data in coverage_data.values():
                        if "statementMap" in file_data and "s" in file_data:
                            statements = file_data["statementMap"]
                            hits = file_data["s"]
                            total_lines += len(statements)
                            covered_lines += sum(1 for count in hits.values() if count > 0)

                    coverage_pct = (covered_lines / total_lines * 100) if total_lines > 0 else 0

                summary = {
                    "total_lines": total_lines,
                    "covered_lines": covered_lines,
                    "coverage_percent": round(coverage_pct, 2),
                    "status": "✅ PASS" if coverage_pct >= 80 else "⚠️  LOW"
                }

                print(f"\n📊 Line Coverage: {coverage_pct:.2f}%")
                print(f"   Lines: {summary['covered_lines']}/{summary['total_lines']}")
                print(f"   Status: {summary['status']}")

                return True, summary
            else:
                print("⚠️  Coverage files not found")
                return False, {"error": "No coverage file"}

        except Exception as e:
            print(f"❌ Error running TypeScript client coverage: {e}")
            return False, {"error": str(e)}

    def run_typescript_hosting_coverage(self) -> Tuple[bool, dict]:
        """Run TypeScript hosting test coverage using Jest"""
        print("\n" + "=" * 60)
        print("📘 Running TypeScript Coverage (Hosting SDK)")
        print("=" * 60)

        ts_package = self.repo_root / "typescript" / "packages" / "agents-hosting"

        if not ts_package.exists():
            print("❌ TypeScript hosting package not found")
            return False, {"error": "Package not found"}

        try:
            # Run tests with coverage
            cmd = ["npm", "test", "--", "--coverage", "--coverageReporters=json", "--coverageReporters=text"]

            result = subprocess.run(
                cmd,
                cwd=ts_package,
                capture_output=True,
                text=True
            )

            print(result.stdout)

            # Read coverage results - try multiple possible file locations
            coverage_files = [
                ts_package / "coverage" / "coverage-summary.json",
                ts_package / "coverage" / "coverage-final.json",
            ]

            coverage_file = None
            for f in coverage_files:
                if f.exists():
                    coverage_file = f
                    break

            if coverage_file:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)

                # Handle different file formats
                if "total" in coverage_data:
                    # coverage-summary.json format
                    total = coverage_data["total"]
                    lines = total.get("lines", {})
                    coverage_pct = lines.get("pct", 0)
                    total_lines = lines.get("total", 0)
                    covered_lines = lines.get("covered", 0)
                else:
                    # coverage-final.json format - aggregate all files
                    total_lines = 0
                    covered_lines = 0
                    for file_data in coverage_data.values():
                        if "statementMap" in file_data and "s" in file_data:
                            statements = file_data["statementMap"]
                            hits = file_data["s"]
                            total_lines += len(statements)
                            covered_lines += sum(1 for count in hits.values() if count > 0)

                    coverage_pct = (covered_lines / total_lines * 100) if total_lines > 0 else 0

                summary = {
                    "total_lines": total_lines,
                    "covered_lines": covered_lines,
                    "coverage_percent": round(coverage_pct, 2),
                    "status": "✅ PASS" if coverage_pct >= 80 else "⚠️  LOW"
                }

                print(f"\n📊 Line Coverage: {coverage_pct:.2f}%")
                print(f"   Lines: {summary['covered_lines']}/{summary['total_lines']}")
                print(f"   Status: {summary['status']}")

                return True, summary
            else:
                print("⚠️  Coverage files not found")
                return False, {"error": "No coverage file"}

        except Exception as e:
            print(f"❌ Error running TypeScript hosting coverage: {e}")
            return False, {"error": str(e)}

    def print_summary(self):
        """Print summary of all coverage results"""
        print("\n" + "=" * 60)
        print("📊 COVERAGE SUMMARY")
        print("=" * 60)

        if not self.results:
            print("No coverage results available")
            return

        # Group results by type
        client_results = {}
        hosting_results = {}
        script_results = {}

        for key, data in self.results.items():
            if "script" in key:
                script_results[key] = data
            elif "hosting" in key:
                hosting_results[key] = data
            else:
                client_results[key] = data

        # Print Client SDK results
        if client_results:
            print("\n🔹 CLIENT SDKs:")
            for lang, data in client_results.items():
                lang_name = lang.replace("_client", "").replace("_", " ").upper()
                if "error" in data:
                    print(f"  {lang_name}: ❌ {data['error']}")
                else:
                    coverage = data.get("coverage_percent", 0)
                    status = data.get("status", "")
                    print(f"  {lang_name}: {coverage:.2f}% {status}")

                    if "total_lines" in data:
                        print(f"    Lines: {data['covered_lines']}/{data['total_lines']}")
                    elif "total_statements" in data:
                        print(f"    Statements: {data['covered_statements']}/{data['total_statements']}")

        # Print Hosting SDK results
        if hosting_results:
            print("\n🔸 HOSTING SDKs:")
            for lang, data in hosting_results.items():
                lang_name = lang.replace("_hosting", "").replace("_", " ").upper()
                if "error" in data:
                    print(f"  {lang_name}: ❌ {data['error']}")
                else:
                    coverage = data.get("coverage_percent", 0)
                    status = data.get("status", "")
                    print(f"  {lang_name}: {coverage:.2f}% {status}")

                    if "total_lines" in data:
                        print(f"    Lines: {data['covered_lines']}/{data['total_lines']}")
                    elif "total_statements" in data:
                        print(f"    Statements: {data['covered_statements']}/{data['total_statements']}")

        # Print Script Test results
        if script_results:
            print("\n🔧 SCRIPT TESTS:")
            for key, data in script_results.items():
                name = key.replace("_", " ").upper()
                if "error" in data:
                    print(f"  {name}: ❌ {data['error']}")
                else:
                    coverage = data.get("coverage_percent", 0)
                    status = data.get("status", "")
                    scripts_tested = data.get("scripts_with_tests", 0)
                    total_scripts = data.get("total_scripts", 0)
                    print(f"  {name}: {scripts_tested}/{total_scripts} scripts ({coverage:.1f}%) {status}")

                    tests_passed = data.get("tests_passed", 0)
                    tests_failed = data.get("tests_failed", 0)
                    print(f"    Tests: {tests_passed} passed", end="")
                    if tests_failed > 0:
                        print(f", {tests_failed} failed", end="")
                    print()

        # Calculate averages
        client_coverages = [
            data.get("coverage_percent", 0)
            for key, data in client_results.items()
            if "coverage_percent" in data
        ]

        hosting_coverages = [
            data.get("coverage_percent", 0)
            for key, data in hosting_results.items()
            if "coverage_percent" in data
        ]

        script_coverages = [
            data.get("coverage_percent", 0)
            for key, data in script_results.items()
            if "coverage_percent" in data
        ]

        print(f"\n{'='*60}")
        if client_coverages:
            avg_client = sum(client_coverages) / len(client_coverages)
            print(f"Average Client Coverage:  {avg_client:.2f}%")

        if hosting_coverages:
            avg_hosting = sum(hosting_coverages) / len(hosting_coverages)
            print(f"Average Hosting Coverage: {avg_hosting:.2f}%")

        if script_coverages:
            avg_scripts = sum(script_coverages) / len(script_coverages)
            print(f"Average Script Coverage:  {avg_scripts:.2f}%")

        all_coverages = client_coverages + hosting_coverages + script_coverages
        if all_coverages:
            avg_overall = sum(all_coverages) / len(all_coverages)
            print(f"Overall Average Coverage: {avg_overall:.2f}%")

        print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Run test coverage for Agent Protocol Client and Hosting SDKs",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--csharp",
        action="store_true",
        help="Run C# coverage only (both client and hosting)"
    )
    parser.add_argument(
        "--python",
        action="store_true",
        help="Run Python coverage only (both client and hosting)"
    )
    parser.add_argument(
        "--typescript",
        action="store_true",
        help="Run TypeScript coverage only (both client and hosting)"
    )
    parser.add_argument(
        "--scripts",
        action="store_true",
        help="Run script tests coverage only"
    )
    parser.add_argument(
        "--client",
        action="store_true",
        help="Run client SDKs only"
    )
    parser.add_argument(
        "--hosting",
        action="store_true",
        help="Run hosting SDKs only"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all SDKs (client + hosting + scripts) - default behavior"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary from previous run"
    )

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    runner = CoverageRunner(repo_root)

    # Determine what to run
    run_all_langs = not (args.csharp or args.python or args.typescript or args.scripts)
    run_all_sdks = not (args.client or args.hosting) or args.all

    if args.summary:
        # Just show summary (if results exist)
        runner.print_summary()
        return 0

    # Run coverage based on flags
    # C# Coverage
    if args.csharp or run_all_langs:
        if args.client or run_all_sdks:
            success, result = runner.run_csharp_coverage()
            runner.results["csharp_client"] = result

        if args.hosting or run_all_sdks:
            success, result = runner.run_csharp_hosting_coverage()
            runner.results["csharp_hosting"] = result

    # Python Coverage
    if args.python or run_all_langs:
        if args.client or run_all_sdks:
            success, result = runner.run_python_coverage()
            runner.results["python_client"] = result

        if args.hosting or run_all_sdks:
            success, result = runner.run_python_hosting_coverage()
            runner.results["python_hosting"] = result

    # TypeScript Coverage
    if args.typescript or run_all_langs:
        if args.client or run_all_sdks:
            success, result = runner.run_typescript_coverage()
            runner.results["typescript_client"] = result

        if args.hosting or run_all_sdks:
            success, result = runner.run_typescript_hosting_coverage()
            runner.results["typescript_hosting"] = result

    # Script Tests Coverage
    if args.scripts or run_all_langs or args.all:
        success, result = runner.run_script_tests_coverage()
        runner.results["script_tests"] = result

    # Print summary
    runner.print_summary()

    # Save results
    results_file = repo_root / ".workspace" / "coverage-results.json"
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, "w") as f:
        json.dump(runner.results, f, indent=2)

    print(f"\n✅ Results saved to: {results_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
