#!/usr/bin/env python3
import argparse
"""
Validate TypeSpec Model Documentation

Checks that models have @usage and @example documentation.

Usage:
    python validate-model-docs.py [path_to_typespec]
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class ModelIssue:
    """Represents a model documentation issue."""
    file: str
    line: int
    model_name: str
    severity: str
    message: str
    category: str

    def __str__(self):
        icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[self.severity]
        return f"{icon} {self.severity.upper()}: {self.file}:{self.line} ({self.model_name})\n   {self.message}\n   Category: {self.category}\n"


def find_models(content: str, file_path: Path) -> List[Dict]:
    """Find all model definitions in TypeSpec file."""
    models = []
    
    # Pattern to match model definitions with their doc comments
    model_pattern = r'/\*\*(.*?)\*/\s*model\s+(\w+)'
    
    for match in re.finditer(model_pattern, content, re.DOTALL):
        doc_comment = match.group(1)
        model_name = match.group(2)
        line_num = content[:match.start()].count('\n') + 1
        
        models.append({
            'line': line_num,
            'name': model_name,
            'doc_comment': doc_comment
        })
    
    return models


def check_model_docs(doc_comment: str) -> Dict[str, bool]:
    """Check if model has @usage and @example documentation."""
    result = {
        'has_usage': False,
        'has_example': False,
        'example_count': 0
    }
    
    # Check for @usage tag
    if re.search(r'@usage', doc_comment):
        result['has_usage'] = True
    
    # Check for @example tags
    example_matches = re.findall(r'@example', doc_comment)
    result['example_count'] = len(example_matches)
    result['has_example'] = result['example_count'] > 0
    
    return result


def validate_model(model: Dict, file_path: Path, important_models: List[str]) -> List[ModelIssue]:
    """Validate documentation for a single model."""
    issues = []
    model_name = model['name']
    doc_check = check_model_docs(model['doc_comment'])
    
    # Determine if this is an important model that requires documentation
    is_important = model_name in important_models
    
    # Check for @usage
    if not doc_check['has_usage']:
        severity = 'error' if is_important else 'warning'
        issues.append(ModelIssue(
            file=file_path.name,
            line=model['line'],
            model_name=model_name,
            severity=severity,
            message='Missing @usage section',
            category='missing_usage'
        ))
    
    # Check for @example
    if not doc_check['has_example']:
        severity = 'error' if is_important else 'warning'
        issues.append(ModelIssue(
            file=file_path.name,
            line=model['line'],
            model_name=model_name,
            severity=severity,
            message='Missing @example block',
            category='missing_example'
        ))
    
    return issues


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate TypeSpec model documentation"
    )
    parser.add_argument(
        "typespec_dir",
        nargs="?",
        type=Path,
        default=Path(__file__).parent.parent.parent / 'typespec',
        help="Path to TypeSpec directory (default: typespec/)"
    )
    args = parser.parse_args()

    typespec_dir = args.typespec_dir

    if not typespec_dir.exists():
        print(f"❌ Directory not found: {typespec_dir}")
        sys.exit(1)
    
    print("📋 Validating TypeSpec Model Documentation\n")
    print(f"📁 Scanning: {typespec_dir}\n")
    
    # Important models that should have documentation (core API models)
    important_models = [
        'AgentCard', 'AgentDefinition', 'Run', 'Thread', 'ChatMessage',
        'AITool', 'RunSubscription', 'AgentSubscription', 'ThreadSubscription',
        'ModelCapabilities', 'Connection', 'AutoResponseConfig'
    ]
    
    # Find all TypeSpec files
    tsp_files = list(typespec_dir.glob('*.tsp'))
    
    all_issues = []
    models_by_file = {}
    
    for tsp_file in tsp_files:
        content = tsp_file.read_text()
        models = find_models(content, tsp_file)
        
        if models:
            models_by_file[tsp_file.name] = models
        
        for model in models:
            issues = validate_model(model, tsp_file, important_models)
            all_issues.extend(issues)
    
    # Sort issues by severity
    errors = [i for i in all_issues if i.severity == 'error']
    warnings = [i for i in all_issues if i.severity == 'warning']
    
    # Print results
    if errors:
        print("❌ ERRORS (Important models missing docs):\n")
        for issue in sorted(errors, key=lambda x: x.model_name):
            print(issue)
    
    if warnings:
        print("⚠️  WARNINGS (Other models missing docs):\n")
        # Group by category
        missing_usage = [i for i in warnings if i.category == 'missing_usage']
        missing_example = [i for i in warnings if i.category == 'missing_example']
        
        if missing_usage:
            print(f"Missing @usage ({len(missing_usage)} models):")
            for issue in sorted(missing_usage[:10], key=lambda x: x.model_name):
                print(f"  - {issue.model_name} ({issue.file}:{issue.line})")
            if len(missing_usage) > 10:
                print(f"  ... and {len(missing_usage) - 10} more")
            print()
        
        if missing_example:
            print(f"Missing @example ({len(missing_example)} models):")
            for issue in sorted(missing_example[:10], key=lambda x: x.model_name):
                print(f"  - {issue.model_name} ({issue.file}:{issue.line})")
            if len(missing_example) > 10:
                print(f"  ... and {len(missing_example) - 10} more")
            print()
    
    # Summary by file
    print("=" * 70)
    print("📊 Summary by File:\n")
    
    for file_name, models in sorted(models_by_file.items()):
        file_issues = [i for i in all_issues if i.file == file_name]
        complete = len(models) - len(file_issues)
        print(f"{file_name}:")
        print(f"  Total models: {len(models)}")
        print(f"  ✅ Complete:  {complete}")
        print(f"  ❌ Missing:   {len(file_issues)}")
        print()
    
    # Overall summary
    total_models = sum(len(models) for models in models_by_file.values())
    complete_models = total_models - len(all_issues)
    
    print("=" * 70)
    print("📊 Overall Summary:\n")
    print(f"   Total models:     {total_models}")
    print(f"   ✅ Complete:       {complete_models}")
    print(f"   ❌ Errors:         {len(errors)}")
    print(f"   ⚠️  Warnings:       {len(warnings)}")
    print(f"   📄 Files:          {len(tsp_files)}")
    print()
    
    # Recommendations
    print("💡 Important Models Needing Documentation:\n")
    important_missing = [i for i in errors if i.model_name in important_models]
    if important_missing:
        for model_name in sorted(set(i.model_name for i in important_missing)):
            model_issues = [i for i in important_missing if i.model_name == model_name]
            print(f"  {model_name}:")
            for issue in model_issues:
                print(f"    - {issue.message}")
        print()
    else:
        print("  ✅ All important models have documentation!\n")
    
    print("💡 Next Steps:\n")
    if errors:
        print("1. Add @usage and @example to important models listed above")
        print("2. Use AgentCard as a template for structure")
        print("3. Focus on core API models first (AgentCard, Run, Thread, etc.)")
    else:
        print("1. Consider adding @usage/@example to remaining models")
        print("2. Focus on models used in API responses")
        print("3. Use AgentCard as a template")
    print()
    
    # Exit code
    if errors:
        print("❌ Model documentation validation FAILED")
        sys.exit(1)
    elif warnings:
        print("⚠️  Model documentation validation passed with warnings")
        sys.exit(0)
    else:
        print("✅ All models have complete documentation!")
        sys.exit(0)


if __name__ == '__main__':
    main()
