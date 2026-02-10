# ToolLifecycleHooks

Tool Lifecycle Hooks

<!-- GENERATED_START -->

## ToolLifecycleHooks

Tool Lifecycle Hooks
2. Memory persistence:
- after_execute: Write result to journal thread
3. Audit logging:
- before_execute: Log invocation with user/agent IDs
- after_execute: Log result with timing
- on_error: Log error with context

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `afterExecute` | `LifecycleHook` | No | Executed after successful tool invocation. |
| `beforeExecute` | `LifecycleHook` | No | Executed before tool invocation. |
| `onError` | `LifecycleHook` | No | Executed when tool invocation fails. |

---
<!-- GENERATED_END -->