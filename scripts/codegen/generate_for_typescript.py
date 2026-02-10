#!/usr/bin/env python3
"""
Generate TypeScript types for the TypeScript packages directory.

This script:
1. Runs standard TypeScript generation
2. Copies generated files to TypeScript package structure
3. Updates index.ts exports
"""

import shutil
import subprocess
import sys
from pathlib import Path


def generate_for_typescript():
    """Generate and setup TypeScript types for packages."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent

    typespec_dir = repo_root / "typespec"
    ts_output = repo_root / "typescript" / "packages" / "agents" / "src" / "generated"
    js_output = repo_root / "javascript" / "packages" / "agents" / "src" / "generated"

    print("╔" + "=" * 56 + "╗")
    print("║     TypeScript Type Generation (for TS packages)      ║")
    print("╚" + "=" * 56 + "╝")
    print()

    # First run the standard generation
    print("Running standard TypeScript generation...")
    try:
        subprocess.run(
            [sys.executable, str(script_dir / "generate_sdk.py"), "--lang", "typescript"],
            check=True
        )
    except subprocess.CalledProcessError:
        print("\n❌ Error: TypeScript generation failed")
        sys.exit(1)

    # Copy generated files to TypeScript packages
    print("\nCopying generated types to TypeScript packages...")

    # Clean and recreate output
    if ts_output.exists():
        shutil.rmtree(ts_output)
    ts_output.mkdir(parents=True, exist_ok=True)

    # Copy from JS output if it exists
    if js_output.exists():
        for item in js_output.iterdir():
            if item.is_file():
                shutil.copy2(item, ts_output)
            elif item.is_dir():
                shutil.copytree(item, ts_output / item.name, dirs_exist_ok=True)

    # Update index.ts to export generated types
    print("Updating TypeScript package index...")

    index_content = '''/**
 * Microsoft Agents - Core TypeScript Types
 *
 * This package provides TypeScript types generated from TypeSpec definitions
 * for the Microsoft Agents Protocol.
 *
 * @packageDocumentation
 */

// Generated types
export * from './generated/messages';
export * from './generated/threads';
export * from './generated/execution';
export * from './generated/tools';
export * from './generated/agents';
export * from './generated/streaming';
export * from './generated/subscriptions';
export * from './generated/common';

// Utility functions
export * from './utilities';
'''

    index_path = repo_root / "typescript" / "packages" / "agents" / "src" / "index.ts"
    index_path.write_text(index_content)

    print()
    print("╔" + "=" * 56 + "╗")
    print("║   ✅ TypeScript types generated successfully!         ║")
    print("╚" + "=" * 56 + "╝")
    print()
    print(f"Output directory: {ts_output}")
    print()


if __name__ == "__main__":
    generate_for_typescript()
