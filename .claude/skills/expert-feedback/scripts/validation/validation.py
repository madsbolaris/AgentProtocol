"""
Comprehensive schema validation for expert-feedback outputs.

This module provides high-level validation helpers that use JSON schemas
to validate expert outputs, synthesized results, and other data files.
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from file_io.json_ops import load_json
from file_io.workspace_utils import WorkspacePaths
from prompts.templates import load_json_schema

# Try to import jsonschema, provide helpful error if not available
try:
    from jsonschema import validate, ValidationError
except ImportError:
    raise ImportError(
        "jsonschema library is required for validation. "
        "Install it with: pip3 install jsonschema"
    )


def validate_expert_outputs(
    workspace: Path,
    iteration: int,
    expert: str
) -> Dict[str, List[str]]:
    """
    Validate all expert outputs against schemas.

    Args:
        workspace: Workspace directory path
        iteration: Iteration number
        expert: Expert name

    Returns:
        Dictionary with validation errors:
        {
            "state": [list of errors],
            "questions": [list of errors],
            "review": [list of errors]
        }

    Example:
        errors = validate_expert_outputs(workspace_path, 1, "typescript")
        if any(errors.values()):
            print(f"Validation errors found: {errors}")
    """
    errors = {
        "state": [],
        "questions": [],
        "review": []
    }

    # Use WorkspacePaths to get file locations
    paths = WorkspacePaths(workspace)
    state_file = paths.expert_state_json(expert, iteration)
    questions_file = paths.expert_questions_json(expert, iteration)
    review_file = paths.expert_review_md(expert, iteration)

    # Validate state.json
    if state_file.exists():
        try:
            schema = load_json_schema("state-expert.schema.json")
            data = load_json(state_file)
            validate(data, schema)
        except ValidationError as e:
            errors["state"].append(f"{e.json_path}: {e.message}")
        except Exception as e:
            errors["state"].append(f"Error loading/validating: {str(e)}")
    else:
        errors["state"].append("File not found")

    # Validate questions.json
    if questions_file.exists():
        try:
            schema = load_json_schema("questions.schema.json")
            data = load_json(questions_file)
            validate(data, schema)
        except ValidationError as e:
            errors["questions"].append(f"{e.json_path}: {e.message}")
        except Exception as e:
            errors["questions"].append(f"Error loading/validating: {str(e)}")
    else:
        errors["questions"].append("File not found")

    # Check review markdown exists
    if not review_file.exists():
        errors["review"].append("File not found")

    return errors


def validate_synthesized_outputs(
    workspace: Path,
    iteration: int
) -> Dict[str, List[str]]:
    """
    Validate synthesized outputs against schemas.

    Args:
        workspace: Workspace directory path
        iteration: Iteration number

    Returns:
        Dictionary with validation errors:
        {
            "questions": [list of errors],
            "state": [list of errors]
        }
    """
    errors = {
        "questions": [],
        "state": []
    }

    # Validate questions.json (synthesized questions)
    questions_file = workspace / "questions.json"
    if questions_file.exists():
        try:
            schema = load_json_schema("synthesized-questions.schema.json")
            data = load_json(questions_file)
            validate(data, schema)
        except ValidationError as e:
            errors["questions"].append(f"{e.json_path}: {e.message}")
        except Exception as e:
            errors["questions"].append(f"Error loading/validating: {str(e)}")
    else:
        errors["questions"].append("File not found")

    # Validate state.json (overall state)
    state_file = workspace / "state.json"
    if state_file.exists():
        try:
            schema = load_json_schema("state-overall.schema.json")
            # Read state.json directly to avoid load_json restriction
            import json
            data = json.loads(state_file.read_text())
            validate(data, schema)
        except ValidationError as e:
            errors["state"].append(f"{e.json_path}: {e.message}")
        except Exception as e:
            errors["state"].append(f"Error loading/validating: {str(e)}")
    else:
        errors["state"].append("File not found")

    return errors


def validate_finalization_outputs(
    workspace: Path,
    mode: str
) -> Dict[str, List[str]]:
    """
    Validate finalization outputs against schemas.

    Args:
        workspace: Workspace directory path
        mode: Mode (adr, create, improve, review)

    Returns:
        Dictionary with validation errors:
        {
            "adr": [list of errors] (if mode is adr),
            "artifact": [list of errors] (for other modes)
        }
    """
    errors = {}

    if mode == "adr":
        errors["adr"] = []
        adr_file = workspace / "adr-output.json"
        if adr_file.exists():
            try:
                schema = load_json_schema("adr-output.schema.json")
                data = load_json(adr_file)
                validate(data, schema)
            except ValidationError as e:
                errors["adr"].append(f"{e.json_path}: {e.message}")
            except Exception as e:
                errors["adr"].append(f"Error loading/validating: {str(e)}")
        else:
            errors["adr"].append("File not found")
    else:
        # For other modes, just check that artifact file exists
        errors["artifact"] = []
        # The artifact could have various names depending on mode
        # Just check workspace for any .md or .py or .ts files generated
        artifacts = list(workspace.glob("*.md")) + list(workspace.glob("*.py")) + list(workspace.glob("*.ts"))
        if not artifacts:
            errors["artifact"].append("No artifact file found in workspace")

    return errors


def validate_or_raise(file_path: Path, schema_name: str) -> None:
    """
    Validate JSON file or raise exception with clear error.

    Args:
        file_path: Path to JSON file to validate
        schema_name: Name of schema file (e.g., 'state-expert.schema.json')

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If validation fails

    Example:
        try:
            validate_or_raise(state_file, "state-expert.schema.json")
        except ValueError as e:
            print(f"Validation failed: {e}")
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    schema = load_json_schema(schema_name)

    # For state.json files, read directly to avoid load_json restriction
    # For other files, use load_json
    if file_path.name == "state.json":
        import json
        data = json.loads(file_path.read_text())
    else:
        data = load_json(file_path)

    try:
        validate(data, schema)
    except ValidationError as e:
        raise ValueError(
            f"Validation failed for {file_path}:\n"
            f"  Path: {e.json_path}\n"
            f"  Error: {e.message}"
        )


def validate_all_experts(
    workspace: Path,
    iteration: int,
    experts: List[str],
    raise_on_error: bool = False
) -> Tuple[bool, Dict[str, Dict[str, List[str]]]]:
    """
    Validate all expert outputs for an iteration.

    Args:
        workspace: Workspace directory path
        iteration: Iteration number
        experts: List of expert names
        raise_on_error: If True, raise ValueError on first error

    Returns:
        Tuple of (all_valid: bool, errors_by_expert: dict)

    Example:
        all_valid, errors = validate_all_experts(workspace_path, 1, ["typescript", "python"])
        if not all_valid:
            for expert, errors_dict in errors.items():
                print(f"{expert} errors: {errors_dict}")
    """
    all_errors = {}
    all_valid = True

    for expert in experts:
        errors = validate_expert_outputs(workspace, iteration, expert)

        # Check if this expert has any errors
        has_errors = any(error_list for error_list in errors.values())

        if has_errors:
            all_valid = False
            all_errors[expert] = errors

            if raise_on_error:
                error_msg = f"Validation failed for expert '{expert}':\n"
                for file_type, error_list in errors.items():
                    if error_list:
                        error_msg += f"  {file_type}: {', '.join(error_list)}\n"
                raise ValueError(error_msg)

    return all_valid, all_errors


def validate_workspace_complete(
    workspace: Path,
    iteration: int,
    experts: List[str],
    mode: str
) -> Tuple[bool, Dict[str, List[str]]]:
    """
    Validate that workspace has all required files for completion.

    Args:
        workspace: Workspace directory path
        iteration: Iteration number
        experts: List of expert names
        mode: Mode (adr, create, improve, review)

    Returns:
        Tuple of (is_complete: bool, missing_files: dict)

    Example:
        complete, missing = validate_workspace_complete(workspace_path, 1, ["typescript"], "review")
        if not complete:
            print(f"Missing files: {missing}")
    """
    missing = {
        "expert_files": [],
        "synthesized_files": [],
        "finalization_files": []
    }

    # Use WorkspacePaths to get file locations
    paths = WorkspacePaths(workspace)

    # Check expert files
    for expert in experts:
        state_file = paths.expert_state_json(expert, iteration)
        questions_file = paths.expert_questions_json(expert, iteration)
        review_file = paths.expert_review_md(expert, iteration)

        if not state_file.exists():
            missing["expert_files"].append(f"{expert}/state.json (iteration {iteration})")
        if not questions_file.exists():
            missing["expert_files"].append(f"{expert}/questions.json (iteration {iteration})")
        if not review_file.exists():
            missing["expert_files"].append(f"review-{expert}.md (iteration {iteration})")

    # Check consolidated files
    synthesized_questions = workspace / "questions.json"
    state_file = workspace / "state.json"

    if not synthesized_questions.exists():
        missing["synthesized_files"].append("questions.json")
    if not state_file.exists():
        missing["synthesized_files"].append("state.json")

    # Check finalization files
    if mode == "adr":
        adr_file = workspace / "adr-output.json"
        if not adr_file.exists():
            missing["finalization_files"].append("adr-output.json")
    else:
        # For other modes, check for any artifact
        artifacts = list(workspace.glob("*.md")) + list(workspace.glob("*.py")) + list(workspace.glob("*.ts"))
        if not artifacts:
            missing["finalization_files"].append("artifact (any .md/.py/.ts file)")

    # Check if complete
    is_complete = not any(missing.values())

    return is_complete, missing


def get_validation_summary(
    validation_results: Dict[str, Dict[str, List[str]]]
) -> str:
    """
    Format validation results as a human-readable summary.

    Args:
        validation_results: Results from validate_all_experts or similar

    Returns:
        Formatted summary string

    Example:
        _, errors = validate_all_experts(workspace_path, 1, ["typescript", "python"])
        if errors:
            print(get_validation_summary(errors))
    """
    if not validation_results:
        return "✅ All validations passed"

    lines = ["❌ Validation errors found:"]

    for expert, errors_dict in validation_results.items():
        lines.append(f"\n{expert}:")
        for file_type, error_list in errors_dict.items():
            if error_list:
                lines.append(f"  {file_type}:")
                for error in error_list:
                    lines.append(f"    - {error}")

    return "\n".join(lines)
