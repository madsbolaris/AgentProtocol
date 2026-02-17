#!/usr/bin/env python3
"""
Analyze recording files to review prompts and agent outputs.

This script helps verify that prompts are working correctly by:
1. Extracting the compiled prompt sent to agents
2. Showing the resulting agent work/output
3. Identifying any unexpected behaviors

Usage:
    # Analyze all recordings
    python3 tests/integration/analyze_recordings.py

    # Analyze specific recording by hash
    python3 tests/integration/analyze_recordings.py --hash 344dbeddc140ac96

    # Analyze most recent recordings
    python3 tests/integration/analyze_recordings.py --recent 5
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


def load_recording(recordings_dir: Path, hash_id: str) -> tuple[Optional[Dict], Optional[Dict]]:
    """Load request and response for a recording hash."""
    request_file = recordings_dir / f"{hash_id}.request.json"
    response_file = recordings_dir / f"{hash_id}.response.json"

    request_data = None
    response_data = None

    if request_file.exists():
        with open(request_file) as f:
            request_data = json.load(f)

    if response_file.exists():
        with open(response_file) as f:
            response_data = json.load(f)

    return request_data, response_data


def extract_prompt_from_request(request_data: Dict[str, Any]) -> str:
    """Extract the main prompt text from request data."""
    if not request_data:
        return "No request data"

    prompt = request_data.get("prompt", "")

    # Handle list format (system blocks)
    if isinstance(prompt, list):
        parts = []
        for block in prompt:
            if isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
            elif isinstance(block, str):
                parts.append(block)
        prompt = "\n\n".join(parts)

    return prompt


def extract_agent_output_from_response(response_data: Dict[str, Any]) -> str:
    """Extract the agent's final output/response from response events."""
    if not response_data:
        return "No response data"

    events = response_data.get("events", [])

    # Extract text content from AssistantMessage events
    content_parts = []
    for event in events:
        raw = event.get("raw", "")

        # Look for AssistantMessage with TextBlock content
        if "AssistantMessage" in raw and "TextBlock(text=" in raw:
            # Extract text between TextBlock(text=" and ")
            try:
                start = raw.find('TextBlock(text="') + len('TextBlock(text="')
                if start > len('TextBlock(text="') - 1:
                    # Find the closing quote - need to handle escaped quotes
                    end = start
                    while end < len(raw):
                        if raw[end] == '"' and (end == start or raw[end-1] != '\\'):
                            break
                        end += 1

                    if end < len(raw):
                        text = raw[start:end]
                        # Unescape common escape sequences
                        text = text.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
                        content_parts.append(text)
            except Exception:
                # If parsing fails, skip this event
                pass

    return "\n".join(content_parts) if content_parts else "No content found in response"


def identify_expert_from_prompt(prompt: str) -> str:
    """Try to identify which expert this recording is for."""
    prompt_lower = prompt.lower()

    if "typescript" in prompt_lower:
        return "typescript"
    elif "python" in prompt_lower:
        return "python"
    elif "synthesis" in prompt_lower or "consolidat" in prompt_lower:
        return "synthesis"
    else:
        return "unknown"


def analyze_tool_usage(response_data: Dict[str, Any]) -> Dict[str, int]:
    """Analyze tool usage from response events."""
    if not response_data:
        return {}

    events = response_data.get("events", [])
    tool_counts = {}

    for event in events:
        raw = event.get("raw", "")
        # Look for ToolUseBlock with name
        if "ToolUseBlock" in raw and "name='" in raw:
            try:
                start = raw.find("name='") + len("name='")
                end = raw.find("'", start)
                if start > len("name='") - 1 and end > start:
                    tool_name = raw[start:end]
                    tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            except Exception:
                pass

    return tool_counts


def analyze_recording(recordings_dir: Path, hash_id: str, verbose: bool = False) -> None:
    """Analyze a single recording and display summary."""
    print(f"\n{'='*80}")
    print(f"Recording: {hash_id}")
    print(f"{'='*80}")

    request_data, response_data = load_recording(recordings_dir, hash_id)

    if not request_data and not response_data:
        print(f"❌ Recording files not found for hash: {hash_id}")
        return

    # Extract info
    prompt = extract_prompt_from_request(request_data)
    output = extract_agent_output_from_response(response_data)
    expert = identify_expert_from_prompt(prompt)
    tool_usage = analyze_tool_usage(response_data)

    # Display summary
    print(f"\n🤖 Expert: {expert.upper()}")
    print(f"\n📝 Prompt Length: {len(prompt)} characters")
    print(f"📤 Output Length: {len(output)} characters")

    # Display tool usage
    if tool_usage:
        print(f"\n🔧 Tool Usage:")
        total_tools = sum(tool_usage.values())
        for tool, count in sorted(tool_usage.items()):
            print(f"   - {tool}: {count}")
        print(f"   Total: {total_tools} tool calls")

    # Show prompt preview
    print(f"\n{'─'*80}")
    print("📋 PROMPT PREVIEW (first 500 chars):")
    print(f"{'─'*80}")
    print(prompt[:500])
    if len(prompt) > 500:
        print("\n... [truncated] ...")

    # Show output preview
    print(f"\n{'─'*80}")
    print("💬 AGENT OUTPUT PREVIEW (first 1000 chars):")
    print(f"{'─'*80}")
    print(output[:1000])
    if len(output) > 1000:
        print("\n... [truncated] ...")

    # Look for concerning patterns in output
    print(f"\n{'─'*80}")
    print("🔍 ANALYSIS:")
    print(f"{'─'*80}")

    concerning_patterns = []

    # Check tool usage efficiency
    if tool_usage:
        bash_count = tool_usage.get("Bash", 0)
        glob_count = tool_usage.get("Glob", 0)
        grep_count = tool_usage.get("Grep", 0)
        read_count = tool_usage.get("Read", 0)

        # Check for inefficient patterns
        if bash_count > 5 and expert in ["typescript", "python"]:
            concerning_patterns.append(f"⚠️  High Bash usage ({bash_count}) - consider using Glob/Grep instead")

        if bash_count > 0 and glob_count == 0 and expert in ["typescript", "python"]:
            concerning_patterns.append(f"⚠️  Used Bash but no Glob - may have inefficient file discovery")

        total_tools = sum(tool_usage.values())
        if total_tools > 20 and expert in ["typescript", "python"]:
            concerning_patterns.append(f"⚠️  High tool usage ({total_tools}) - target is ~10-15 for small projects")

        if read_count > 10:
            concerning_patterns.append(f"⚠️  Many file reads ({read_count}) - may be reading too broadly")

    # Check if agent is doing unexpected things
    if "I cannot" in output or "I can't" in output:
        concerning_patterns.append("⚠️  Agent refused or couldn't complete task")

    if len(output) < 200 and expert in ["typescript", "python"]:
        concerning_patterns.append("⚠️  Output seems too short - agent may not have completed properly")

    # Check for expected patterns based on expert type
    if expert == "typescript":
        if "typescript" not in output.lower() and "ts" not in output.lower():
            concerning_patterns.append("⚠️  TypeScript expert output doesn't mention TypeScript")

    if expert == "python":
        if "python" not in output.lower() and "py" not in output.lower():
            concerning_patterns.append("⚠️  Python expert output doesn't mention Python")

    # Check for expected review structure
    if expert in ["typescript", "python"]:
        if "## " not in output:
            concerning_patterns.append("⚠️  Output may be missing markdown structure (no ## headers)")
        if "concern" not in output.lower() and "recommendation" not in output.lower():
            concerning_patterns.append("⚠️  Output may be missing expected sections (concerns, recommendations)")

    if concerning_patterns:
        print("\n".join(concerning_patterns))
    else:
        print("✅ No obvious issues detected")

    # Save detailed analysis if verbose
    if verbose:
        analysis_file = recordings_dir / f"{hash_id}.analysis.txt"
        with open(analysis_file, 'w') as f:
            f.write(f"Recording Analysis: {hash_id}\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Expert: {expert}\n\n")
            f.write(f"FULL PROMPT:\n{'-'*80}\n{prompt}\n\n")
            f.write(f"FULL OUTPUT:\n{'-'*80}\n{output}\n\n")
            if concerning_patterns:
                f.write(f"CONCERNS:\n{'-'*80}\n")
                f.write("\n".join(concerning_patterns))
        print(f"\n💾 Detailed analysis saved to: {analysis_file}")


def get_recent_recordings(recordings_dir: Path, count: int = 5) -> List[str]:
    """Get the N most recently created recording hashes."""
    request_files = list(recordings_dir.glob("*.request.json"))

    # Sort by modification time (most recent first)
    request_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    # Extract hashes
    hashes = [f.stem.replace(".request", "") for f in request_files[:count]]

    return hashes


def main():
    parser = argparse.ArgumentParser(description="Analyze recording files")
    parser.add_argument("--hash", help="Specific recording hash to analyze")
    parser.add_argument("--recent", type=int, help="Analyze N most recent recordings")
    parser.add_argument("--all", action="store_true", help="Analyze all recordings")
    parser.add_argument("--verbose", "-v", action="store_true", help="Save detailed analysis to files")
    parser.add_argument("--recordings-dir", help="Custom recordings directory (default: tests/recordings)",
                       default=None)
    parser.add_argument("--test", help="Specific test name subdirectory to analyze")
    parser.add_argument("--list-tests", action="store_true", help="List available test directories")

    args = parser.parse_args()

    # List available tests and exit
    if args.list_tests:
        base_dir = Path("tests/recordings")
        if base_dir.exists():
            test_dirs = [d.name for d in base_dir.iterdir() if d.is_dir()]
            if test_dirs:
                print("\n📁 Available test directories:")
                for test_dir in sorted(test_dirs):
                    recording_count = len(list((base_dir / test_dir).glob("*.response.json")))
                    print(f"   - {test_dir} ({recording_count} recordings)")
            else:
                print("No test directories found in tests/recordings/")
        else:
            print("tests/recordings/ directory not found")
        return

    # Determine recordings directory
    if args.recordings_dir:
        recordings_dir = Path(args.recordings_dir)
    elif args.test:
        recordings_dir = Path("tests/recordings") / args.test
    else:
        recordings_dir = Path("tests/recordings")

    if not recordings_dir.exists():
        print(f"❌ Recordings directory not found: {recordings_dir}")
        sys.exit(1)

    # Determine which recordings to analyze
    if args.hash:
        hashes = [args.hash]
    elif args.recent:
        hashes = get_recent_recordings(recordings_dir, args.recent)
        print(f"\n📊 Analyzing {len(hashes)} most recent recordings...")
    elif args.all:
        request_files = list(recordings_dir.glob("*.request.json"))
        hashes = [f.stem for f in request_files]
        print(f"\n📊 Analyzing all {len(hashes)} recordings...")
    else:
        # Default: analyze 3 most recent
        hashes = get_recent_recordings(recordings_dir, 3)
        print(f"\n📊 Analyzing 3 most recent recordings...")
        print("(Use --recent N, --all, or --hash to change)")

    # Analyze each recording
    for hash_id in hashes:
        analyze_recording(recordings_dir, hash_id, args.verbose)

    print(f"\n{'='*80}")
    print(f"✅ Analysis complete! Reviewed {len(hashes)} recording(s)")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
