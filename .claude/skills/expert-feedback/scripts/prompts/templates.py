"""
Template loading and prompt building functions for expert-feedback.

This module provides functions to load Jinja2 templates and build prompts
for expert reviews and synthesis.
"""
from pathlib import Path
from typing import Dict, Any, Optional, List
import jinja2
import json


# Get the prompts directory (relative to scripts/prompts/templates.py)
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
EXPERTS_DIR = PROMPTS_DIR / "experts"
SYNTHESIS_DIR = PROMPTS_DIR / "synthesis"

# Expert information (minimal - can be expanded)
EXPERT_INFO = {
    "typescript": {
        "name": "TypeScript Expert",
        "category": "Frontend/Backend",
        "background": "Expert in TypeScript, Node.js, and modern JavaScript ecosystems."
    },
    "python": {
        "name": "Python Expert",
        "category": "Backend",
        "background": "Expert in Python, Django/Flask, and Python ecosystem best practices."
    },
    "dx": {
        "name": "Developer Experience Expert",
        "category": "DX",
        "background": "Expert in developer experience, tooling, and workflow optimization."
    },
    "security": {
        "name": "Security Expert",
        "category": "Security",
        "background": "Expert in application security, threat modeling, and secure coding practices."
    }
}


def load_expert_info(expert_name: str) -> Dict[str, Any]:
    """
    Load expert information.

    Args:
        expert_name: Name of the expert (e.g., "typescript", "python")

    Returns:
        Dictionary with expert metadata
    """
    return EXPERT_INFO.get(expert_name, {
        "name": f"{expert_name.title()} Expert",
        "category": "General",
        "background": f"Expert in {expert_name}"
    })


def load_json_schema(schema_name: str) -> Dict[str, Any]:
    """
    Load JSON schema for validation.

    Args:
        schema_name: Name of the schema (e.g., "expert-review", "synthesis")

    Returns:
        JSON schema dictionary
    """
    # For now, return a minimal schema
    # TODO: Load actual schemas if they exist
    return {
        "type": "object",
        "properties": {},
        "additionalProperties": True
    }


def render_template(template_name: str, **kwargs) -> str:
    """
    Render a Jinja2 template with context variables.

    Args:
        template_name: Name of the template file, optionally with path (e.g., "synthesis/01-initial-synthesis.jinja2" or "01-initial-synthesis.jinja2")
        **kwargs: Template variables passed as keyword arguments

    Returns:
        Rendered template string
    """
    # If template_name includes a path, extract it
    if "/" in template_name:
        # Template includes directory (e.g., "synthesis/01-initial-synthesis.jinja2")
        template_dir = PROMPTS_DIR
        template_file = template_name
    else:
        # Determine directory based on template name
        if "synthesis" in template_name or template_name.startswith("0"):
            template_dir = SYNTHESIS_DIR
            template_file = template_name
        elif "expert" in template_name or "review" in template_name or "refine" in template_name:
            template_dir = EXPERTS_DIR
            template_file = template_name
        else:
            template_dir = PROMPTS_DIR
            template_file = template_name

    template_path = template_dir / template_file

    if not template_path.exists():
        # Fallback - return simple formatted template
        return f"# {template_name}\n\n{json.dumps(kwargs, indent=2)}"

    # Load and render template
    # Use PROMPTS_DIR as base if template includes path, otherwise use specific dir
    if "/" in template_name:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(PROMPTS_DIR)))
        template = env.get_template(template_name)
    else:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(template_dir)))
        template = env.get_template(template_file)

    return template.render(**kwargs)


def build_expert_prompt(
    expert_name: str,
    expert_info: Dict[str, Any],
    review_context: str,
    workspace: str,
    iteration: int,
    focus_folders: Optional[List[str]] = None,
    focus_files: Optional[List[str]] = None,  # Accept both parameter names
    focus_context: Optional[str] = None
) -> str:
    """
    Build initial expert review prompt for iteration 1.

    Args:
        expert_name: Name of the expert
        expert_info: Expert metadata from load_expert_info()
        review_context: Context/instructions for the review
        workspace: Workspace path
        iteration: Iteration number (should be 1)
        focus_folders: Optional list of folders to focus on
        focus_files: Optional list of files to focus on
        focus_context: Optional context about what to focus on

    Returns:
        Formatted prompt string
    """
    # Handle both focus_folders and focus_files (backwards compatibility)
    focus_items = focus_folders or focus_files or []
    # Load the iteration 1 template
    template_path = EXPERTS_DIR / "01-review-topic.jinja2"

    if not template_path.exists():
        # Fallback to basic prompt if template doesn't exist
        return f"""# {expert_info['name']} Review - Iteration {iteration}

You are conducting this review as a **{expert_info['name']}**.

{expert_info['background']}

## Review Context

{review_context}

## Workspace

{workspace}

## Your Task

Review the code/design and provide recommendations, concerns, and questions.

Write your review to: {workspace}/iteration-{iteration}/experts/review-{expert_name}.md
"""

    # Load and render template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(EXPERTS_DIR)))
    template = env.get_template("01-review-topic.jinja2")

    return template.render(
        expert_name=expert_info['name'],
        expert=expert_name,
        expert_background=expert_info['background'],
        review_context=review_context,
        workspace=workspace,
        iteration=iteration,
        focus_folders=focus_items,
        focus_context=focus_context or ""
    )


def build_refinement_prompt(
    expert_name: str,
    workspace: str,
    iteration: int,
    qa_answers: Optional[Dict[str, Any]] = None,
    synthesized_questions: Optional[List[Dict[str, Any]]] = None,
    other_experts: Optional[List[Dict[str, Any]]] = None,
    convergence_data: Optional[Dict[str, Any]] = None,
    iteration_diff: Optional[Dict[str, Any]] = None,
    previous_dx_rating: Optional[int] = None
) -> str:
    """
    Build refinement prompt for iteration 2+.

    Args:
        expert_name: Name of the expert
        workspace: Workspace path
        iteration: Iteration number (should be >1)
        qa_answers: User answers to questions
        synthesized_questions: Consolidated questions from iteration 1
        other_experts: Other experts' findings
        convergence_data: Convergence information
        iteration_diff: Changes since previous iteration
        previous_dx_rating: Previous DX rating

    Returns:
        Formatted prompt string
    """
    # Load the iteration 2+ template
    template_path = EXPERTS_DIR / "02-refine-with-synthesis.jinja2"

    if not template_path.exists():
        # Fallback to basic prompt
        return f"""# {expert_name.title()} Review - Iteration {iteration} (DELTA)

**CRITICAL: Write ONLY what CHANGED.**

## User Answers

{qa_answers if qa_answers else "No answers provided"}

## Your Task

Refine your review based on user answers and peer feedback.

Write your refined review to: {workspace}/iteration-{iteration}/experts/review-{expert_name}.md
"""

    # Load and render template
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(EXPERTS_DIR)))
    template = env.get_template("02-refine-with-synthesis.jinja2")

    expert_info = load_expert_info(expert_name)

    return template.render(
        expert_name=expert_info['name'],
        expert=expert_name,
        expert_background=expert_info['background'],
        workspace=workspace,
        iteration=iteration,
        questions=synthesized_questions or [],
        other_experts=other_experts or [],
        convergence_data=convergence_data,
        iteration_diff=iteration_diff,
        previous_dx_rating=previous_dx_rating
    )
