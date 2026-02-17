#!/usr/bin/env python3
"""
List available experts grouped by category.

Usage:
    python3 list-experts.py [--format json|text]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from file_io.json_ops import load_json


def get_category_name(category_id: str) -> str:
    """Convert category ID to display name."""
    # Simple title-case with dashes to spaces
    return category_id.replace("-", " ").title() + " Experts"


def get_category_description(category_id: str) -> str:
    """Generate category description from category ID."""
    descriptions = {
        "language-sdks": "Experts in language-specific SDK patterns and idioms",
        "llm-clients": "Experts in LLM provider client libraries (OpenAI, Anthropic, etc.)",
        "agent-frameworks": "Experts in agent orchestration frameworks (LangChain, etc.)",
        "autonomous-agents": "Experts in long-running AI agents for task automation and code generation",
        "multi-agent-frameworks": "Experts in multi-agent coordination, collaboration, and role-based orchestration",
        "agent-hosting": "Experts in agent hosting platforms (Microsoft 365 Agents, etc.)",
        "middleware": "Experts in middleware and integration frameworks",
        "prompt-formats": "Experts in agent serialization (Prompty, Semantic Kernel, etc.)",
        "chat-ui": "Experts in chat interface libraries (Bot Framework, etc.)",
        "evaluation": "Experts in LLM/agent evaluation frameworks",
        "observability": "Experts in LLM/agent monitoring and tracing",
        "api-specs": "Experts in LLM/agent REST API specifications",
        "general": "Cross-cutting expertise (DX, beginner-friendly, etc.)"
    }
    return descriptions.get(category_id, f"Experts in {category_id}")


def load_experts():
    """Load experts from experts.json."""
    experts_path = Path(__file__).parent.parent / "experts.json"
    return load_json(experts_path)


def categorize_experts(experts):
    """Group experts by category, deriving categories from data."""
    categorized = {}

    for expert_id, expert_data in experts.items():
        category = expert_data.get("category", "general")

        if category not in categorized:
            categorized[category] = []

        categorized[category].append({
            "id": expert_id,
            "name": expert_data["name"],
            "background": expert_data.get("background", ""),
            "repos": len(expert_data.get("repos", []))
        })

    # Sort categories by name for consistent output
    return dict(sorted(categorized.items()))


def format_text(categorized):
    """Format as human-readable text."""
    output = ["Available Expert Reviewers\n", "=" * 50, ""]

    for cat_id in sorted(categorized.keys()):
        experts = categorized[cat_id]
        cat_name = get_category_name(cat_id)
        cat_desc = get_category_description(cat_id)

        output.append(f"\n{cat_name}")
        output.append(f"{cat_desc}")
        output.append("-" * 50)

        for expert in sorted(experts, key=lambda x: x["id"]):
            # Simplified: just ID and name, no repos count or background
            output.append(f"  • {expert['id']:<20} - {expert['name']}")

    output.append(f"\nTotal: {sum(len(e) for e in categorized.values())} experts")
    return "\n".join(output)


def format_json(categorized):
    """Format as JSON."""
    # Build categories dict dynamically
    categories = {}
    for cat_id in categorized.keys():
        categories[cat_id] = {
            "name": get_category_name(cat_id),
            "description": get_category_description(cat_id)
        }

    result = {
        "categories": categories,
        "experts": categorized,
        "total": sum(len(e) for e in categorized.values())
    }
    return json.dumps(result, indent=2)


def main():
    parser = argparse.ArgumentParser(description="List available expert reviewers")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                       help="Output format")
    args = parser.parse_args()

    try:
        experts = load_experts()
        categorized = categorize_experts(experts)

        if args.format == "json":
            print(format_json(categorized))
        else:
            print(format_text(categorized))

    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "status": "error"
        }), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
