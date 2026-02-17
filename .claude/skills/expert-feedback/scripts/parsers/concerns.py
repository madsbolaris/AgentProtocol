#!/usr/bin/env python3
"""
Parse synthesized artifact review concerns markdown into structured JSON.

Input: synthesized-concerns.md (LLM-generated markdown)
Output: synthesized-concerns.json (structured data)

The parser handles synthesis of artifact review feedback from multiple experts.
"""
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Evidence:
    """Evidence from an expert review."""
    expert: str
    quote: str


@dataclass
class Concern:
    """A synthesized concern from artifact reviews."""
    title: str
    priority: str  # "high", "medium", or "low"
    category: str  # e.g., "Testing", "Documentation", "Performance"
    raised_by: List[str]  # List of expert names
    agreement_level: str  # "unanimous", "majority", or "split"
    description: str
    evidence: List[Evidence]
    recommendation: str
    impact_if_ignored: str


@dataclass
class SynthesizedConcerns:
    """Complete synthesized concerns with summary."""
    summary: Dict[str, int]
    concerns: List[Concern]


class SynthesizedConcernsParser:
    """Parse synthesized concerns markdown into structured data."""

    def __init__(self, markdown_path: Path):
        self.markdown = markdown_path.read_text()
        self.sections = self._split_sections()

    def _split_sections(self) -> Dict[str, str]:
        """Split markdown by ## headers."""
        sections = {}
        current_section = None
        current_content = []

        for line in self.markdown.split('\n'):
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                # Start new section
                current_section = line[3:].strip()
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections

    def parse_summary(self) -> Dict[str, int]:
        """Parse Summary section."""
        section = self.sections.get('Summary', '')
        if not section:
            return {}

        summary = {}

        # Extract counts from markdown
        patterns = {
            'total_experts': r'\*\*Total Experts:\*\*\s*(\d+)',
            'approvals': r'\*\*Approvals:\*\*\s*(\d+)',
            'minor_tweaks': r'\*\*Minor Tweaks:\*\*\s*(\d+)',
            'concerns_raised': r'\*\*Concerns Raised:\*\*\s*(\d+)',
            'total_concerns': r'\*\*Synthesized Concerns:\*\*\s*(\d+)',
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, section)
            if match:
                summary[key] = int(match.group(1))
            else:
                summary[key] = 0

        return summary

    def parse_concerns(self) -> List[Concern]:
        """Parse Synthesized Concerns section."""
        section = self.sections.get('Synthesized Concerns', '')
        if not section:
            return []

        concerns = []

        # Split by ### headers (each concern)
        concern_blocks = re.split(r'\n### ', '\n' + section)[1:]

        for block in concern_blocks:
            concern = self._parse_concern_block(block)
            if concern:
                concerns.append(concern)

        return concerns

    def _parse_concern_block(self, block: str) -> Optional[Concern]:
        """Parse a single concern block."""
        lines = block.split('\n')
        title = lines[0].strip()

        # Extract structured fields
        priority_match = re.search(r'\*\*Priority:\*\*\s*(High|Medium|Low)', block, re.IGNORECASE)
        priority = priority_match.group(1).lower() if priority_match else 'medium'

        category_match = re.search(r'\*\*Category:\*\*\s*([^\n]+)', block)
        category = category_match.group(1).strip() if category_match else 'General'

        raised_by_match = re.search(r'\*\*Raised by:\*\*\s*([^\n]+)', block)
        if raised_by_match:
            # Parse comma-separated list of experts
            raised_by_text = raised_by_match.group(1).strip()
            # Handle both "expert1, expert2" and "[expert1, expert2]" formats
            raised_by_text = raised_by_text.strip('[]')
            raised_by = [e.strip() for e in raised_by_text.split(',')]
        else:
            raised_by = []

        agreement_match = re.search(r'\*\*Agreement Level:\*\*\s*(Unanimous|Majority|Split)', block, re.IGNORECASE)
        agreement_level = agreement_match.group(1).lower() if agreement_match else 'unknown'

        # Extract description (multi-line)
        description_match = re.search(r'\*\*Description:\*\*\s*\n(.*?)(?:\*\*Evidence:\*\*|$)', block, re.DOTALL)
        description = description_match.group(1).strip() if description_match else ''

        # Extract evidence (list of expert quotes)
        evidence = []
        evidence_section = re.search(r'\*\*Evidence:\*\*\s*\n(.*?)(?:\*\*Recommendation:\*\*|$)', block, re.DOTALL)
        if evidence_section:
            evidence_text = evidence_section.group(1).strip()
            # Parse bullet list: "- [expert]: [quote]"
            for line in evidence_text.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    line = line[2:]
                    # Split on first colon
                    if ':' in line:
                        expert_part, quote_part = line.split(':', 1)
                        expert = expert_part.strip().strip('[]')
                        quote = quote_part.strip()
                        evidence.append(Evidence(expert=expert, quote=quote))

        # Extract recommendation (multi-line)
        recommendation_match = re.search(r'\*\*Recommendation:\*\*\s*\n(.*?)(?:\*\*Impact if Ignored:\*\*|---|\Z)', block, re.DOTALL)
        recommendation = recommendation_match.group(1).strip() if recommendation_match else ''

        # Extract impact if ignored (multi-line)
        impact_match = re.search(r'\*\*Impact if Ignored:\*\*\s*\n(.*?)(?:---|$)', block, re.DOTALL)
        impact_if_ignored = impact_match.group(1).strip() if impact_match else ''

        return Concern(
            title=title,
            priority=priority,
            category=category,
            raised_by=raised_by,
            agreement_level=agreement_level,
            description=description,
            evidence=evidence,
            recommendation=recommendation,
            impact_if_ignored=impact_if_ignored
        )

    def parse(self) -> SynthesizedConcerns:
        """Parse the complete synthesized concerns document."""
        summary = self.parse_summary()
        concerns = self.parse_concerns()

        return SynthesizedConcerns(
            summary=summary,
            concerns=concerns
        )

    def to_json(self) -> Dict[str, Any]:
        """Convert parsed concerns to JSON dict."""
        synthesized = self.parse()

        return {
            'summary': synthesized.summary,
            'concerns': [
                {
                    'title': c.title,
                    'priority': c.priority,
                    'category': c.category,
                    'raised_by': c.raised_by,
                    'agreement_level': c.agreement_level,
                    'description': c.description,
                    'evidence': [asdict(e) for e in c.evidence],
                    'recommendation': c.recommendation,
                    'impact_if_ignored': c.impact_if_ignored
                }
                for c in synthesized.concerns
            ]
        }


def parse_synthesized_concerns(markdown_path: Path, output_path: Path) -> Dict[str, Any]:
    """Parse synthesized concerns markdown and save to JSON.

    Args:
        markdown_path: Path to synthesized-concerns.md
        output_path: Path to write synthesized-concerns.json

    Returns:
        Parsed concerns as dict
    """
    parser = SynthesizedConcernsParser(markdown_path)
    concerns_data = parser.to_json()

    # Write JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(concerns_data, indent=2))

    print(f"✅ Parsed synthesized concerns: {markdown_path.name}")
    print(f"   Total concerns: {len(concerns_data['concerns'])}")
    print(f"   Categories: {set(c['category'] for c in concerns_data['concerns'])}")

    return concerns_data


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parse synthesized concerns markdown")
    parser.add_argument("--markdown", type=Path, required=True, help="Path to synthesized-concerns.md")
    parser.add_argument("--output", type=Path, required=True, help="Path to write synthesized-concerns.json")

    args = parser.parse_args()

    parse_synthesized_concerns(args.markdown, args.output)


if __name__ == "__main__":
    main()
