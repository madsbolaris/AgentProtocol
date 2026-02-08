# Git Hooks for Agent Protocol

This directory contains git hooks that automate validation and ensure code quality.

## Installation

Run the installation script from the repository root:

```bash
./scripts/install-git-hooks.sh
```

This creates symlinks from `.git/hooks/` to `.githooks/`, making the hooks active.

## Available Hooks

### pre-commit

**Runs before every commit**

Ensures:
1. ✅ Documentation examples are extracted from tests
2. ⚠️  Warns if golden files are being modified
3. ✅ Python tests validate against golden files (if Python files changed)
4. ✅ C# tests validate against golden files (if C# files changed)
5. ❌ Prevents commits with `UPDATE_GOLDEN` env var set

**Example output:**
```
🔍 Running pre-commit checks...

📝 Extracting documentation examples...
✓ Documentation examples extracted

🔍 Checking for golden file changes...
⚠️  Golden files are being modified:
    test-data/results/shared/basic-xml-serialization.json

⚠️  Please ensure these changes are intentional!

🐍 Running Python tests with golden file validation...
✓ Python tests passed (validated against golden files)

═══════════════════════════════════════════════════════════════
✓ All pre-commit checks passed!
═══════════════════════════════════════════════════════════════
```

**If tests fail:**
```
✗ Python tests failed

If output changes are intentional, update golden files:
  pytest --update-golden tests/test_doc_examples.py

Then review and stage the updated golden files:
  git add test-data/results/shared/
```

### post-merge

**Runs after git pull/merge**

Validates tests after pulling changes, especially useful when golden files were updated by others.

**Example output:**
```
🔄 Post-merge validation...
⚠️  Golden files were updated in this merge:
    test-data/results/shared/multimodal-message.json

Running tests to validate against new golden files...

🐍 Validating Python tests...
✓ Python tests pass with updated golden files

✓ Post-merge validation complete
```

## Bypassing Hooks

In rare cases where you need to bypass the hooks:

```bash
# Skip pre-commit hook
git commit --no-verify

# Skip all hooks
git push --no-verify
```

**Warning:** Only bypass hooks when absolutely necessary, as they prevent common mistakes.

## Hook Behavior

### When Python Files Change

The pre-commit hook will:
1. Extract documentation examples
2. Run Python tests in validation mode
3. Fail if outputs don't match golden files

### When C# Files Change

The pre-commit hook will:
1. Extract documentation examples
2. Run .NET tests in validation mode
3. Fail if outputs don't match golden files

### When Golden Files Change

The pre-commit hook will:
1. Display which golden files are being modified
2. Show a diff of the changes
3. Warn you to review carefully
4. Continue with commit (allows intentional updates)

### UPDATE_GOLDEN Protection

If `UPDATE_GOLDEN=1` is set in your environment, the pre-commit hook will fail:

```
✗ UPDATE_GOLDEN environment variable is set
  This prevents accidental commits in update mode.
  Unset it before committing: unset UPDATE_GOLDEN
```

This prevents accidentally committing while in golden file update mode.

## Workflow Examples

### Normal Development

```bash
# Edit code
vim src/my_file.py

# Commit (hooks run automatically)
git commit -m "Fix bug"
# → pre-commit validates tests pass
# → commit succeeds if validation passes
```

### Updating Golden Files

```bash
# Make changes that affect output
vim src/serializer.py

# Try to commit - tests fail
git commit -m "Update serialization format"
# → ✗ Python tests failed (output mismatch)

# Review the diff, confirm change is intentional
pytest tests/test_doc_examples.py  # see the diff

# Update golden files
pytest --update-golden tests/test_doc_examples.py
# → ✓ Updated golden file: basic-xml-serialization

# Review changes
git diff test-data/results/shared/basic-xml-serialization.json

# Stage golden files
git add test-data/results/shared/

# Commit
git commit -m "Update serialization format"
# → pre-commit shows golden file warning
# → commit succeeds
```

### After Pulling Changes

```bash
# Pull changes from remote
git pull origin main
# → post-merge hook runs automatically

# If golden files were updated:
# → Tests validate against new golden files
# → Warns if tests fail

# If tests fail, update your code or reach out to the PR author
```

## Uninstalling Hooks

To remove the git hooks:

```bash
rm .git/hooks/pre-commit
rm .git/hooks/post-merge
```

Or reinstall default hooks:

```bash
# This will restore git's default hooks
git init
```

## Customizing Hooks

The hooks are located in `.githooks/` and are under version control.

To modify a hook:
1. Edit the file in `.githooks/`
2. Test it manually: `.githooks/pre-commit`
3. Commit the changes
4. Others will get the update when they pull

## Troubleshooting

### Hook doesn't run

Check if hooks are installed:
```bash
ls -la .git/hooks/
```

You should see symlinks pointing to `.githooks/`:
```
pre-commit -> ../../.githooks/pre-commit
post-merge -> ../../.githooks/post-merge
```

If not, run the installation script:
```bash
./scripts/install-git-hooks.sh
```

### Hook fails with permission denied

Make sure hooks are executable:
```bash
chmod +x .githooks/*
```

### Tests fail in hook but pass manually

The hook may be using a different environment. Check:
- Python version: `python --version`
- Working directory
- Environment variables: `env | grep UPDATE_GOLDEN`

### Hook is too slow

If the hook takes too long, you can:
1. Skip it temporarily: `git commit --no-verify`
2. Optimize the hook script
3. Run only affected tests (modify the hook)

## Best Practices

1. **Keep hooks fast** - They run on every commit, so speed matters
2. **Make failures clear** - Good error messages help developers fix issues
3. **Allow bypassing** - Sometimes you need `--no-verify`, that's OK
4. **Test hooks** - Run hooks manually before committing changes to them
5. **Document changes** - Update this README when modifying hooks

## Related Documentation

- [Golden File Testing](../docs/contributing/golden-files.md)
- [Test-Driven Documentation](../docs/contributing/test-driven-docs.md)
- [GitHub Actions Workflow](../.github/workflows/test-and-docs.yml)
