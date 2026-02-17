#!/usr/bin/env python3
"""
Analyze expert-feedback recording files to show timing and tool usage.

Usage:
    python3 scripts/analyze_recordings.py <recording_dir>
    python3 scripts/analyze_recordings.py tests/recordings/test_generate_iteration_1_with_questions

Output:
    - Duration for each expert
    - Token usage
    - Tool call sequence with details
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def parse_tool_from_event(raw_str: str) -> List[Tuple[str, Dict]]:
    """Extract tool calls from event string representation."""
    tools = []

    # Find all ToolUseBlock instances
    # Format: ToolUseBlock(id='...', name='Read', input={'file_path': '...'})
    # The input dict can span multiple lines and contain nested structures

    # First, find all tool names
    tool_pattern = r"ToolUseBlock\([^)]*name='([^']+)'"
    tool_names = re.findall(tool_pattern, raw_str)

    if not tool_names:
        return tools

    # For each tool, try to extract input parameters
    for tool_name in tool_names:
        tool_input = {}

        # Extract common parameters with flexible matching
        # file_path
        file_path_match = re.search(r"'file_path':\s*'([^']+)'", raw_str)
        if file_path_match:
            tool_input['file_path'] = file_path_match.group(1)

        # pattern (for Glob/Grep)
        pattern_match = re.search(r"'pattern':\s*'([^']+)'", raw_str)
        if pattern_match:
            tool_input['pattern'] = pattern_match.group(1)

        # command (for Bash)
        command_match = re.search(r"'command':\s*'([^']+)'", raw_str)
        if command_match:
            tool_input['command'] = command_match.group(1)

        # output_mode (for Grep)
        output_mode_match = re.search(r"'output_mode':\s*'([^']+)'", raw_str)
        if output_mode_match:
            tool_input['output_mode'] = output_mode_match.group(1)

        tools.append((tool_name, tool_input))

    return tools


def format_tool_call(tool_name: str, tool_input: Dict) -> str:
    """Format a tool call for display."""
    if tool_name == 'Read':
        path = tool_input.get('file_path', 'unknown')
        # Shorten long paths
        if len(path) > 70:
            parts = path.split('/')
            path = '.../' + '/'.join(parts[-2:])
        return f"Read: {path}"

    elif tool_name == 'Write':
        path = tool_input.get('file_path', 'unknown')
        if len(path) > 70:
            parts = path.split('/')
            path = '.../' + '/'.join(parts[-2:])
        return f"Write: {path}"

    elif tool_name == 'Glob':
        pattern = tool_input.get('pattern', 'unknown')
        return f"Glob: {pattern}"

    elif tool_name == 'Grep':
        pattern = tool_input.get('pattern', 'unknown')
        if len(pattern) > 50:
            pattern = pattern[:50] + '...'
        output_mode = tool_input.get('output_mode', 'files')
        return f"Grep: '{pattern}' ({output_mode})"

    elif tool_name == 'Bash':
        cmd = tool_input.get('command', 'unknown')
        if len(cmd) > 60:
            cmd = cmd[:60] + '...'
        return f"Bash: {cmd}"

    else:
        return tool_name


def analyze_recording(response_file: Path) -> Dict:
    """Analyze a single recording file."""
    with open(response_file, 'r') as f:
        recording = json.load(f)

    events = recording.get('events', [])
    tool_calls = []

    # Extract all tool calls
    for event in events:
        raw_str = event.get('raw', '')

        # Check if this is an assistant message with tools
        if 'AssistantMessage' in raw_str and 'ToolUseBlock' in raw_str:
            tools = parse_tool_from_event(raw_str)
            tool_calls.extend(tools)

    return {
        'total_events': len(events),
        'tool_calls': tool_calls
    }


def find_timing_in_output(output_file: Path, expert_names: List[str]) -> Dict[str, Optional[Tuple[int, int]]]:
    """Extract timing and token info from test output file."""
    timings = {name: None for name in expert_names}

    if not output_file.exists():
        return timings

    with open(output_file, 'r') as f:
        content = f.read()

    # Pattern: ✅ [03:30] python - complete (210s, 10,880 tokens, $0.000) [1/1]
    pattern = r'✅\s+\[[^\]]+\]\s+(\w+)\s+-\s+complete\s+\((\d+)s,\s+([\d,]+)\s+tokens'

    for match in re.finditer(pattern, content):
        expert = match.group(1)
        seconds = int(match.group(2))
        tokens = int(match.group(3).replace(',', ''))

        if expert in timings:
            timings[expert] = (seconds, tokens)

    return timings


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/analyze_recordings.py <recording_dir>")
        print("Example: python3 scripts/analyze_recordings.py tests/recordings/test_generate_iteration_1_with_questions")
        sys.exit(1)

    recording_dir = Path(sys.argv[1])

    if not recording_dir.exists():
        print(f"Error: Directory not found: {recording_dir}")
        sys.exit(1)

    # Find all .response.json files
    response_files = sorted(recording_dir.glob('*.response.json'))

    if not response_files:
        print(f"No recording files found in {recording_dir}")
        sys.exit(1)

    # Find corresponding request files to get expert names
    recordings = {}
    for response_file in response_files:
        hash_id = response_file.stem.replace('.response', '')
        request_file = recording_dir / f"{hash_id}.request.json"

        if request_file.exists():
            with open(request_file, 'r') as f:
                request = json.load(f)

            # Extract expert name from prompt
            prompt = request.get('prompt', '')
            match = re.search(r'Expert Design Review:\s+([^\n]+)', prompt)
            expert_name = match.group(1).strip() if match else 'unknown'

            recordings[expert_name] = {
                'hash': hash_id,
                'request_file': request_file,
                'response_file': response_file
            }

    # Look for timing info in output files
    timings = {}
    expert_names = [name.split()[0].lower() for name in recordings.keys()]  # Get first word, lowercase

    # Check common output file locations
    import glob
    output_patterns = [
        '/private/tmp/claude-*/-Users-mabolan-AgentProtocol/tasks/*.output',
        str(recording_dir.parent.parent.parent / 'output.txt'),
        'output.txt'
    ]

    for pattern_str in output_patterns:
        for output_file in glob.glob(pattern_str):
            output_path = Path(output_file)
            if output_path.exists():
                timings = find_timing_in_output(output_path, expert_names)
                if any(v is not None for v in timings.values()):
                    break
        if timings:
            break

    # Display results
    print("="*80)
    print("Recording Analysis")
    print("="*80)
    print(f"Directory: {recording_dir}")
    print(f"Recordings found: {len(recordings)}")
    print()

    for expert_name, info in recordings.items():
        print("="*80)
        print(f"{expert_name}")
        print("="*80)

        # Analyze recording
        analysis = analyze_recording(info['response_file'])

        # Show timing if available
        timing_info = timings.get(expert_name.split()[0].lower())  # Match first word lowercase
        if timing_info:
            seconds, tokens = timing_info
            minutes = seconds // 60
            remaining_secs = seconds % 60
            print(f"Duration: {minutes}m {remaining_secs}s ({seconds}s)")
            print(f"Tokens: {tokens:,}")
        else:
            print("Duration: Not found in output logs")

        print(f"Events: {analysis['total_events']}")
        print(f"Tool calls: {len(analysis['tool_calls'])}")

        if analysis['tool_calls']:
            print("\nTool sequence:")
            for i, (tool_name, tool_input) in enumerate(analysis['tool_calls'], 1):
                formatted = format_tool_call(tool_name, tool_input)
                print(f"  {i:2d}. {formatted}")

        print()


if __name__ == '__main__':
    main()
