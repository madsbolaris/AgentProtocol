# ToolOutput

Tool Output

<!-- GENERATED_START -->

## ToolOutput

Tool Output

### Usage

Use Cases:
- Tool approval: Human reviews delete_file before execution
- External execution: Tools executed by external system, results fed back
- Modified execution: Human modifies tool arguments before running

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `output` | `string` | Yes | Tool execution result. |
| `tool_call_id` | `string` | Yes | Tool call ID this output corresponds to. |

---
<!-- GENERATED_END -->