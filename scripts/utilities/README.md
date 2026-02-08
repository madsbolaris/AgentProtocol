# Utility Scripts

General-purpose utility scripts for development, testing, and bot management.

## Bot Management

### start-all-echo-bots.sh
Start all echo bot implementations (Python, .NET, TypeScript) simultaneously.

```bash
./scripts/utilities/start-all-echo-bots.sh
```

### copy-echo-bots.sh
Copy echo bot samples between directories.

```bash
./scripts/utilities/copy-echo-bots.sh
```

## Testing & Validation

### test_function_tools.sh
Test function tools functionality across implementations.

```bash
./scripts/utilities/test_function_tools.sh
```

### validate_test_infrastructure.sh
Validate that test infrastructure is set up correctly.

```bash
./scripts/utilities/validate_test_infrastructure.sh
```

### validate-echo-bots.py
Validate that echo bot samples haven't changed from their baseline.

```bash
python scripts/utilities/validate-echo-bots.py

# Update baselines (only when intentionally changing echo bots)
python scripts/utilities/validate-echo-bots.py --update
```

## Development Tools

### install-git-hooks.sh
Install git hooks for the repository.

```bash
./scripts/utilities/install-git-hooks.sh
```

### wrap_with_thread.py
Wrap messages in thread XML elements for testing.

```bash
python scripts/utilities/wrap_with_thread.py <input-file> <output-file>
```

### fix_xml_indentation.py
Fix XML indentation in test files.

```bash
python scripts/utilities/fix_xml_indentation.py <file-or-directory>
```

### generate_function_tools_golden_files.sh
Generate golden files for basic.m365.agent.

```bash
./scripts/utilities/generate_function_tools_golden_files.sh
```

## Usage Tips

- Most shell scripts should be run from the repository root
- Python scripts can be run from anywhere with proper paths
- Check script help text with `--help` flag when available
