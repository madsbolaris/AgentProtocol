# Expert Feedback Analysis Tools

## Quick Reference

When working with expert-feedback recordings, USE THESE TOOLS instead of manually inspecting files:

### Analyze Recording Files

```bash
python3 scripts/analyze_recordings.py <recording_dir>
```

**Example:**
```bash
python3 scripts/analyze_recordings.py tests/recordings/test_generate_iteration_1_with_questions
```

**Output:**
- Duration for each expert (minutes, seconds)
- Token usage
- Total events
- Complete tool call sequence with details

**Use this when:**
- You need to know how long experts took
- You want to see what tools they used
- You're debugging recording generation
- You want to compare expert behavior

### Common Recording Directories

```bash
# Iteration 1 with questions
tests/recordings/test_generate_iteration_1_with_questions

# Question branch (Q1)
tests/recordings/test_generate_question_branch_q1

# Artifact workflow
tests/recordings/test_generate_artifact_workflow
```

## Why This Exists

Recording files are stored as Python object repr() strings, not JSON. Parsing them manually is error-prone and time-consuming. This script handles:

1. Extracting tool calls from string representations
2. Finding timing info from test output logs
3. Formatting output clearly
4. Handling multiple experts in parallel

## Implementation Details

The script parses:
- `*.response.json` - Contains event stream with tool calls
- `*.request.json` - Contains initial prompt (used to identify expert)
- `/private/tmp/claude-*/tasks/*.output` - Test output with timing info

Tool calls are extracted using regex patterns that match the `ToolUseBlock` format in the repr() strings.

## Future Improvements

If recording format changes or you need additional analysis:

1. Update `scripts/analyze_recordings.py`
2. Test with: `python3 scripts/analyze_recordings.py tests/recordings/<test_name>`
3. Commit changes

## Integration with Tests

When generating new recordings, run this script after test completes to verify:
- Experts completed successfully
- Tool usage is reasonable
- No unexpected behavior occurred
