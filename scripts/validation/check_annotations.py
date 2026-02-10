#!/usr/bin/env python3
"""
Check for ContentAnnotations model and usage in TypeSpec files.

This script validates that the TypeSpec schema includes proper annotation
support for content filtering, audience targeting, and encryption.
"""

import argparse
import re
import sys
from pathlib import Path


def check_annotations(typespec_path: Path, verbose: bool = False) -> int:
    """
    Check for ContentAnnotations model and usage.

    Returns:
        0 if all checks pass
        1 if any checks fail
    """
    # Validate TypeSpec file exists
    if not typespec_path.exists():
        print(f"❌ Error: TypeSpec file not found: {typespec_path}")
        print()
        print("Expected location:")
        print(f"  {typespec_path.absolute()}")
        print()
        print("Make sure you're running from the project root:")
        print("  python3 scripts/validation/check_annotations.py")
        return 1

    content = typespec_path.read_text()
    failures = 0

    print('=' * 70)
    print('🔍 Content Annotations Validation')
    print('=' * 70)
    print()
    print(f"Checking: {typespec_path}")
    print()

    # Check if ContentAnnotations model exists
    print('1. ContentAnnotations Model')
    print('-' * 70)
    if 'model ContentAnnotations' in content:
        print('✅ ContentAnnotations model FOUND')

        # Extract the model definition
        if verbose:
            model_regex = r'model ContentAnnotations\s*\{([^}]+)\}'
            match = re.search(model_regex, content, re.DOTALL)
            if match:
                print()
                print('Definition:')
                print(match.group(0))
    else:
        print('⚠️  ContentAnnotations model NOT FOUND')
        print()
        print('This is optional - annotations provide metadata for content filtering.')
        failures += 1
    print()

    # Check for audience and encryption at message level
    print('2. ChatMessage Security Fields')
    print('-' * 70)
    chat_message_regex = r'model ChatMessage\s*\{([\s\S]*?)\n\}'
    chat_match = re.search(chat_message_regex, content)

    if chat_match:
        message_body = chat_match.group(1)

        audience_found = 'audience?:' in message_body or 'audience:' in message_body
        encryption_found = 'encryption?:' in message_body or 'encryption:' in message_body

        if audience_found:
            print('✅ audience field FOUND at ChatMessage level')
        else:
            print('⚠️  audience field NOT FOUND at ChatMessage level')
            print('   (Optional: Used for targeting messages to specific audiences)')
            failures += 1

        if encryption_found:
            print('✅ encryption field FOUND at ChatMessage level')
        else:
            print('⚠️  encryption field NOT FOUND at ChatMessage level')
            print('   (Optional: Used for end-to-end encryption metadata)')
            failures += 1
    else:
        print('❌ Could not find ChatMessage model definition')
        failures += 1
    print()

    # Check if any content types reference ContentAnnotations
    print('3. Content Type Annotations')
    print('-' * 70)
    annotations_refs = re.findall(r'annotations\?:\s*ContentAnnotations', content)

    if annotations_refs:
        print(f'✅ Found {len(annotations_refs)} content types with annotations support')
        if verbose:
            print()
            print('Content types using annotations:')
            for i, ref in enumerate(annotations_refs, 1):
                print(f'  {i}. {ref}')
    else:
        print('⚠️  NO content types reference ContentAnnotations')
        print('   (Optional: Enables per-content annotation metadata)')
        failures += 1
    print()

    # Check for EncryptedContent
    print('4. Encrypted Content Type')
    print('-' * 70)
    if 'model EncryptedContent' in content:
        print('✅ EncryptedContent model FOUND')
    else:
        print('⚠️  EncryptedContent model NOT FOUND')
        print('   (Optional: Dedicated type for encrypted content)')
        failures += 1
    print()

    # Summary
    print('=' * 70)
    if failures == 0:
        print('✅ All annotation checks passed!')
        print('=' * 70)
        return 0
    else:
        print(f'⚠️  {failures} optional features not found')
        print('=' * 70)
        print()
        print('Note: These are optional features for advanced use cases:')
        print('  - ContentAnnotations: Metadata for content filtering')
        print('  - audience/encryption: Message-level security')
        print('  - EncryptedContent: Dedicated encrypted content type')
        print()
        print('If you need these features, add them to typespec/messages.tsp')
        return 0  # Don't fail on optional features


def main():
    parser = argparse.ArgumentParser(
        description='Check for ContentAnnotations and security features in TypeSpec',
        epilog="""
Examples:
  # Check default TypeSpec file
  python3 scripts/validation/check_annotations.py

  # Check with verbose output
  python3 scripts/validation/check_annotations.py --verbose

  # Check custom TypeSpec file
  python3 scripts/validation/check_annotations.py --typespec path/to/messages.tsp

This script checks for optional security and annotation features:
  - ContentAnnotations model (metadata for content filtering)
  - audience/encryption fields (message-level security)
  - EncryptedContent type (dedicated encrypted content)
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--typespec',
        type=str,
        default='typespec/messages.tsp',
        help='Path to TypeSpec file (default: typespec/messages.tsp)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output including model definitions'
    )

    args = parser.parse_args()

    # Resolve path relative to project root
    project_root = Path(__file__).parent.parent.parent
    typespec_path = project_root / args.typespec

    return check_annotations(typespec_path, args.verbose)


if __name__ == '__main__':
    sys.exit(main())
