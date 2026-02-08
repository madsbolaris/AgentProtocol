#!/usr/bin/env python3
"""
Validate that echo bot samples haven't changed from their baseline.

This script ensures that echo bot samples stay true to their original M365 SDK implementation,
with only the minimal changes needed for Agent Protocol support.

Usage:
    # Check if echo bots match their snapshots
    python scripts/validate-echo-bots.py

    # Update snapshots (only run this when intentionally changing echo bots)
    python scripts/validate-echo-bots.py --update
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List

# Files to track for each echo bot
TRACKED_FILES = {
    "python": [
        "python/samples/agents/echo-bot/src/agent.py",
        "python/samples/agents/echo-bot/src/start_server.py",
        "python/samples/agents/echo-bot/src/main.py",
        "python/samples/agents/echo-bot/requirements.txt",
    ],
    "dotnet": [
        "dotnet/samples/agents/EchoBot/MyAgent.cs",
        "dotnet/samples/agents/EchoBot/Program.cs",
        "dotnet/samples/agents/EchoBot/QuickStart.csproj",
    ],
    "typescript": [
        "typescript/samples/echo-bot/src/agent.ts",
        "typescript/samples/echo-bot/src/index.ts",
        "typescript/samples/echo-bot/package.json",
    ],
}

SNAPSHOT_FILE = Path(__file__).parent / "echo-bot-snapshots.json"


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    if not file_path.exists():
        return "FILE_NOT_FOUND"

    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_snapshots(repo_root: Path) -> Dict[str, Dict[str, str]]:
    """Compute hashes for all tracked files."""
    snapshots = {}

    for lang, files in TRACKED_FILES.items():
        snapshots[lang] = {}
        for file_path in files:
            full_path = repo_root / file_path
            file_hash = compute_file_hash(full_path)
            snapshots[lang][file_path] = file_hash

    return snapshots


def load_snapshots() -> Dict[str, Dict[str, str]]:
    """Load snapshots from file."""
    if not SNAPSHOT_FILE.exists():
        return {}

    with open(SNAPSHOT_FILE, "r") as f:
        return json.load(f)


def save_snapshots(snapshots: Dict[str, Dict[str, str]]) -> None:
    """Save snapshots to file."""
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshots, f, indent=2, sort_keys=True)
        f.write("\n")


def validate_snapshots(current: Dict[str, Dict[str, str]], baseline: Dict[str, Dict[str, str]]) -> List[str]:
    """Validate current snapshots against baseline. Returns list of errors."""
    errors = []

    for lang, files in current.items():
        if lang not in baseline:
            errors.append(f"❌ {lang}: No baseline found (new language?)")
            continue

        for file_path, current_hash in files.items():
            baseline_hash = baseline[lang].get(file_path)

            if baseline_hash is None:
                errors.append(f"❌ {lang}: {file_path} - New file not in baseline")
            elif current_hash == "FILE_NOT_FOUND":
                errors.append(f"❌ {lang}: {file_path} - File not found")
            elif current_hash != baseline_hash:
                errors.append(f"❌ {lang}: {file_path} - Content changed")
                errors.append(f"   Expected: {baseline_hash}")
                errors.append(f"   Got:      {current_hash}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate echo bot samples")
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update snapshots instead of validating"
    )
    args = parser.parse_args()

    # Find repository root
    repo_root = Path(__file__).parent.parent

    print("🔍 Validating echo bot samples...")
    print(f"   Repository: {repo_root}")
    print(f"   Snapshots:  {SNAPSHOT_FILE}")
    print()

    # Compute current snapshots
    current_snapshots = compute_snapshots(repo_root)

    if args.update:
        # Update mode: save new snapshots
        save_snapshots(current_snapshots)
        print("✅ Snapshots updated successfully!")
        print()
        print("⚠️  WARNING: Only update snapshots when intentionally changing echo bots.")
        print("   Commit the updated echo-bot-snapshots.json file.")
        return 0

    # Validate mode: compare against baseline
    baseline_snapshots = load_snapshots()

    if not baseline_snapshots:
        print("❌ No baseline snapshots found!")
        print("   Run with --update to create initial snapshots.")
        return 1

    errors = validate_snapshots(current_snapshots, baseline_snapshots)

    if errors:
        print("❌ Echo bot validation FAILED!")
        print()
        for error in errors:
            print(error)
        print()
        print("Echo bots have changed from their baseline. This is not allowed!")
        print()
        print("If you intentionally changed the echo bots:")
        print("  1. Ensure changes are minimal and justified")
        print("  2. Run: python scripts/validate-echo-bots.py --update")
        print("  3. Commit the updated snapshots")
        return 1

    print("✅ All echo bot samples are valid!")
    print()
    print("Validated files:")
    for lang, files in TRACKED_FILES.items():
        print(f"  {lang}:")
        for file_path in files:
            print(f"    ✓ {file_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
