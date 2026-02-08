#!/usr/bin/env python3
"""
Enum Synchronization Validator

Extracts enums from TypeSpec files and compares them with documentation.
Ensures enum values are consistent across all files.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

# Colors for output
try:
    from colorama import init, Fore, Style
    init()
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    RESET = Style.RESET_ALL
except ImportError:
    RED = GREEN = YELLOW = BLUE = RESET = ""


@dataclass
class EnumDefinition:
    name: str
    values: List[str]
    file: str
    line_start: int


def find_project_root() -> Path:
    """Find the AgentProtocol project root."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "typespec").exists() and (current / "docs").exists():
            return current
        current = current.parent
    raise RuntimeError("docs/specifications/ directories)")


def extract_typespec_enums(typespec_dir: Path) -> Dict[str, EnumDefinition]:
    """Extract all enum definitions from TypeSpec files."""
    enums = {}

    for tsp_file in typespec_dir.glob("*.tsp"):
        content = tsp_file.read_text()
        lines = content.split('\n')

        # Pattern: enum EnumName {
        enum_pattern = re.compile(r'^\s*enum\s+(\w+)\s*\{')

        i = 0
        while i < len(lines):
            match = enum_pattern.match(lines[i])
            if match:
                enum_name = match.group(1)
                line_start = i + 1
                values = []

                # Extract enum values until closing brace
                i += 1
                while i < len(lines) and '}' not in lines[i]:
                    # Look for value definitions (ignoring comments)
                    value_match = re.match(r'^\s*(\w+)\s*[,]?\s*(?://.*)?$', lines[i])
                    if value_match:
                        values.append(value_match.group(1))
                    i += 1

                enums[enum_name] = EnumDefinition(
                    name=enum_name,
                    values=values,
                    file=str(tsp_file.relative_to(tsp_file.parent.parent)),
                    line_start=line_start
                )
            i += 1

    return enums


# Words/patterns that should be excluded from enum value extraction
EXCLUDED_WORDS = {
    # Table headers and common field names
    'Value', 'Status', 'Role', 'Field', 'Type', 'Name', 'Description',
    'Parameter', 'Required', 'Default', 'Example', 'Operation', 'Aspect',
    # Model field names commonly appearing in tables
    'threadId', 'channelId', 'userId', 'agentId', 'metadata', 'timestamp',
    'createdAt', 'updatedAt', 'lastActivityAt', 'lastMessageAt',
    'additionalInstructions', 'instructions', 'model', 'temperature',
    'messages', 'content', 'participants', 'unreadCount', 'channelInfo',
    'displayName', 'description', 'kind', 'template', 'serviceUrl',
    'inputSchema', 'outputSchema', 'externalConversationId', 'externalTenantId',
    # Security/encryption fields
    'encryption', 'algorithm', 'keyId', 'iv', 'authTag', 'priority', 'lastModified',
    # Pagination/filtering
    'after', 'before', 'limit', 'order', 'filter',
    # API-related terms
    'Webhook', 'Cancel', 'Messages', 'Citations', 'Output', 'Session',
    'Provider', 'Capabilities', 'AgentRunResult', 'AgentsClient', 'Thinking',
    'auto_execute_tools',
    # Table separator patterns
    '-', '--', '---', '----', '-----'
}


def extract_markdown_enum_references(md_file: Path) -> Dict[str, List[str]]:
    """Extract enum value lists from markdown documentation."""
    content = md_file.read_text()
    enum_refs = {}

    # Pattern 1: Markdown tables with enum values
    # Looking for patterns like:
    # | queued | Description |
    # | in_progress | Description |

    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect enum-like tables (look for known enum contexts)
        # Must be in a header or immediately preceding a table
        if any(keyword in line.lower() for keyword in ['runstatus', 'run status', 'threadstatus', 'thread status', 'chatrole', 'chat role']):
            # Try to determine enum name
            enum_name = None
            if 'runstatus' in line.lower() or 'run status' in line.lower():
                enum_name = 'RunStatus'
            elif 'threadstatus' in line.lower() or 'thread status' in line.lower():
                enum_name = 'ThreadStatus'
            elif 'chatrole' in line.lower() or 'chat role' in line.lower():
                enum_name = 'ChatRole'

            if enum_name:
                values = []
                # Look ahead for table rows
                j = i + 1
                in_table = False
                while j < len(lines) and j < i + 50:  # Look at next 50 lines max
                    current_line = lines[j].strip()

                    # Start of table (header separator)
                    if current_line.startswith('|') and '-' in current_line:
                        in_table = True
                        j += 1
                        continue

                    # End of table (empty line or non-table line after table started)
                    if in_table and (not current_line or not current_line.startswith('|')):
                        break

                    # Extract value from table row (only if in table)
                    if in_table and current_line.startswith('|'):
                        table_row_match = re.match(r'^\|\s*`?(\w+)`?\s*\|', current_line)
                        if table_row_match:
                            value = table_row_match.group(1)
                            # Skip excluded words and patterns
                            if value not in EXCLUDED_WORDS and not set(value) == {'-'}:
                                # Additional validation: enum values are typically lowercase with underscores
                                # or camelCase, but not PascalCase field names
                                if ('_' in value or value.islower() or
                                    (value[0].islower() and any(c.isupper() for c in value[1:]))):
                                    values.append(value)
                    j += 1

                if values:
                    enum_refs[enum_name] = values

        # Pattern 2: Code blocks with enum definitions
        if '```typescript' in line or '```typespec' in line or ('```' in line and i + 1 < len(lines) and 'enum' in lines[i+1]):
            # Look for enum definitions in code blocks
            j = i + 1
            code_block = []
            while j < len(lines) and '```' not in lines[j]:
                code_block.append(lines[j])
                j += 1

            code_text = '\n'.join(code_block)
            enum_pattern = re.compile(r'enum\s+(\w+)\s*\{([^}]+)\}', re.DOTALL)
            for match in enum_pattern.finditer(code_text):
                enum_name = match.group(1)
                enum_body = match.group(2)
                # More careful extraction of enum values
                values = []
                for line in enum_body.split('\n'):
                    # Match enum value lines (exclude comments and empty lines)
                    value_match = re.match(r'^\s*(\w+)\s*[,]?\s*(?://.*)?$', line.strip())
                    if value_match:
                        value = value_match.group(1)
                        if value not in EXCLUDED_WORDS:
                            values.append(value)
                if values:
                    enum_refs[enum_name] = values

        i += 1

    return enum_refs


def compare_enums(typespec_enums: Dict[str, EnumDefinition],
                  doc_enums: Dict[str, List[str]],
                  doc_file: str) -> List[str]:
    """Compare enum definitions and return list of issues."""
    issues = []

    for enum_name, ts_enum in typespec_enums.items():
        if enum_name in doc_enums:
            doc_values = doc_enums[enum_name]
            ts_values = ts_enum.values

            # Check for missing values
            missing_in_doc = set(ts_values) - set(doc_values)
            extra_in_doc = set(doc_values) - set(ts_values)

            if missing_in_doc:
                issues.append(
                    f"{doc_file}: {enum_name} missing values: {', '.join(sorted(missing_in_doc))}"
                )

            if extra_in_doc:
                issues.append(
                    f"{doc_file}: {enum_name} has extra values not in TypeSpec: {', '.join(sorted(extra_in_doc))}"
                )

            # Check order (warning only)
            if doc_values != ts_values and not (missing_in_doc or extra_in_doc):
                issues.append(
                    f"{doc_file}: {enum_name} values in different order (warning)"
                )

    return issues


def main():
    """Main validation function."""
    print(f"{BLUE}╔═══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║     Enum Synchronization Validator                       ║{RESET}")
    print(f"{BLUE}╚═══════════════════════════════════════════════════════════╝{RESET}\n")

    try:
        project_root = find_project_root()
        print(f"Project root: {project_root}\n")
    except RuntimeError as e:
        print(f"{RED}Error: {e}{RESET}")
        return 1

    # Extract TypeSpec enums
    typespec_dir = project_root / "typespec"
    print(f"{BLUE}[1/3] Extracting enums from TypeSpec files...{RESET}")
    typespec_enums = extract_typespec_enums(typespec_dir)

    print(f"Found {len(typespec_enums)} enums in TypeSpec:")
    for enum_name, enum_def in typespec_enums.items():
        print(f"  • {enum_name}: {len(enum_def.values)} values ({enum_def.file})")
    print()

    # Check documentation files
    print(f"{BLUE}[2/3] Checking documentation files...{RESET}")
    all_issues = []

    # Check specifications
    specs_dir = project_root / "specifications"
    api_ref_dir = project_root / "api-reference"

    for doc_dir in [specs_dir, api_ref_dir]:
        if not doc_dir.exists():
            continue

        for md_file in doc_dir.glob("*.md"):
            doc_enums = extract_markdown_enum_references(md_file)

            if doc_enums:
                rel_path = str(md_file.relative_to(project_root))
                print(f"  Checking {rel_path}...")
                issues = compare_enums(typespec_enums, doc_enums, rel_path)
                all_issues.extend(issues)

    # Report results
    print(f"\n{BLUE}[3/3] Results{RESET}")
    print("=" * 60)

    if not all_issues:
        print(f"{GREEN}✓ All enums are synchronized!{RESET}")
        return 0
    else:
        print(f"{RED}✗ Found {len(all_issues)} synchronization issues:{RESET}\n")
        for issue in all_issues:
            if "warning" in issue.lower():
                print(f"{YELLOW}  ⚠ {issue}{RESET}")
            else:
                print(f"{RED}  ✗ {issue}{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
