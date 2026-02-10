# ToolDefinition

Example of a tool with nested input parameters.

<!-- GENERATED_START -->

## ToolDefinition

Example of a tool with nested input parameters.
XML Output:
```xml
<tool name="get_weather" description="Get weather data">
<inputs>
<input name="location" type="text" required="true" />
<input name="units" type="text" value="fahrenheit" />
</inputs>
</tool>
```

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `description` | `string` | Yes |  |
| `inputs` | `InputParameter[]` | Yes |  |
| `name` | `string` | Yes |  |

---
<!-- GENERATED_END -->