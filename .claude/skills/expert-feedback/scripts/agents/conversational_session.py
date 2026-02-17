#!/usr/bin/env python3
"""
Conversational session management for expert-feedback workflow.

This module provides the ConversationalSession class that manages persistent
agent sessions across multiple conversational turns, enabling:
- Context preservation (agent remembers previous responses)
- Token reduction (no context repetition)
- Natural iterative refinement
- Session resumption after interruption
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from jinja2 import Template, Environment, FileSystemLoader

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from state.manager import StateManager


class ConversationalSession:
    """
    Manages a single agent's conversational session across multiple turns.

    A conversational session represents an ongoing dialogue with a single agent.
    Each turn builds on previous context, allowing the agent to:
    - Remember its own recommendations
    - See how its input influenced synthesis
    - Naturally refine thinking over iterations
    - Build coherent reasoning chains

    Usage:
        # Start new session (iteration 1)
        session = ConversationalSession("expert", "typescript", workspace)
        response = await session.send_turn("01-review-topic.jinja2", context)

        # Resume session (iteration 2+)
        session = ConversationalSession.load("typescript", workspace)
        response = await session.send_turn("02-refine-with-synthesis.jinja2", context)
    """

    def __init__(
        self,
        agent_type: str,
        agent_id: str,
        workspace: Path,
        session_id: Optional[str] = None
    ):
        """
        Initialize a conversational session.

        Args:
            agent_type: Type of agent ("expert", "synthesis", "finalization")
            agent_id: Unique identifier for this agent (e.g., "typescript", "synthesis-agent")
            workspace: Workspace directory path
            session_id: Existing session ID for resumption (None for new session)
        """
        self.agent_type = agent_type
        self.agent_id = agent_id
        self.workspace = workspace
        self.session_id = session_id
        self.turn_count = 0
        self.conversation_history: List[Dict[str, Any]] = []
        self.state_manager = StateManager(workspace)

        # Load existing session data if resuming
        if session_id:
            self._load_session_data()

        # Setup Jinja2 environment for prompt rendering
        # Go up 3 levels: conversational_session.py -> agents/ -> scripts/ -> expert-feedback/
        prompts_dir = Path(__file__).parent.parent.parent / "prompts"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(prompts_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True
        )

    @classmethod
    def load(cls, agent_id: str, workspace: Path) -> "ConversationalSession":
        """
        Load an existing conversational session for resumption.

        Args:
            agent_id: The agent identifier to resume
            workspace: Workspace directory path

        Returns:
            ConversationalSession instance with session_id and history loaded

        Raises:
            ValueError: If no session exists for this agent
        """
        state_manager = StateManager(workspace)
        state = state_manager.load()

        # Determine agent type from ID
        if agent_id in ["synthesis", "synthesis-agent"]:
            agent_type = "synthesis"
            session_id = state_manager.get_synthesis_session_for_iteration(state.iteration)
        elif agent_id in ["finalization", "finalization-agent"]:
            agent_type = "finalization"
            # For finalization, check artifact generation session
            session_id = state.artifact_generation_session_id
        elif agent_id in ["artifact-generation", "artifact_generation"]:
            agent_type = "artifact-generation"
            session_id = state.artifact_generation_session_id
        else:
            agent_type = "expert"
            expert_sessions = state_manager.get_expert_sessions_for_iteration(state.iteration)
            session_id = expert_sessions.get(agent_id)

        if not session_id:
            raise ValueError(
                f"No session found for agent '{agent_id}' in iteration {state.iteration}. "
                f"Create a new session first."
            )

        return cls(
            agent_type=agent_type,
            agent_id=agent_id,
            workspace=workspace,
            session_id=session_id
        )

    async def send_turn(
        self,
        prompt_template: str,
        context: Dict[str, Any],
        timeout: int = 600
    ) -> Dict[str, Any]:
        """
        Send a conversational turn to the agent.

        This continues the ongoing conversation with a new prompt. The agent
        has access to all previous turns in its conversation history.

        Args:
            prompt_template: Prompt filename (e.g., "01-review-topic.jinja2")
            context: Context variables for prompt rendering
            timeout: Maximum time to wait for response (seconds)

        Returns:
            Response dictionary containing:
                - content: Agent's response text
                - session_id: Session ID (for first turn)
                - turn: Turn number
                - timestamp: When response was received

        Raises:
            Exception: If agent call fails
        """
        # Render prompt from template
        prompt = self._render_prompt(prompt_template, context)

        # Send message to agent
        # TODO: Replace with actual Claude Agent SDK call
        response = await self._send_to_agent(prompt, timeout)

        # Capture session ID from first turn
        if self.turn_count == 0 and "session_id" in response:
            self.session_id = response["session_id"]
            self._save_session_id()

        # Track conversation
        self.turn_count += 1
        turn_data = {
            "turn": self.turn_count,
            "prompt_template": prompt_template,
            "timestamp": datetime.utcnow().isoformat(),
            "response_summary": self._summarize_response(response)
        }
        self.conversation_history.append(turn_data)
        self._save_conversation_history()

        # Update state manager with session mapping
        self.state_manager.update_sessions({
            self.agent_id: self.session_id
        })

        return response

    async def _send_to_agent(self, prompt: str, timeout: int) -> Dict[str, Any]:
        """
        Send prompt to Claude agent and get response.

        Args:
            prompt: Rendered prompt text
            timeout: Maximum wait time

        Returns:
            Response dictionary from agent with keys:
                - content: Text content from agent
                - session_id: Session ID for continuity
                - turn: Turn number

        Raises:
            Exception: If agent call fails
        """
        from claude_agent_sdk import query, ClaudeAgentOptions
        from claude_agent_sdk.types import (
            AssistantMessage, SystemMessage, ResultMessage,
            TextBlock, ThinkingBlock
        )

        # Create options with session continuity
        options = ClaudeAgentOptions(
            allowed_tools=[],  # Direct response, no tools needed
            resume=self.session_id  # Resume existing session if available
        )

        # Call agent
        query_call = query(prompt=prompt, options=options)

        # Accumulate response content
        content_parts = []
        captured_session_id = self.session_id

        # Process messages from agent
        async for message in query_call:
            # Debug: Log message type
            import sys
            print(f"[DEBUG _send_to_agent] Got message type: {type(message).__name__}", file=sys.stderr)

            # Capture session ID
            if hasattr(message, 'subtype') and message.subtype == "init":
                if hasattr(message, 'data') and isinstance(message.data, dict):
                    session_id_from_init = message.data.get("session_id")
                    if session_id_from_init:
                        captured_session_id = session_id_from_init
                        print(f"[DEBUG _send_to_agent] Captured session ID from init: {captured_session_id[:12]}", file=sys.stderr)
            elif hasattr(message, 'session_id') and message.session_id:
                captured_session_id = message.session_id
                print(f"[DEBUG _send_to_agent] Captured session ID from message: {captured_session_id[:12]}", file=sys.stderr)

            # Accumulate text content from AssistantMessage
            # Use attribute checking instead of isinstance to work with mock SDK
            if hasattr(message, 'content') and isinstance(getattr(message, 'content', None), list):
                print(f"[DEBUG _send_to_agent] Message with content list detected, blocks: {len(message.content)}", file=sys.stderr)
                for block in message.content:
                    # Check if block has text attribute (TextBlock)
                    if hasattr(block, 'text'):
                        print(f"[DEBUG _send_to_agent] TextBlock found, length: {len(block.text)}", file=sys.stderr)
                        content_parts.append(block.text)

            # Also check for ResultMessage with result field
            # Use attribute checking instead of isinstance
            if hasattr(message, 'result') and message.result:
                print(f"[DEBUG _send_to_agent] Message with result field, length: {len(message.result)}", file=sys.stderr)
                # Use result field as fallback if no text blocks found
                if not content_parts:
                    content_parts.append(message.result)

        # Combine all content
        full_content = "\n".join(content_parts)
        print(f"[DEBUG _send_to_agent] Final content length: {len(full_content)}", file=sys.stderr)

        # Strip markdown code fences if present (```json ... ``` or ``` ... ```)
        stripped_content = full_content.strip()
        if stripped_content.startswith("```"):
            # Find the end of the opening fence (could be ```json or just ```)
            first_newline = stripped_content.find("\n")
            if first_newline != -1:
                # Remove opening fence
                stripped_content = stripped_content[first_newline + 1:]
                # Remove closing fence if present
                if stripped_content.rstrip().endswith("```"):
                    stripped_content = stripped_content.rstrip()[:-3].rstrip()
            print(f"[DEBUG _send_to_agent] Stripped markdown fences, new length: {len(stripped_content)}", file=sys.stderr)

        return {
            "content": stripped_content,
            "session_id": captured_session_id,
            "turn": self.turn_count + 1
        }

    def _render_prompt(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a Jinja2 template with context.

        Args:
            template_name: Prompt template filename
            context: Variables for template

        Returns:
            Rendered prompt text
        """
        # Determine subdirectory based on agent type
        if self.agent_type == "expert":
            template_path = f"experts/{template_name}"
        elif self.agent_type == "synthesis":
            template_path = f"synthesis/{template_name}"
        elif self.agent_type == "finalization":
            template_path = f"finalization/{template_name}"
        elif self.agent_type == "artifact-generation":
            template_path = f"artifact-generator/{template_name}"
        else:
            template_path = template_name

        try:
            template = self.jinja_env.get_template(template_path)
            return template.render(**context)
        except Exception as e:
            raise ValueError(
                f"Failed to render template '{template_path}': {e}"
            )

    def _save_session_id(self):
        """Save session ID to state.json for resumption."""
        if not self.session_id:
            return

        # Update state manager with session mapping
        self.state_manager.update_sessions({
            self.agent_id: self.session_id
        })

    def _save_conversation_history(self):
        """Save conversation history to workspace for debugging."""
        history_file = self.workspace / f"session-{self.agent_id}.json"
        history_file.write_text(json.dumps({
            "agent_type": self.agent_type,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "conversation": self.conversation_history
        }, indent=2))

    def _load_session_data(self):
        """Load existing session data from workspace."""
        history_file = self.workspace / f"session-{self.agent_id}.json"

        if not history_file.exists():
            return

        try:
            data = json.loads(history_file.read_text())
            self.turn_count = data.get("turn_count", 0)
            self.conversation_history = data.get("conversation", [])
        except Exception as e:
            print(f"⚠️ Failed to load session history: {e}")

    def _summarize_response(self, response: Dict[str, Any]) -> str:
        """
        Create brief summary of response for history tracking.

        Args:
            response: Agent response dictionary

        Returns:
            Summary string (first 200 chars of content)
        """
        content = response.get("content", "")
        if len(content) > 200:
            return content[:200] + "..."
        return content

    def get_context_summary(self) -> str:
        """
        Get human-readable summary of this session.

        Returns:
            Summary string showing session progress
        """
        return (
            f"Session {self.agent_id} ({self.agent_type}): "
            f"{self.turn_count} turns, "
            f"session_id={self.session_id}"
        )

    def get_next_turn_number(self) -> int:
        """
        Get the turn number for the next prompt.

        Returns:
            Next turn number (1-indexed)
        """
        return self.turn_count + 1

    def to_dict(self) -> Dict[str, Any]:
        """
        Export session data as dictionary.

        Returns:
            Session data dictionary
        """
        return {
            "agent_type": self.agent_type,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "conversation_history": self.conversation_history
        }


def get_next_prompt_name(agent_type: str, turn: int, context: Dict[str, Any] = None) -> str:
    """
    Get the appropriate prompt filename for a given turn.

    This helper function maps turn numbers to prompt filenames following
    the conversational naming convention: {sequence}-{action}-{context}.jinja2

    Args:
        agent_type: "expert", "synthesis", or "finalization"
        turn: Turn number (1, 2, 3, ...)
        context: Additional context that might affect prompt selection

    Returns:
        Prompt filename (e.g., "01-review-topic.jinja2")

    Examples:
        >>> get_next_prompt_name("expert", 1)
        "01-review-topic.jinja2"

        >>> get_next_prompt_name("expert", 2)
        "02-refine-with-synthesis.jinja2"

        >>> get_next_prompt_name("synthesis", 1)
        "01-initial-synthesis.jinja2"
    """
    if agent_type == "expert":
        if turn == 1:
            return "01-review-topic.jinja2"
        elif turn == 2:
            return "02-refine-with-synthesis.jinja2"
        elif turn == 3:
            return "03-final-refinement.jinja2"
        elif turn == 4:
            return "04-review-artifact.jinja2"
        else:
            raise ValueError(f"No prompt defined for expert turn {turn}")

    elif agent_type == "synthesis":
        if turn == 1:
            return "01-initial-synthesis.jinja2"
        elif turn == 2:
            return "02-refine-synthesis.jinja2"
        elif turn == 3:
            return "03-final-synthesis.jinja2"
        else:
            raise ValueError(f"No prompt defined for synthesis turn {turn}")

    elif agent_type == "finalization":
        mode = context.get("mode", "review") if context else "review"
        if turn == 1:
            if mode == "review":
                return "01-generate-adr.jinja2"
            elif mode == "improve":
                return "01-generate-plan.jinja2"
            elif mode == "create":
                return "01-generate-architecture.jinja2"
        elif turn == 2:
            return "02-regenerate-with-concerns.jinja2"
        elif turn == 3:
            return "03-apply-tweaks.jinja2"
        else:
            raise ValueError(f"No prompt defined for finalization turn {turn}")

    else:
        raise ValueError(f"Unknown agent type: {agent_type}")


if __name__ == "__main__":
    # Basic usage example
    import asyncio
    from pathlib import Path

    async def example():
        workspace = Path("/tmp/test-conversational-session")
        workspace.mkdir(exist_ok=True)

        # Create new expert session
        session = ConversationalSession("expert", "typescript", workspace)
        print(f"Created session: {session.get_context_summary()}")

        # Simulate turn 1
        # response = await session.send_turn(
        #     "01-review-topic.jinja2",
        #     {"topic": "API design", "expert_name": "TypeScript"}
        # )

        # Simulate turn 2 (resume)
        # session2 = ConversationalSession.load("typescript", workspace)
        # response2 = await session2.send_turn(
        #     "02-refine-with-synthesis.jinja2",
        #     {"synthesis": "..."}
        # )

        print("Session example complete (SDK integration pending)")

    # asyncio.run(example())
    print("ConversationalSession class loaded successfully")
    print("To use: from conversational_session import ConversationalSession")
