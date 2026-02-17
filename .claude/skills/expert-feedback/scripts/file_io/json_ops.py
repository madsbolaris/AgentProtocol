"""
JSON I/O operations.

Extracted from common.py to separate concerns.
"""
import json
from pathlib import Path
from typing import Dict, Any


def load_json(path: Path) -> Dict[str, Any]:
    """
    Load JSON from file.

    IMPORTANT: Direct state.json access is forbidden (Phase 1.4).
    Use StateManager.load() instead to ensure consistency and prevent race conditions.
    """
    import inspect

    # Enforce StateManager usage for state.json (Phase 1.4)
    if path.name == "state.json":
        caller_frame = inspect.stack()[1]
        raise RuntimeError(
            "❌ Direct state.json access is forbidden.\n"
            "Use StateManager.load() instead to ensure consistency and prevent race conditions.\n"
            f"Attempted from: {caller_frame.filename}:{caller_frame.lineno}\n"
            f"Migration: Replace load_json(state_path) with StateManager(workspace).load()"
        )

    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], path: Path) -> None:
    """
    Save data as JSON to file.

    IMPORTANT: Direct state.json writes are forbidden (Phase 1.4).
    Use StateManager methods instead to ensure atomic updates and consistency.
    """
    import inspect

    path.parent.mkdir(parents=True, exist_ok=True)

    # Enforce StateManager usage for state.json (Phase 1.4)
    if path.name == "state.json":
        caller_frame = inspect.stack()[1]
        raise RuntimeError(
            "❌ Direct state.json writes are forbidden.\n"
            "Use StateManager methods instead to ensure atomic updates and consistency.\n"
            f"Attempted from: {caller_frame.filename}:{caller_frame.lineno}\n"
            f"Migration: Replace save_json(data, state_path) with StateManager(workspace).update(...)"
        )

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
