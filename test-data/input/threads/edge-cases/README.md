# Edge Case Test Files

This directory contains test files for boundary conditions, error scenarios, and unusual input patterns.

## Subdirectories

### empty/
Tests for empty or minimal content:
- `40-empty-thread.xml` - Thread with no messages or minimal structure

**Total**: 1 file

**Purpose**: Validates handling of empty threads, which may occur during thread initialization or cleanup.

### duplicates/
Tests for duplicate content handling:
- `42-duplicate-user-messages.xml` - Thread with duplicate user messages

**Total**: 1 file

**Purpose**: Validates deduplication logic, message ID uniqueness enforcement, and duplicate detection.

### long/
Tests for extended content:
- Currently empty (no files have been moved here yet)

**Total**: 0 files

**Purpose**: Reserved for testing long conversations, large message counts, and performance limits.

**Note**: The `43-long-conversation.xml` file is located in `../conversations/multi-turn/` as it's a valid multi-turn conversation test.

### special/
Tests for special cases and unusual patterns:
- `18-edge-cases.xml` - General edge case scenarios

**Total**: 1 file

**Purpose**: Validates handling of unusual but valid patterns that don't fit other categories.

## Purpose

Edge case tests ensure robust handling of:
- Boundary conditions
- Unusual but valid inputs
- Degenerate cases
- Performance limits
- Error recovery

## Testing Focus

### Empty Content
- Empty threads (no messages)
- Empty messages (no content)
- Empty text fields
- Missing optional attributes

```xml
<!-- Empty thread -->
<thread thread-id="thread_001" created-at="2024-02-09T12:00:00Z">
  <!-- No messages -->
</thread>
```

### Duplicate Content
- Duplicate message IDs (should fail validation)
- Duplicate content (may be valid)
- Repeated function calls
- Duplicate tool results

```xml
<!-- Duplicate messages - should be detected -->
<thread>
  <user message-id="msg_001">Hello</user>
  <user message-id="msg_001">Hello</user>  <!-- Duplicate ID! -->
</thread>
```

### Long Content
- Many messages (100+)
- Long text content (10KB+)
- Deep nesting
- Large attachments

### Special Cases
- Unicode and special characters
- Whitespace handling
- Attribute ordering
- Namespace variations
- Schema edge cases

## Edge Case Categories

### 1. Structural Edge Cases
- Minimal valid structure
- Maximum nesting depth
- Empty elements
- Self-closing tags

### 2. Content Edge Cases
- Empty strings
- Very long strings
- Special characters
- Malformed but parseable content

### 3. Semantic Edge Cases
- Orphaned tool results (no matching call)
- Out-of-order timestamps
- Missing required context
- Unusual role sequences

### 4. Performance Edge Cases
- Large message counts
- Large individual messages
- Complex nested structures
- High attribute counts

## Validation Behavior

Edge case tests verify that the system:
- ✅ Accepts valid edge cases without error
- ⚠️ Warns on unusual but valid patterns
- ❌ Rejects invalid edge cases appropriately
- 🛡️ Handles edge cases without crashes

### Expected Outcomes

| Edge Case | Expected Behavior |
|-----------|------------------|
| Empty thread | Parse successfully, zero messages |
| Duplicate message ID | Validation error |
| Duplicate content | Warning, but accept |
| Very long message | Accept up to reasonable limit |
| Out-of-order timestamps | Validation error |
| Missing optional attributes | Accept with defaults |

## Total Files

**3 files** across 4 subdirectories (1 subdirectory currently empty).

**Note**: The `long/` subdirectory is currently empty but reserved for future tests of extended conversations and performance scenarios.

## Relationship to Invalid Tests

Edge cases are **valid but unusual** inputs. For **invalid** inputs that should fail parsing or validation, see the `../invalid/` directory which contains 17 test files for negative testing.

Key differences:
- **Edge cases** (this directory): Valid XML, unusual patterns, should parse successfully
- **Invalid cases** (`../invalid/`): Invalid XML or protocol violations, should fail validation

## Usage Example

```python
# Python - Test empty thread handling
thread = parse_thread_xml("edge-cases/empty/40-empty-thread.xml")
assert thread is not None
assert len(thread.messages) == 0

# Test duplicate detection
try:
    thread = parse_thread_xml("edge-cases/duplicates/42-duplicate-user-messages.xml")
    # May parse but should fail validation
    result = validate_thread(thread)
    assert not result.is_valid
    assert any("duplicate" in str(err).lower() for err in result.errors)
except ValidationError as e:
    assert "duplicate" in str(e).lower()
```

```csharp
// C# - Test special edge cases
var xml = File.ReadAllText("edge-cases/special/18-edge-cases.xml");
var thread = ParseThreadXml(xml);

// Should parse successfully
Assert.NotNull(thread);

// Validate for edge case handling
var validationResult = ValidateThread(thread);
// May have warnings but should not have critical errors
Assert.True(validationResult.IsValid || validationResult.HasWarningsOnly);
```

## Future Test Additions

Planned additions for comprehensive edge case coverage:

### long/ subdirectory
- `90-hundred-message-thread.xml` - Thread with 100+ messages
- `91-very-long-text-content.xml` - Message with 50KB+ text
- `92-deep-nesting.xml` - Deeply nested content structure

### special/ subdirectory
- Unicode handling tests
- Whitespace preservation tests
- XML entity handling tests
- Namespace variation tests

## Related Directories

- See `../invalid/` for negative test cases (invalid XML)
- See `../basic/` for normal, well-formed test cases
- See `../conversations/multi-turn/43-long-conversation.xml` for extended conversation testing
