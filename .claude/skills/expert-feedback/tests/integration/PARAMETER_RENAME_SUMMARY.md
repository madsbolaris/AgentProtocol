# Parameter Rename: `topic` → `review_context`

## Summary

Renamed the `topic` parameter to `review_context` throughout the expert-feedback codebase to better reflect that it should contain detailed, multi-paragraph guidance rather than a short topic string.

## Why This Change?

**Before (Misleading):**
```python
topic = "Review calculator API"  # Sounds like a short title
```

**After (Clear):**
```python
review_context = """Review the calculator API for production readiness.

This API provides basic arithmetic operations...

Focus Areas:
- Input validation
- Error handling
- Security issues

Known Issues to Identify:
- Missing validation
- eval() usage (security risk)

Goal: Identify all production gaps."""
```

## Files Changed

### Core Files

1. **`prompts/experts/01-review-topic.jinja2`**
   - Line 37: `## Topic Under Review` → `## Review Context & Objectives`
   - Line 39: `{{ topic }}` → `{{ review_context }}`

2. **`scripts/prompts/templates.py`**
   - Line 100: `topic: str` → `review_context: str`
   - Line 113: Updated docstring to explain expected format
   - Line 135: `topic=topic` → `review_context=review_context`

3. **`scripts/core/spawn_experts.py`**
   - Lines 165, 381, 466: `topic: str` → `review_context: str`
   - All call sites updated

### Test Files

1. **`tests/integration/test_generate_workflow_recordings.py`**
   - Updated to use `review_context` with detailed multi-paragraph description
   - Example shows proper format with focus areas, known issues, and goals

2. **`tests/integration/test_generate_basic_recordings.py`**
   - Parameter renamed from `topic` to `review_context`

## Usage Guidelines

### ✅ Good Review Context

```python
review_context = """Review the authentication module for security and reliability.

The module handles user login, session management, and OAuth2 integration.
It's critical for protecting user data and preventing unauthorized access.

**Focus Areas:**
- Token handling and storage
- Session expiration and renewal
- OAuth2 flow implementation
- Error handling for auth failures
- Rate limiting and brute force protection

**Security Concerns:**
- Check for token leakage in logs
- Verify secure session storage
- Validate OAuth2 state parameter usage
- Review error messages (no information disclosure)

**Performance:**
- Session lookup efficiency
- Token refresh overhead
- Database query optimization

**Goal:** Ensure the authentication module meets security best practices
and can handle production load without vulnerabilities."""
```

### ❌ Bad Review Context (Too Vague)

```python
review_context = "Review the auth module"  # TOO SHORT
review_context = "Authentication"  # NOT DESCRIPTIVE
review_context = "Check auth security"  # NO CONTEXT
```

## Expected Format

The `review_context` parameter should include:

1. **Overview** (1-2 paragraphs)
   - What is being reviewed
   - Why it's important
   - Where it's located

2. **Focus Areas** (bulleted list)
   - Specific aspects to examine
   - Key concerns to investigate

3. **Known Issues or Context** (optional but helpful)
   - Things experts should look for
   - Background information
   - Previous feedback or concerns

4. **Goal Statement**
   - What you want to achieve from the review
   - Success criteria

## Migration Guide

If you have code using the old `topic` parameter:

```python
# Before
await spawn_all_experts(
    experts=["typescript"],
    topic="Review API",  # ❌ Too short
    workspace=workspace,
    ...
)

# After
await spawn_all_experts(
    experts=["typescript"],
    review_context="""Review the REST API for production readiness.

    The API provides CRUD operations for user management...

    Focus on error handling, validation, and security.

    Goal: Identify issues preventing production deployment.""",  # ✅ Detailed
    workspace=workspace,
    ...
)
```

## Benefits

1. **Clearer expectations** - Developers know to provide details, not just a title
2. **Better agent guidance** - Agents get comprehensive context upfront
3. **More consistent reviews** - Detailed specs lead to more focused analysis
4. **Self-documenting** - Parameter name indicates expected content

## Testing

All existing tests have been updated and pass with the new parameter name.

Run tests to verify:
```bash
cd /Users/mabolan/AgentProtocol/.claude/skills/expert-feedback
pytest tests/integration/test_generate_workflow_recordings.py -v
pytest tests/integration/test_generate_basic_recordings.py -v
```
