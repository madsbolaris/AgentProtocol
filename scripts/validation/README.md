# API Reference Validation

Validation script to check the quality of generated API reference documentation.

## Usage

```bash
# From scripts directory
make api-ref

# Or directly
python3 validation/validate-api-reference.py
```

## What It Checks

### ❌ **Errors** (Must Fix)

1. **TypeSpec Metadata Pollution**
   - Checks for developer-facing comments (BASE:, SOURCE:, RATIONALE:, etc.)
   - Example: `MESSAGING APP PATTERN:`, `CRITICAL SEMANTIC DISTINCTION:`
   - **Impact**: Confuses users with internal design notes

2. **Missing Examples/Samples**
   - Every endpoint should have HTTP request/response examples
   - Helps users understand how to use the API
   - **Impact**: Users can't figure out how to call endpoints

3. **Missing Descriptions**
   - Endpoints and models should have clear descriptions
   - **Impact**: Users don't understand what endpoints do

4. **Structural Issues**
   - MANUAL_START inside GENERATED sections
   - Mismatched MANUAL_START/END markers
   - **Impact**: Merge logic broken, content in wrong place

5. **Low Manual Content Coverage**
   - Operations files should have manual examples for at least 30% of endpoints
   - **Impact**: Auto-generated docs lack real-world guidance

### ⚠️ **Warnings** (Should Fix)

1. **Empty Parameter Descriptions**
   - Parameter tables with empty Description columns
   - Example: `| threadId | string | No | |`
   - **Impact**: Low (parameter names are often self-documenting)
   - **Fix**: Add @doc comments to TypeSpec parameters

2. **Very Short Descriptions**
   - Descriptions under 10 characters
   - **Impact**: Might not provide enough context

3. **Duplicate Headings**
   - Same heading appears multiple times (excluding standard sections)
   - **Impact**: Confusing navigation

### ℹ️ **Info** (Nice to Fix)

1. **Placeholder Content**
   - TODO, FIXME, XXX, [Coming soon], etc.
   - **Impact**: Looks unfinished

## Current Validation Results

After all fixes applied:

```
📊 Validation Results:
   ❌ Errors:   81
   ⚠️  Warnings: 183
   ℹ️  Info:     0
```

### Breakdown of Errors

**TypeSpec Metadata Pollution**: ✅ **FIXED**
- All instances removed from user-facing docs

**Missing Examples**: **17 endpoints**
- thread-subscriptions.md: 5 endpoints (structural issue causing this)
- threads.md: 5 endpoints (GET message, stream, watch operations)
- Other files: 7 endpoints scattered

**Missing Descriptions**: **64 endpoints**
- Mostly in threads.md and subscription files
- **Root Cause**: TypeSpec source files missing @doc comments
- **Fix Required**: Add descriptions to TypeSpec, then regenerate

**Structural Issues**: **5 instances**
- thread-subscriptions.md has MANUAL markers inside GENERATED section
- **Fix Required**: Restructure manual content file

### Breakdown of Warnings

**Empty Parameter Descriptions**: **183 instances**
- Standard pagination params: `after`, `limit`
- Filter params: `threadId`, `agentId`, `status`
- **Root Cause**: TypeSpec parameters missing @doc
- **Impact**: LOW - parameter names are self-documenting
- **Fix**: Add @doc decorators to TypeSpec parameters (optional)

## Recommendations

### High Priority

1. ✅ **Remove metadata pollution** - DONE
2. ✅ **Merge manual content** - DONE
3. **Fix structural issues** in thread-subscriptions.md
4. **Add examples** to 17 missing endpoints

### Medium Priority

5. **Add descriptions** to 64 endpoints (requires TypeSpec updates)
6. **Complete manual content** for all operation files

### Low Priority

7. **Add parameter descriptions** (requires TypeSpec @doc comments)

## Files Checked

The validator checks all markdown files in `api-reference/`:

```
api-reference/
├── README.md (✓)
├── operations.md (⚠️ Reference only, excluded from checks)
├── models.md (✓)
├── content-types.md (✓)
├── tools.md (✓)
├── agents.md (✓)
└── operations/
    ├── agents.md (✓)
    ├── runs.md (✓)
    ├── threads.md (⚠️ 17 endpoints need examples/descriptions)
    ├── agent-subscriptions.md (✓)
    ├── run-subscriptions.md (✓)
    └── thread-subscriptions.md (❌ Structural issues)
```

## Integration

The validation script is integrated into the documentation workflow:

```bash
# Complete workflow with validation
make docs      # Generate + merge
make api-ref   # Validate quality
```

Exit codes:
- `0` = All checks passed
- `1` = Errors found (blocks CI/CD)

## Extending the Validator

To add new checks, edit `validate-api-reference.py`:

1. Add method `_check_your_feature()`
2. Call it from `_validate_file()`
3. Append issues to `self.issues`
4. Use appropriate severity: 'error', 'warning', 'info'

Example:
```python
def _check_your_feature(self, file_path: Path, lines: List[str]):
    """Check for your specific issue."""
    for i, line in enumerate(lines, 1):
        if 'PROBLEM' in line:
            self.issues.append(ValidationIssue(
                severity='error',
                file=str(file_path),
                line=i,
                message="Found a problem",
                context=line.strip()[:80]
            ))
```
