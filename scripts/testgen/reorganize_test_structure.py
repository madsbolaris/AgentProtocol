#!/usr/bin/env python3
"""
Reorganize test-data directory structure to match input hierarchy.

This script:
1. Maps normalized files to their source input files
2. Reorganizes normalized/ to match input/ structure
3. Reorganizes results/ to match input/ structure
4. Moves normalized/ into results/normalized/
"""

import argparse
import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Base paths
TEST_DATA = Path("/Users/mabolan/AgentProtocol/test-data")
INPUT_DIR = TEST_DATA / "input"
NORMALIZED_DIR = TEST_DATA / "normalized"
RESULTS_DIR = TEST_DATA / "results"
NEW_NORMALIZED_DIR = RESULTS_DIR / "normalized"


def find_input_file(filename: str, search_roots: List[Path]) -> Path | None:
    """Find the input file matching the given filename in the input directory."""
    for root in search_roots:
        for input_file in root.rglob(filename):
            return input_file
    return None


def get_relative_path(input_file: Path, base: Path) -> Path:
    """Get relative path from base directory (e.g., input/evals or input/threads)."""
    try:
        return input_file.relative_to(base)
    except ValueError:
        return None


def reorganize_normalized_files():
    """Reorganize normalized files to match input structure."""
    print("=" * 80)
    print("TASK 1: Reorganizing normalized/ to match input/ structure")
    print("=" * 80)

    # Get all normalized files (they're currently flat)
    normalized_files = list(NORMALIZED_DIR.glob("*.xml"))
    print(f"\nFound {len(normalized_files)} normalized files to reorganize")

    # Track statistics
    moved = 0
    not_found = 0
    errors = []

    # Search roots in input directory
    search_roots = [INPUT_DIR / "evals", INPUT_DIR / "threads"]

    for norm_file in normalized_files:
        filename = norm_file.name

        # Find corresponding input file
        input_file = find_input_file(filename, search_roots)

        if not input_file:
            print(f"  WARNING: No input file found for {filename}")
            not_found += 1
            continue

        # Determine which category (evals or threads)
        if "evals" in input_file.parts:
            base = INPUT_DIR / "evals"
            category = "evals"
        else:
            base = INPUT_DIR / "threads"
            category = "threads"

        # Get relative path from category base
        rel_path = get_relative_path(input_file, base)
        if not rel_path:
            print(f"  ERROR: Could not determine relative path for {filename}")
            errors.append(filename)
            continue

        # Create new path in normalized directory
        new_path = NORMALIZED_DIR / category / rel_path.parent / filename

        # Create parent directory
        new_path.parent.mkdir(parents=True, exist_ok=True)

        # Move file
        try:
            shutil.move(str(norm_file), str(new_path))
            print(f"  ✓ {filename} -> {category}/{rel_path.parent}")
            moved += 1
        except Exception as e:
            print(f"  ERROR: Failed to move {filename}: {e}")
            errors.append(filename)

    print(f"\nSummary:")
    print(f"  Moved: {moved}")
    print(f"  Not found: {not_found}")
    print(f"  Errors: {len(errors)}")
    if errors:
        print(f"  Error files: {', '.join(errors)}")


def reorganize_result_files():
    """Reorganize result files to match input structure."""
    print("\n" + "=" * 80)
    print("TASK 2: Reorganizing results/ to match input/ structure")
    print("=" * 80)

    # Get all result JSON files (currently in results/evals/json/)
    result_files = list((RESULTS_DIR / "evals" / "json").glob("*.json"))
    print(f"\nFound {len(result_files)} result files to reorganize")

    # Track statistics
    moved = 0
    not_found = 0
    errors = []

    # Search roots in input directory
    search_roots = [INPUT_DIR / "evals", INPUT_DIR / "threads"]

    for result_file in result_files:
        # Extract base filename (remove -result.json suffix)
        filename = result_file.name.replace("-result.json", ".xml")

        # Find corresponding input file
        input_file = find_input_file(filename, search_roots)

        if not input_file:
            print(f"  WARNING: No input file found for {filename}")
            not_found += 1
            continue

        # Determine which category (evals or threads)
        if "evals" in input_file.parts:
            base = INPUT_DIR / "evals"
            category = "evals"
        else:
            base = INPUT_DIR / "threads"
            category = "threads"

        # Get relative path from category base
        rel_path = get_relative_path(input_file, base)
        if not rel_path:
            print(f"  ERROR: Could not determine relative path for {filename}")
            errors.append(result_file.name)
            continue

        # Create new path in results directory (keep -result.json suffix)
        result_filename = input_file.stem + "-result.json"
        new_path = RESULTS_DIR / category / rel_path.parent / result_filename

        # Create parent directory
        new_path.parent.mkdir(parents=True, exist_ok=True)

        # Move file
        try:
            shutil.move(str(result_file), str(new_path))
            print(f"  ✓ {result_file.name} -> {category}/{rel_path.parent}")
            moved += 1
        except Exception as e:
            print(f"  ERROR: Failed to move {result_file.name}: {e}")
            errors.append(result_file.name)

    print(f"\nSummary:")
    print(f"  Moved: {moved}")
    print(f"  Not found: {not_found}")
    print(f"  Errors: {len(errors)}")
    if errors:
        print(f"  Error files: {', '.join(errors)}")

    # Clean up empty json directory
    json_dir = RESULTS_DIR / "evals" / "json"
    if json_dir.exists() and not any(json_dir.iterdir()):
        json_dir.rmdir()
        print(f"\n  Removed empty directory: {json_dir}")


def move_normalized_into_results():
    """Move normalized/ into results/normalized/."""
    print("\n" + "=" * 80)
    print("TASK 3: Moving normalized/ into results/normalized/")
    print("=" * 80)

    if not NORMALIZED_DIR.exists():
        print(f"  ERROR: {NORMALIZED_DIR} does not exist!")
        return

    if NEW_NORMALIZED_DIR.exists():
        print(f"  WARNING: {NEW_NORMALIZED_DIR} already exists!")
        response = input("  Do you want to remove it and continue? (yes/no): ")
        if response.lower() != "yes":
            print("  Aborting...")
            return
        shutil.rmtree(NEW_NORMALIZED_DIR)

    try:
        shutil.move(str(NORMALIZED_DIR), str(NEW_NORMALIZED_DIR))
        print(f"  ✓ Moved {NORMALIZED_DIR} to {NEW_NORMALIZED_DIR}")
    except Exception as e:
        print(f"  ERROR: Failed to move normalized directory: {e}")


def verify_structure():
    """Verify the final structure is correct."""
    print("\n" + "=" * 80)
    print("TASK 5: Verification")
    print("=" * 80)

    # Count files in each directory
    input_files = list(INPUT_DIR.rglob("*.xml"))
    normalized_files = list(NEW_NORMALIZED_DIR.rglob("*.xml")) if NEW_NORMALIZED_DIR.exists() else []
    result_files = list(RESULTS_DIR.rglob("*-result.json"))

    print(f"\nFile counts:")
    print(f"  Input files: {len(input_files)}")
    print(f"  Normalized files: {len(normalized_files)}")
    print(f"  Result files: {len(result_files)}")

    # Check directory structure matches
    print(f"\nDirectory structure check:")

    # Get unique subdirectories for each
    input_dirs = set()
    for f in input_files:
        if "evals" in f.parts:
            rel = f.relative_to(INPUT_DIR / "evals")
        elif "threads" in f.parts:
            rel = f.relative_to(INPUT_DIR / "threads")
        else:
            continue
        if rel.parent != Path("."):
            input_dirs.add(rel.parent)

    normalized_dirs = set()
    for f in normalized_files:
        if "evals" in f.parts:
            rel = f.relative_to(NEW_NORMALIZED_DIR / "evals")
        elif "threads" in f.parts:
            rel = f.relative_to(NEW_NORMALIZED_DIR / "threads")
        else:
            continue
        if rel.parent != Path("."):
            normalized_dirs.add(rel.parent)

    result_dirs = set()
    for f in result_files:
        if "evals" in f.parts:
            # Skip normalized subdirectory
            if "normalized" in f.parts:
                continue
            rel = f.relative_to(RESULTS_DIR / "evals")
        elif "threads" in f.parts:
            if "normalized" in f.parts:
                continue
            rel = f.relative_to(RESULTS_DIR / "threads")
        else:
            continue
        if rel.parent != Path("."):
            result_dirs.add(rel.parent)

    print(f"  Input unique subdirs: {len(input_dirs)}")
    print(f"  Normalized unique subdirs: {len(normalized_dirs)}")
    print(f"  Result unique subdirs: {len(result_dirs)}")

    # Check if structures match
    if normalized_files:
        if normalized_dirs == input_dirs:
            print("  ✓ Normalized structure matches input structure")
        else:
            print("  ✗ Normalized structure does NOT match input structure")
            missing = input_dirs - normalized_dirs
            if missing:
                print(f"    Missing in normalized: {missing}")

    if result_files:
        if result_dirs.issubset(input_dirs):
            print("  ✓ Result structure matches input structure")
        else:
            print("  ✗ Result structure does NOT match input structure")
            missing = result_dirs - input_dirs
            if missing:
                print(f"    Extra in results: {missing}")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Reorganize test data directory structure"
    )
    parser.parse_args()

    print("Test Data Directory Reorganization")
    print("=" * 80)
    print(f"Base directory: {TEST_DATA}")
    print()

    # Confirm before proceeding
    print("This script will:")
    print("  1. Reorganize normalized/ to match input/ structure")
    print("  2. Reorganize results/ to match input/ structure")
    print("  3. Move normalized/ into results/normalized/")
    print()

    response = input("Do you want to proceed? (yes/no): ")
    if response.lower() != "yes":
        print("Aborting...")
        return

    # Execute tasks
    reorganize_normalized_files()
    reorganize_result_files()
    move_normalized_into_results()
    verify_structure()

    print("\n" + "=" * 80)
    print("DONE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
