# LintError

Lint Error

<!-- GENERATED_START -->

## LintError

Lint Error
Error from linting operation.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `element` | `string` | No | Element or attribute that caused error |
| `fix` | `string` | No | Suggested fix |
| `line` | `int32` | No | Location in file (line number) |
| `message` | `string` | Yes | Error message |
| `severity` | `"error" | "warning" | "info"` | Yes | Severity level |

---
<!-- GENERATED_END -->