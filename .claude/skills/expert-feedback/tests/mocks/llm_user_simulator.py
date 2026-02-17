#!/usr/bin/env python3
"""
LLM-powered user simulator for automated workflow decisions.

Uses Claude Code SDK to simulate realistic user behavior:
- Review concerns and decide AGREE/DISAGREE
- Provide context for agreed concerns
- Approve or reject final artifacts
"""

import asyncio
import json
import re
from typing import List, Dict, Any


class LLMUserSimulator:
    """Simulates user decisions using LLM reasoning."""

    async def review_concerns(
        self,
        concerns: List[Dict[str, Any]],
        artifact_context: str
    ) -> Dict[str, Any]:
        """
        Review concerns and decide which to agree/disagree with.

        Args:
            concerns: List of concern dicts with 'id', 'title', 'severity', 'description'
            artifact_context: Context about what artifact is being reviewed

        Returns:
            {
                "concern-001": {
                    "decision": "AGREE",
                    "user_context": "Yes, we need better error handling"
                },
                "concern-002": {
                    "decision": "DISAGREE",
                    "user_context": "This is intentional design"
                }
            }
        """
        from claude_agent_sdk import query, ClaudeAgentOptions

        prompt = f"""You are a product manager reviewing expert concerns about a technical artifact.

Artifact Context: {artifact_context}

Concerns Raised:
{self._format_concerns(concerns)}

For each concern, decide AGREE or DISAGREE:
- AGREE if concern is valid and should be addressed
- DISAGREE if concern is invalid or intentional design

Make realistic decisions (agree with 60-70% of concerns).
Provide brief context explaining each decision.

Output JSON format:
{{
    "concern-001": {{"decision": "AGREE", "user_context": "explanation"}},
    "concern-002": {{"decision": "DISAGREE", "user_context": "explanation"}}
}}
"""

        options = ClaudeAgentOptions(allowed_tools=[])
        response = await self._get_llm_response(prompt, options)
        return self._parse_concern_decisions(response)

    async def approve_artifact(
        self,
        artifact_content: str,
        iteration_count: int
    ) -> Dict[str, Any]:
        """
        Decide whether to approve or reject final artifact.

        Args:
            artifact_content: The artifact content to review
            iteration_count: Number of concern iterations completed

        Returns:
            {
                "decision": "APPROVE" | "REJECT",
                "reason": "explanation"
            }
        """
        from claude_agent_sdk import query, ClaudeAgentOptions

        prompt = f"""You are a product manager reviewing a final artifact after {iteration_count} concern iteration(s).

Artifact:
{artifact_content[:1000]}...

Decide: APPROVE or REJECT
- APPROVE if artifact is complete and addresses all major concerns
- REJECT if major issues remain (realistic: approve after 1-2 concern iterations)

Output JSON format:
{{"decision": "APPROVE", "reason": "explanation"}}
"""

        options = ClaudeAgentOptions(allowed_tools=[])
        response = await self._get_llm_response(prompt, options)
        return self._parse_approval_decision(response)

    async def _get_llm_response(self, prompt: str, options) -> str:
        """Get response from Claude via SDK."""
        from claude_agent_sdk import query

        full_response = ""
        async for event in query(prompt=prompt, options=options):
            if hasattr(event, 'content_block') and hasattr(event.content_block, 'text'):
                full_response += event.content_block.text
        return full_response

    def _format_concerns(self, concerns: List[Dict]) -> str:
        """Format concerns for prompt."""
        if not concerns:
            return "No concerns raised."

        lines = []
        for c in concerns:
            lines.append(f"- [{c.get('id', 'unknown')}] {c.get('title', 'Untitled')}")
            lines.append(f"  Severity: {c.get('severity', 'medium')}")
            if 'description' in c and c['description']:
                lines.append(f"  Description: {c['description']}")
        return "\n".join(lines)

    def _parse_concern_decisions(self, response: str) -> Dict:
        """Extract JSON from LLM response."""
        # Find JSON block in response
        json_match = re.search(r'\{[^\}]+\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Fallback: return empty dict
        return {}

    def _parse_approval_decision(self, response: str) -> Dict:
        """Extract approval decision from LLM response."""
        # Find JSON block in response
        json_match = re.search(r'\{[^\}]+\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass

        # Fallback: default to approve
        return {"decision": "APPROVE", "reason": "default approval"}
