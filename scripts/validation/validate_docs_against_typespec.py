#!/usr/bin/env python3
"""
Validate documentation against TypeSpec source of truth.

This script:
1. Parses TypeSpec files to extract models, discriminators, properties, and enums
2. Searches documentation for references
3. Reports discrepancies (things in docs but not in TypeSpec)
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class TypeSpecParser:
    """Parse TypeSpec files to extract models, discriminators, enums."""

    def __init__(self, typespec_dir: str):
        self.typespec_dir = Path(typespec_dir)
        self.models: Dict[str, Dict] = {}
        self.discriminators: Dict[str, Set[str]] = defaultdict(set)
        self.enums: Dict[str, Set[str]] = defaultdict(set)
        self.all_properties: Set[str] = set()

    def parse(self):
        """Parse all TypeSpec files."""
        for tsp_file in self.typespec_dir.glob("**/*.tsp"):
            self._parse_file(tsp_file)

    def _parse_file(self, file_path: Path):
        """Parse a single TypeSpec file."""
        content = file_path.read_text()

        # Extract discriminated unions
        # Pattern: @discriminator("kind") union UnionName { ... }
        discriminator_pattern = r'@discriminator\("(\w+)"\)\s+union\s+(\w+)\s*\{'
        for match in re.finditer(discriminator_pattern, content):
            discriminator_field = match.group(1)
            union_name = match.group(2)
            # Extract member types
            union_start = match.end()
            union_end = self._find_closing_brace(content, union_start)
            union_body = content[union_start:union_end]
            members = re.findall(r'(\w+)(?:,|\s|$)', union_body)
            self.discriminators[union_name] = set(members)

        # Extract model definitions
        # Pattern: model ModelName { ... }
        model_pattern = r'model\s+(\w+)\s*\{'
        for match in re.finditer(model_pattern, content):
            model_name = match.group(1)
            model_start = match.end()
            model_end = self._find_closing_brace(content, model_start)
            model_body = content[model_start:model_end]

            # Extract discriminator value (kind: "value")
            kind_pattern = r'kind:\s*"(\w+)"'
            kind_match = re.search(kind_pattern, model_body)
            discriminator_value = kind_match.group(1) if kind_match else None

            # Extract properties
            prop_pattern = r'(\w+)(?:\?)?\s*:\s*([^;]+);'
            properties = {}
            for prop_match in re.finditer(prop_pattern, model_body):
                prop_name = prop_match.group(1)
                prop_type = prop_match.group(2).strip()
                properties[prop_name] = prop_type
                self.all_properties.add(prop_name)

            self.models[model_name] = {
                'discriminator_value': discriminator_value,
                'properties': properties,
                'file': str(file_path.relative_to(self.typespec_dir))
            }

        # Extract enums
        # Pattern: enum EnumName { ... }
        enum_pattern = r'enum\s+(\w+)\s*\{'
        for match in re.finditer(enum_pattern, content):
            enum_name = match.group(1)
            enum_start = match.end()
            enum_end = self._find_closing_brace(content, enum_start)
            enum_body = content[enum_start:enum_end]
            # Extract enum values
            enum_values = re.findall(r'(\w+)(?:,|\s|$)', enum_body)
            self.enums[enum_name] = set(enum_values)

    def _find_closing_brace(self, content: str, start: int) -> int:
        """Find matching closing brace."""
        depth = 1
        pos = start
        while depth > 0 and pos < len(content):
            if content[pos] == '{':
                depth += 1
            elif content[pos] == '}':
                depth -= 1
            pos += 1
        return pos

    def get_all_discriminator_values(self) -> Set[str]:
        """Get all valid discriminator values from TypeSpec."""
        values = set()
        for model_name, model_info in self.models.items():
            if model_info['discriminator_value']:
                values.add(model_info['discriminator_value'])
        return values

    def get_all_model_names(self) -> Set[str]:
        """Get all model names from TypeSpec."""
        return set(self.models.keys())


class DocumentationValidator:
    """Validate documentation against TypeSpec."""

    def __init__(self, typespec_parser: TypeSpecParser, docs_dirs: List[str]):
        self.typespec = typespec_parser
        self.docs_dirs = [Path(d) for d in docs_dirs]
        self.issues: List[Dict] = []

    def validate(self):
        """Run validation."""
        print("🔍 Validating documentation against TypeSpec...\n")

        # Get valid discriminator values from TypeSpec
        valid_discriminators = self.typespec.get_all_discriminator_values()
        print(f"✓ Found {len(valid_discriminators)} valid discriminator values in TypeSpec")
        print(f"  Examples: {', '.join(list(valid_discriminators)[:10])}\n")

        # Get all valid model names
        valid_models = self.typespec.get_all_model_names()
        print(f"✓ Found {len(valid_models)} model definitions in TypeSpec")
        print(f"  Examples: {', '.join(list(valid_models)[:10])}\n")

        # Known invalid discriminators (removed in Phase 1)
        invalid_discriminators = {
            'celExpression', 'powerFxExpression', 'CELExpression', 'PowerFxExpression',
        }

        # Known removed models/types
        removed_models = {
            'CELExpressionCondition', 'PowerFxExpressionCondition',
            'celExpression', 'powerFxExpression',
        }

        # Validate each documentation file
        for docs_dir in self.docs_dirs:
            for md_file in docs_dir.glob("**/*.md"):
                # Skip certain directories
                if any(skip in str(md_file) for skip in ['.workspace', 'design-docs']):
                    continue
                self._validate_file(md_file, valid_discriminators, invalid_discriminators,
                                  valid_models, removed_models)

        # Report issues
        self._report_issues()

    def _validate_file(self, file_path: Path, valid_discriminators: Set[str],
                      invalid_discriminators: Set[str], valid_models: Set[str],
                      removed_models: Set[str]):
        """Validate a single documentation file."""
        content = file_path.read_text()

        # 1. Check for invalid discriminator values in "kind": "value" patterns
        kind_pattern = r'"kind":\s*"(\w+)"'
        for match in re.finditer(kind_pattern, content):
            kind_value = match.group(1)
            line_num = content[:match.start()].count('\n') + 1

            # Check if it's a known invalid discriminator
            if kind_value in invalid_discriminators:
                self.issues.append({
                    'file': str(file_path),
                    'line': line_num,
                    'type': 'INVALID_DISCRIMINATOR',
                    'value': kind_value,
                    'pattern': match.group(0),
                    'severity': 'ERROR',
                    'message': f'Invalid discriminator "{kind_value}" - removed in Phase 1'
                })
            # Check if it's an unknown discriminator (not in TypeSpec)
            # Allow common values that might be in metadata or config
            elif kind_value not in valid_discriminators and kind_value not in [
                'all', 'threadIds', 'metadata', 'always', 'never', 'block', 'modify',
                'telemetry', 'sendMessage', 'remote', 'prompt'
            ]:
                # Skip if it's in a watchScope or similar config
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                line_content = content[line_start:line_end if line_end != -1 else len(content)]

                if 'watchScope' not in line_content and 'hookType' not in line_content:
                    self.issues.append({
                        'file': str(file_path),
                        'line': line_num,
                        'type': 'UNKNOWN_DISCRIMINATOR',
                        'value': kind_value,
                        'pattern': match.group(0),
                        'severity': 'WARNING',
                        'message': f'Unknown discriminator "{kind_value}" - not found in TypeSpec'
                    })

        # 2. Check for old "type": discriminator pattern (should be "kind":)
        type_discriminator_pattern = r'"type":\s*"(text|image|audio|video|event|toolCall|' \
                                     r'roles|content|mention|always|expression|webhook)"'
        for match in re.finditer(type_discriminator_pattern, content):
            type_value = match.group(1)
            line_num = content[:match.start()].count('\n') + 1

            self.issues.append({
                'file': str(file_path),
                'line': line_num,
                'type': 'WRONG_DISCRIMINATOR_FIELD',
                'value': type_value,
                'pattern': match.group(0),
                'severity': 'ERROR',
                'message': f'Should use "kind": "{type_value}" not "type": "{type_value}"'
            })

        # 3. Check for references to removed models/types
        for removed_type in removed_models:
            # Case-insensitive search
            pattern = re.compile(re.escape(removed_type), re.IGNORECASE)
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count('\n') + 1

                # Skip if it's in a comment explaining the removal
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                line_content = content[line_start:line_end if line_end != -1 else len(content)]

                # Skip if line contains words like "removed", "deprecated", "old", "was"
                if any(word in line_content.lower() for word in ['removed', 'deprecated', 'old', 'was', 'not', 'no longer']):
                    continue

                self.issues.append({
                    'file': str(file_path),
                    'line': line_num,
                    'type': 'REMOVED_TYPE_REFERENCE',
                    'value': removed_type,
                    'pattern': match.group(0),
                    'severity': 'WARNING',
                    'message': f'Reference to removed type "{removed_type}"'
                })

        # 4. Check for invalid model references (ModelName in docs but not in TypeSpec)
        # Look for patterns like: Model, ModelName, etc. in code blocks
        model_reference_pattern = r'(?:^|\s)([A-Z][a-zA-Z]+(?:Content|Condition|Config|Hook|Agent|Thread|Run|Message|Event))\b'
        for match in re.finditer(model_reference_pattern, content):
            model_ref = match.group(1)
            line_num = content[:match.start()].count('\n') + 1

            # Check if it's in TypeSpec
            if model_ref not in valid_models and model_ref not in ['AutoResponseConfig', 'ThreadWatch']:
                # Skip common words or if in explanatory text
                if model_ref in ['StartCondition', 'EndCondition', 'TestConfig', 'UserConfig']:
                    continue

                self.issues.append({
                    'file': str(file_path),
                    'line': line_num,
                    'type': 'UNDEFINED_MODEL_REFERENCE',
                    'value': model_ref,
                    'pattern': match.group(0),
                    'severity': 'INFO',
                    'message': f'Model "{model_ref}" referenced but not found in TypeSpec'
                })

        # 5. Check for snake_case where camelCase expected
        snake_case_pattern = r'"(\w+_\w+)":\s*'
        for match in re.finditer(snake_case_pattern, content):
            field_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1

            # Skip known valid snake_case fields
            if field_name in ['api_base', 'api_key', 'user_id', 'agent_id', 'thread_id',
                            'run_id', 'message_id', 'auto_responder_id', 'max_tokens']:
                continue

            # Convert to camelCase suggestion
            camel_case = ''.join(word.capitalize() if i > 0 else word
                               for i, word in enumerate(field_name.split('_')))

            self.issues.append({
                'file': str(file_path),
                'line': line_num,
                'type': 'NAMING_CONVENTION',
                'value': field_name,
                'pattern': match.group(0),
                'severity': 'INFO',
                'message': f'Field uses snake_case "{field_name}" - should be camelCase "{camel_case}"?'
            })

    def _report_issues(self):
        """Report validation issues."""
        if not self.issues:
            print("✅ No issues found! Documentation matches TypeSpec.\n")
            return

        # Group by severity
        errors = [i for i in self.issues if i['severity'] == 'ERROR']
        warnings = [i for i in self.issues if i['severity'] == 'WARNING']
        info = [i for i in self.issues if i['severity'] == 'INFO']

        print(f"❌ Found {len(errors)} errors, {len(warnings)} warnings, and {len(info)} info items:\n")

        # Report errors
        if errors:
            print("ERRORS:")
            print("=" * 80)
            for issue in errors[:20]:  # Limit output
                print(f"\n{issue['file']}:{issue['line']}")
                print(f"  {issue['type']}: {issue['message']}")
                print(f"  Found: {issue['pattern']}")
                if issue['type'] == 'WRONG_DISCRIMINATOR_FIELD':
                    print(f"  Fix: Change to \"kind\": \"{issue['value']}\"")
                elif issue['type'] == 'INVALID_DISCRIMINATOR':
                    print(f"  Fix: Change to \"kind\": \"expression\"")
            if len(errors) > 20:
                print(f"\n  ... and {len(errors) - 20} more errors")
            print()

        # Report warnings
        if warnings:
            print("\nWARNINGS:")
            print("=" * 80)
            for issue in warnings[:10]:  # Limit output
                print(f"\n{issue['file']}:{issue['line']}")
                print(f"  {issue['type']}: {issue['message']}")
                print(f"  Found: {issue['pattern']}")
            if len(warnings) > 10:
                print(f"\n  ... and {len(warnings) - 10} more warnings")
            print()

        # Report info (only summary)
        if info:
            print(f"\nINFO: {len(info)} informational items (run with --verbose to see details)")

        # Summary by file
        print("\nSUMMARY BY FILE:")
        print("=" * 80)
        files_with_issues = defaultdict(lambda: {'ERROR': 0, 'WARNING': 0, 'INFO': 0})
        for issue in self.issues:
            files_with_issues[issue['file']][issue['severity']] += 1

        for file_path, counts in sorted(files_with_issues.items(),
                                       key=lambda x: (x[1]['ERROR'], x[1]['WARNING']),
                                       reverse=True):
            total = sum(counts.values())
            details = f"E:{counts['ERROR']} W:{counts['WARNING']} I:{counts['INFO']}"
            print(f"{total:3d} issues ({details}): {file_path}")


def main():
    """Main entry point."""
    # Paths
    project_root = Path(__file__).parent.parent
    typespec_dir = project_root / "typespec"
    docs_dirs = [
        project_root / "api-reference",
        project_root / "guides",
    ]

    # Parse TypeSpec
    print("📖 Parsing TypeSpec files...")
    parser = TypeSpecParser(str(typespec_dir))
    parser.parse()
    print(f"✓ Parsed {len(parser.models)} models, {len(parser.discriminators)} unions, {len(parser.enums)} enums\n")

    # Validate documentation
    validator = DocumentationValidator(parser, [str(d) for d in docs_dirs])
    validator.validate()

    # Exit code
    errors = [i for i in validator.issues if i['severity'] == 'ERROR']
    if errors:
        print(f"\n❌ Validation failed with {len(errors)} errors")
        exit(1)
    else:
        print("\n✅ Validation passed (warnings/info items don't fail the build)")
        exit(0)


if __name__ == "__main__":
    main()
