#!/usr/bin/env python3
"""
Shared web UI analysis for all experts.

Analyzes web UI implementation, patterns, and potential issues.

Usage:
    python3 scripts/shared/analyze_web_ui.py --file /path/to/web_ui.py
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Any


def analyze_web_ui(file_path: Path) -> Dict[str, Any]:
    """Analyze web UI implementation.

    Args:
        file_path: Path to web UI file

    Returns:
        Dict with UI analysis:
        - file_info: File metadata
        - components: Detected components/routes
        - patterns: Design patterns used
        - issues: Potential issues
        - metrics: Code metrics
    """
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError) as e:
        return {"error": f"Cannot read file: {e}"}

    lines = content.split('\n')
    issues = []
    patterns = []
    components = []

    # File info
    file_info = {
        "path": str(file_path),
        "size_bytes": len(content),
        "line_count": len(lines),
        "framework": detect_framework(content)
    }

    # Detect routes/endpoints
    route_patterns = [
        r'@app\.route\(["\']([^"\']+)["\']\)',  # Flask
        r'@router\.(get|post|put|delete)\(["\']([^"\']+)["\']\)',  # FastAPI
        r'app\.(get|post|put|delete)\(["\']([^"\']+)["\']\)',  # Express
    ]

    for pattern in route_patterns:
        for match in re.finditer(pattern, content):
            route_info = {
                "type": "route",
                "method": match.group(1) if len(match.groups()) > 1 else "GET",
                "path": match.group(2) if len(match.groups()) > 1 else match.group(1),
                "line": content[:match.start()].count('\n') + 1
            }
            components.append(route_info)

    # Detect HTML templates (inline)
    inline_html_count = len(re.findall(r'""".*?<html>.*?"""', content, re.DOTALL))
    if inline_html_count > 0:
        issues.append({
            "severity": "medium",
            "issue": f"Found {inline_html_count} inline HTML templates",
            "recommendation": "Consider using template files for better maintainability"
        })

    # Detect JavaScript (inline)
    inline_js_matches = re.findall(r'<script>.*?</script>', content, re.DOTALL)
    if inline_js_matches:
        total_js_lines = sum(js.count('\n') for js in inline_js_matches)
        if total_js_lines > 100:
            issues.append({
                "severity": "high",
                "issue": f"Found {total_js_lines} lines of inline JavaScript",
                "recommendation": "Extract JavaScript to separate files for better maintainability"
            })

    # Detect CSS (inline)
    inline_css_matches = re.findall(r'<style>.*?</style>', content, re.DOTALL)
    if inline_css_matches:
        total_css_lines = sum(css.count('\n') for css in inline_css_matches)
        if total_css_lines > 50:
            issues.append({
                "severity": "medium",
                "issue": f"Found {total_css_lines} lines of inline CSS",
                "recommendation": "Extract CSS to separate files"
            })

    # Detect patterns
    if 'async def' in content:
        patterns.append("async/await (asynchronous)")
    if 'class ' in content and 'def __init__' in content:
        patterns.append("Object-oriented (classes)")
    if 'websocket' in content.lower():
        patterns.append("WebSocket support")
    if 'sse' in content.lower() or 'server-sent events' in content.lower():
        patterns.append("Server-Sent Events (SSE)")

    # Check for security issues
    if 'eval(' in content:
        issues.append({
            "severity": "critical",
            "issue": "Use of eval() detected",
            "recommendation": "Avoid eval() - major security risk"
        })

    if re.search(r'innerHTML\s*=', content):
        issues.append({
            "severity": "high",
            "issue": "Direct innerHTML assignment detected",
            "recommendation": "Use textContent or createElement to prevent XSS"
        })

    # Check for error handling
    try_count = content.count('try:')
    except_count = content.count('except')
    if try_count == 0 and len(lines) > 100:
        issues.append({
            "severity": "medium",
            "issue": "No error handling (try/except) found",
            "recommendation": "Add error handling for production robustness"
        })

    # Check for logging
    logging_patterns = ['logger.', 'logging.', 'console.log', 'print(']
    has_logging = any(pattern in content for pattern in logging_patterns)
    if not has_logging and len(lines) > 100:
        issues.append({
            "severity": "low",
            "issue": "No logging detected",
            "recommendation": "Add logging for debugging and monitoring"
        })

    # Metrics
    function_count = len(re.findall(r'^def\s+\w+', content, re.MULTILINE))
    class_count = len(re.findall(r'^class\s+\w+', content, re.MULTILINE))

    metrics = {
        "lines_of_code": len(lines),
        "function_count": function_count,
        "class_count": class_count,
        "route_count": len([c for c in components if c["type"] == "route"]),
        "try_except_blocks": try_count,
        "inline_html_lines": sum(
            content[m.start():m.end()].count('\n')
            for m in re.finditer(r'""".*?<html>.*?"""', content, re.DOTALL)
        )
    }

    return {
        "file_info": file_info,
        "components": components,
        "patterns": patterns,
        "issues": issues,
        "metrics": metrics,
        "issue_count": len(issues),
        "critical_issues": len([i for i in issues if i.get("severity") == "critical"]),
        "high_issues": len([i for i in issues if i.get("severity") == "high"])
    }


def detect_framework(content: str) -> str:
    """Detect web framework used.

    Args:
        content: File content

    Returns:
        Framework name or "unknown"
    """
    if 'from flask import' in content or 'import flask' in content:
        return "Flask"
    if 'from fastapi import' in content or 'import fastapi' in content:
        return "FastAPI"
    if 'from django' in content or 'import django' in content:
        return "Django"
    if 'express()' in content:
        return "Express.js"
    if 'import React' in content or 'from react' in content:
        return "React"
    return "unknown"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze web UI implementation"
    )
    parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="Path to web UI file"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (json or summary)"
    )

    args = parser.parse_args()

    result = analyze_web_ui(args.file)

    if "error" in result:
        print(json.dumps(result))
        return 1

    if args.format == "summary":
        # Human-readable summary
        print(f"\n🌐 Web UI Analysis: {result['file_info']['path']}\n")
        print(f"Framework: {result['file_info']['framework']}")
        print(f"Lines: {result['file_info']['line_count']:,}")

        print(f"\n📊 Metrics:")
        for metric, value in result['metrics'].items():
            print(f"  {metric.replace('_', ' ').title()}: {value}")

        if result['patterns']:
            print(f"\n✨ Patterns:")
            for pattern in result['patterns']:
                print(f"  - {pattern}")

        if result['components']:
            print(f"\n🔌 Components ({len(result['components'])}):")
            for comp in result['components'][:10]:  # First 10
                print(f"  - {comp['method']} {comp['path']} (line {comp['line']})")
            if len(result['components']) > 10:
                print(f"  ... and {len(result['components']) - 10} more")

        if result['issues']:
            print(f"\n⚠️ Issues Found: {result['issue_count']}")
            print(f"   Critical: {result['critical_issues']}")
            print(f"   High: {result['high_issues']}")
            for issue in result['issues']:
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "⚪"
                }.get(issue.get("severity", "low"), "⚪")
                print(f"\n{severity_emoji} {issue['issue']}")
                if 'recommendation' in issue:
                    print(f"   → {issue['recommendation']}")
        else:
            print("\n✅ No issues found")
        print()
    else:
        # JSON output
        print(json.dumps(result, indent=2))

    return 0


if __name__ == "__main__":
    exit(main())
