# Universal Snippet Extractor

A single Python script that extracts code snippets from tests in **all languages** (C#, Python, TypeScript).

## Quick Start

```bash
# Extract snippets for all languages
python3 scripts/extract-snippets.py all

# Extract for specific language
python3 scripts/extract-snippets.py csharp
python3 scripts/extract-snippets.py python
python3 scripts/extract-snippets.py typescript
```

## Why Universal?

- ✅ **One script** for all languages (not 3 separate scripts)
- ✅ **Same pattern** everywhere (consistent structure)
- ✅ **Easy maintenance** (update once, works for all)
- ✅ **Add languages** easily (just add config)

## How Tests Are Structured

All languages follow the same pattern - only syntax differs:

```
┌─────────────────────────┐
│ Marker                  │ [DocExample] / @doc_example / @docExample
├─────────────────────────┤
│ Arrange (not extracted) │ Test setup, not in docs
├─────────────────────────┤
│ Act (EXTRACTED)         │ ← This becomes the snippet
├─────────────────────────┤
│ Assert (not extracted)  │ Test validation, not in docs
└─────────────────────────┘
```

## Usage

```bash
# Extract all languages
python3 scripts/extract-snippets.py all

# Or specific language
python3 scripts/extract-snippets.py python

# In CI
./scripts/verify-snippets.sh  # Extracts + checks for changes
```

**Output:** `docs/snippets/{language}/{snippet-id}_main.{ext}`
