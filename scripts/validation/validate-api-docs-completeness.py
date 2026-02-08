#!/usr/bin/env python3
"""
Validate API Documentation Completeness

Checks that API reference documentation files have proper overview and examples sections.
Identifies files that are missing manual content (overview/examples).

Usage:
    python validate-api-docs-completeness.py [path_to_api_reference]
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Set


@dataclass
class DocumentSection:
    """Represents a documentation section."""
    name: str
    present: bool
    line_number: Optional[int] = None
    marker_type: Optional[str] = None  # 'overview', 'examples', 'additional', 'content'


@dataclass
class DocumentAnalysis:
    """Analysis result for a single document."""
    file_path: Path
    has_generated_content: bool
    has_manual_content: bool
    sections: Dict[str, DocumentSection]
    issues: List[str]
    recommendations: List[str]


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    file: str
    severity: str  # 'error', 'warning', 'info'
    message: str
    category: str  # 'missing_overview', 'missing_examples', 'no_manual_content'
    line_number: Optional[int] = None

    def __str__(self):
        icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[self.severity]
        location = f"{self.file}"
        if self.line_number:
            location += f":{self.line_number}"
        result = f"{icon} {self.severity.upper()}: {location}\n"
        result += f"   {self.message}\n"
        result += f"   Category: {self.category}\n"
        return result


def analyze_document(file_path: Path) -> DocumentAnalysis:
    """Analyze a single API reference document."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return DocumentAnalysis(
            file_path=file_path,
            has_generated_content=False,
            has_manual_content=False,
            sections={},
            issues=[f"Failed to read file: {e}"],
            recommendations=[]
        )

    # Check for generated content
    has_generated = '<!-- GENERATED_START -->' in content

    # Check for generic MANUAL_START marker (used when merging 1:1 files)
    has_generic_manual = '<!-- MANUAL_START -->' in content

    # Find all MANUAL_START sections with specific names
    manual_sections = {}
    # Pattern matches section names that can contain spaces, hyphens, slashes, etc.
    manual_pattern = r'<!-- MANUAL_START:\s*(.+?)\s*-->'
    manual_matches = re.finditer(manual_pattern, content)

    for match in manual_matches:
        section_name = match.group(1)
        line_number = content[:match.start()].count('\n') + 1
        manual_sections[section_name] = DocumentSection(
            name=section_name,
            present=True,
            line_number=line_number,
            marker_type='manual'
        )

    has_manual = len(manual_sections) > 0 or has_generic_manual

    # Check for specific expected sections
    sections = {
        'overview': manual_sections.get('overview', DocumentSection('overview', False)),
        'examples': manual_sections.get('examples', DocumentSection('examples', False)),
        'additional': manual_sections.get('additional', DocumentSection('additional', False)),
        'content': manual_sections.get('content', DocumentSection('content', False))
    }

    # Check for endpoint-specific manual sections (e.g., "post /agents", "get -threads-threadid")
    # These count as valid manual content even if no generic overview/examples sections exist
    endpoint_specific_sections = [
        name for name in manual_sections.keys()
        if re.match(r'^(get|post|put|patch|delete)[\s\-]', name, re.IGNORECASE)
    ]

    # If we have endpoint-specific sections OR generic manual marker, treat as having overview/examples
    if endpoint_specific_sections or has_generic_manual:
        # Mark as having overview and examples through endpoint-specific or generic content
        if not sections['overview'].present:
            marker_type = 'generic-manual' if has_generic_manual else 'endpoint-specific'
            sections['overview'] = DocumentSection('overview', True, marker_type=marker_type)
        if not sections['examples'].present:
            marker_type = 'generic-manual' if has_generic_manual else 'endpoint-specific'
            sections['examples'] = DocumentSection('examples', True, marker_type=marker_type)

    # Add any other manual sections found
    for section_name, section in manual_sections.items():
        if section_name not in sections:
            sections[section_name] = section

    issues = []
    recommendations = []

    return DocumentAnalysis(
        file_path=file_path,
        has_generated_content=has_generated,
        has_manual_content=has_manual,
        sections=sections,
        issues=issues,
        recommendations=recommendations
    )


def get_file_category(file_path: Path) -> str:
    """Determine the category of an API reference file."""
    file_name = file_path.name.lower()
    parent_dir = file_path.parent.name.lower()

    # README files are navigation/index files
    if file_name == 'readme.md':
        return 'index'

    # Operations files (in operations/ subdirectory)
    if parent_dir == 'operations':
        return 'operations'

    # Reference files (models, types, tools)
    reference_files = ['agents.md', 'models.md', 'content-types.md', 'tools.md', 'operations.md']
    if file_name in reference_files:
        return 'reference'

    # Unknown/other
    return 'other'


def validate_document(analysis: DocumentAnalysis) -> List[ValidationIssue]:
    """Validate a document and return issues."""
    issues = []
    file_rel = str(analysis.file_path.name)
    category = get_file_category(analysis.file_path)

    # Skip index/README files
    if category == 'index':
        return issues

    # Check if file has any manual content
    if not analysis.has_manual_content:
        if category == 'operations':
            # Operations files MUST have manual content
            issues.append(ValidationIssue(
                file=file_rel,
                severity='error',
                message='Operations file has no manual content (overview/examples)',
                category='no_manual_content'
            ))
        elif category == 'reference':
            # Reference files SHOULD have manual content
            issues.append(ValidationIssue(
                file=file_rel,
                severity='warning',
                message='Reference file has no manual content (overview/examples)',
                category='no_manual_content'
            ))

    # Check for specific required sections
    if analysis.has_manual_content:
        # Check for overview
        if not analysis.sections.get('overview', DocumentSection('overview', False)).present:
            # Check if there's a 'content' section (old style)
            if not analysis.sections.get('content', DocumentSection('content', False)).present:
                if category == 'operations':
                    issues.append(ValidationIssue(
                        file=file_rel,
                        severity='error',
                        message='Missing overview section (use <!-- MANUAL_START: overview -->)',
                        category='missing_overview'
                    ))
                elif category == 'reference':
                    issues.append(ValidationIssue(
                        file=file_rel,
                        severity='warning',
                        message='Missing overview section (use <!-- MANUAL_START: overview -->)',
                        category='missing_overview'
                    ))

        # Check for examples
        if not analysis.sections.get('examples', DocumentSection('examples', False)).present:
            # Check if there's a 'content' section (old style) or 'additional' section
            if not analysis.sections.get('content', DocumentSection('content', False)).present:
                if not analysis.sections.get('additional', DocumentSection('additional', False)).present:
                    if category == 'operations':
                        issues.append(ValidationIssue(
                            file=file_rel,
                            severity='error',
                            message='Missing examples section (use <!-- MANUAL_START: examples -->)',
                            category='missing_examples'
                        ))
                    elif category == 'reference':
                        issues.append(ValidationIssue(
                            file=file_rel,
                            severity='warning',
                            message='Missing examples section (use <!-- MANUAL_START: examples -->)',
                            category='missing_examples'
                        ))

    return issues


def generate_recommendations(analyses: List[DocumentAnalysis]) -> List[str]:
    """Generate recommendations for improving documentation."""
    recommendations = []

    # Files with no manual content
    no_manual = [a for a in analyses if not a.has_manual_content]
    if no_manual:
        recommendations.append("\nFiles Missing Manual Content:")
        for analysis in no_manual:
            category = get_file_category(analysis.file_path)
            if category != 'index':
                recommendations.append(f"  - {analysis.file_path.name} ({category})")

    # Files with manual content but missing overview
    missing_overview = [
        a for a in analyses
        if a.has_manual_content and not a.sections.get('overview', DocumentSection('overview', False)).present
        and not a.sections.get('content', DocumentSection('content', False)).present
    ]
    if missing_overview:
        recommendations.append("\nFiles Missing Overview Section:")
        for analysis in missing_overview:
            recommendations.append(f"  - {analysis.file_path.name}")
            recommendations.append("    Add: <!-- MANUAL_START: overview --> section")

    # Files with manual content but missing examples
    missing_examples = [
        a for a in analyses
        if a.has_manual_content and not a.sections.get('examples', DocumentSection('examples', False)).present
        and not a.sections.get('content', DocumentSection('content', False)).present
        and not a.sections.get('additional', DocumentSection('additional', False)).present
    ]
    if missing_examples:
        recommendations.append("\nFiles Missing Examples Section:")
        for analysis in missing_examples:
            recommendations.append(f"  - {analysis.file_path.name}")
            recommendations.append("    Add: <!-- MANUAL_START: examples --> section")

    return recommendations


def main():
    """Main entry point."""
    # Determine API reference directory
    if len(sys.argv) > 1:
        api_ref_dir = Path(sys.argv[1])
    else:
        api_ref_dir = Path(__file__).parent.parent.parent / 'api-reference'

    if not api_ref_dir.exists():
        print(f"❌ Directory not found: {api_ref_dir}")
        sys.exit(1)

    print("📋 Validating API Documentation Completeness\n")
    print(f"📁 Scanning: {api_ref_dir}\n")

    # Find all markdown files
    md_files = list(api_ref_dir.rglob('*.md'))

    # Analyze each file
    analyses = []
    for md_file in md_files:
        analysis = analyze_document(md_file)
        analyses.append(analysis)

    # Validate and collect issues
    all_issues = []
    for analysis in analyses:
        issues = validate_document(analysis)
        all_issues.extend(issues)

    # Sort issues by severity and category
    errors = [i for i in all_issues if i.severity == 'error']
    warnings = [i for i in all_issues if i.severity == 'warning']
    infos = [i for i in all_issues if i.severity == 'info']

    # Print results
    if errors:
        print("❌ ERRORS:\n")
        for issue in errors:
            print(issue)

    if warnings:
        print("⚠️  WARNINGS:\n")
        for issue in warnings:
            print(issue)

    if infos:
        print("ℹ️  INFO:\n")
        for issue in infos:
            print(issue)

    # Generate recommendations
    recommendations = generate_recommendations(analyses)
    if recommendations:
        print("💡 RECOMMENDATIONS:\n")
        for rec in recommendations:
            print(rec)

    # Summary by category
    print("\n" + "=" * 70)
    print("📊 Summary by Category:\n")

    categories = {
        'operations': [],
        'reference': [],
        'index': [],
        'other': []
    }

    for analysis in analyses:
        category = get_file_category(analysis.file_path)
        categories[category].append(analysis)

    for category, items in categories.items():
        if not items:
            continue

        print(f"\n{category.upper()} ({len(items)} files):")

        complete = [a for a in items if a.has_manual_content and
                   (a.sections.get('overview', DocumentSection('overview', False)).present or
                    a.sections.get('content', DocumentSection('content', False)).present) and
                   (a.sections.get('examples', DocumentSection('examples', False)).present or
                    a.sections.get('content', DocumentSection('content', False)).present or
                    a.sections.get('additional', DocumentSection('additional', False)).present)]

        partial = [a for a in items if a.has_manual_content and a not in complete]
        missing = [a for a in items if not a.has_manual_content and category != 'index']

        print(f"  ✅ Complete:        {len(complete)}")
        print(f"  ⚠️  Partial:         {len(partial)}")
        print(f"  ❌ Missing Content: {len(missing)}")

    # Overall summary
    print("\n" + "=" * 70)
    print("📊 Overall Summary:\n")
    print(f"   ❌ Errors:   {len(errors)}")
    print(f"   ⚠️  Warnings: {len(warnings)}")
    print(f"   ℹ️  Info:     {len(infos)}")
    print(f"   📄 Files:    {len(md_files)}")
    print()

    # Exit code
    if errors:
        print("❌ API documentation completeness validation FAILED")
        sys.exit(1)
    elif warnings:
        print("⚠️  API documentation completeness validation passed with warnings")
        sys.exit(0)
    else:
        print("✅ All API documentation complete!")
        sys.exit(0)


if __name__ == '__main__':
    main()
