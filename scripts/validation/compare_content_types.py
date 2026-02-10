#!/usr/bin/env python3
"""
Compare content types in TypeSpec vs Documentation.
"""

import argparse
import json
import re
from pathlib import Path


def compare_content_types():
    """Compare content types between TypeSpec and docs."""
    script_dir = Path(__file__).parent

    # Read current TypeSpec types
    tsp_types_path = script_dir.parent / ".workspace" / "content-types-current.txt"
    tsp_types = set(
        line.strip()
        for line in tsp_types_path.read_text().split('\n')
        if line.strip()
    )

    # Read content-types.md
    docs_path = script_dir.parent.parent / "api-reference" / "content-types.md"
    docs_content = docs_path.read_text()

    # Extract types mentioned in docs (look for **TypeName** patterns)
    doc_types = set(re.findall(r'\*\*(\w+Content)\*\*', docs_content))

    print(f'TypeSpec Types: {len(tsp_types)}')
    print(f'Documented Types: {len(doc_types)}')
    print()

    # Find differences
    in_tsp_not_in_docs = sorted(tsp_types - doc_types)
    in_docs_not_in_tsp = sorted(doc_types - tsp_types)

    if in_tsp_not_in_docs:
        print('❌ In TypeSpec but NOT in docs:')
        for t in in_tsp_not_in_docs:
            print(f'  - {t}')
        print()

    if in_docs_not_in_tsp:
        print('❌ In docs but NOT in TypeSpec:')
        for t in in_docs_not_in_tsp:
            print(f'  - {t}')
        print()

    if not in_tsp_not_in_docs and not in_docs_not_in_tsp:
        print('✅ All types match!')

    # Write report
    report = {
        'tspCount': len(tsp_types),
        'docCount': len(doc_types),
        'inTspNotInDocs': in_tsp_not_in_docs,
        'inDocsNotInTsp': in_docs_not_in_tsp,
        'tspTypes': sorted(tsp_types),
        'docTypes': sorted(doc_types)
    }

    report_path = script_dir.parent / ".workspace" / "content-type-comparison.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f'\nReport written to: {report_path}')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare content types between TypeSpec and documentation"
    )
    parser.parse_args()
    compare_content_types()


if __name__ == '__main__':
    main()
