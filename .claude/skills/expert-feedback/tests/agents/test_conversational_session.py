"""
Unit tests for agents/conversational_session.py

Tests conversational session management including:
- ConversationalSession initialization and loading
- send_turn() message handling
- Prompt rendering with Jinja2
- Session persistence and resumption
- Conversation history tracking
- get_next_prompt_name() utility function

Target coverage: 80%+
"""
import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime
import sys

# Add scripts to path
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from agents import conversational_session


class TestConversationalSessionInit:
    """Test ConversationalSession initialization."""

    @pytest.mark.high
    def test_init_new_session(self, test_workspace):
        """Test initializing a new conversational session."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )

        assert session.agent_type == "expert"
        assert session.agent_id == "typescript"
        assert session.workspace == test_workspace
        assert session.session_id is None
        assert session.turn_count == 0
        assert len(session.conversation_history) == 0

    @pytest.mark.high
    def test_init_with_session_id(self, test_workspace):
        """Test initializing session with existing session ID."""
        # Create session file
        session_file = test_workspace / "session-typescript.json"
        session_data = {
            "agent_type": "expert",
            "agent_id": "typescript",
            "session_id": "test-session-123",
            "turn_count": 2,
            "conversation": [
                {"turn": 1, "prompt_template": "01-review-topic.jinja2"},
                {"turn": 2, "prompt_template": "02-refine-with-synthesis.jinja2"}
            ]
        }
        session_file.write_text(json.dumps(session_data))

        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace,
            session_id="test-session-123"
        )

        assert session.session_id == "test-session-123"
        assert session.turn_count == 2
        assert len(session.conversation_history) == 2

    @pytest.mark.high
    def test_init_creates_state_manager(self, test_workspace):
        """Test that initialization creates StateManager."""
        with patch('agents.conversational_session.StateManager') as mock_sm:
            session = conversational_session.ConversationalSession(
                agent_type="expert",
                agent_id="typescript",
                workspace=test_workspace
            )

            mock_sm.assert_called_once_with(test_workspace)

    @pytest.mark.high
    def test_init_sets_up_jinja_env(self, test_workspace):
        """Test that Jinja2 environment is set up."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )

        assert session.jinja_env is not None
        assert hasattr(session.jinja_env, 'get_template')


class TestLoadExistingSession:
    """Test loading existing sessions."""

    @pytest.mark.high
    def test_load_expert_session(self, test_workspace):
        """Test loading existing expert session."""
        with patch('agents.conversational_session.StateManager') as mock_sm:
            mock_instance = Mock()
            mock_instance.get_session.return_value = {
                "session_id": "session-123",
                "turn": 2
            }
            mock_sm.return_value = mock_instance

            session = conversational_session.ConversationalSession.load(
                agent_id="typescript",
                workspace=test_workspace
            )

            assert session.agent_type == "expert"
            assert session.agent_id == "typescript"
            assert session.session_id == "session-123"

    @pytest.mark.high
    def test_load_synthesis_session(self, test_workspace):
        """Test loading synthesis session."""
        with patch('agents.conversational_session.StateManager') as mock_sm:
            mock_instance = Mock()
            mock_instance.get_session.return_value = {
                "session_id": "synthesis-session",
                "turn": 1
            }
            mock_sm.return_value = mock_instance

            session = conversational_session.ConversationalSession.load(
                agent_id="synthesis",
                workspace=test_workspace
            )

            assert session.agent_type == "synthesis"
            assert session.agent_id == "synthesis"

    @pytest.mark.high
    def test_load_finalization_session(self, test_workspace):
        """Test loading finalization session."""
        with patch('agents.conversational_session.StateManager') as mock_sm:
            mock_instance = Mock()
            mock_instance.get_session.return_value = {
                "session_id": "final-session",
                "turn": 1
            }
            mock_sm.return_value = mock_instance

            session = conversational_session.ConversationalSession.load(
                agent_id="finalization-agent",
                workspace=test_workspace
            )

            assert session.agent_type == "finalization"

    @pytest.mark.high
    def test_load_nonexistent_session_raises(self, test_workspace):
        """Test loading non-existent session raises ValueError."""
        with patch('agents.conversational_session.StateManager') as mock_sm:
            mock_instance = Mock()
            mock_instance.get_session.return_value = None
            mock_sm.return_value = mock_instance

            with pytest.raises(ValueError, match="No session found"):
                conversational_session.ConversationalSession.load(
                    agent_id="nonexistent",
                    workspace=test_workspace
                )


class TestSendTurn:
    """Test send_turn method."""

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_send_turn_raises_not_implemented(self, test_workspace):
        """Test that send_turn raises NotImplementedError (SDK not integrated)."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )

        # Mock _render_prompt to avoid template loading issues
        with patch.object(session, '_render_prompt', return_value="Rendered prompt"):
            with pytest.raises(NotImplementedError, match="Claude Agent SDK"):
                await session.send_turn(
                    "01-review-topic.jinja2",
                    {"topic": "API Design"}
                )

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_send_turn_renders_prompt(self, test_workspace):
        """Test that send_turn renders prompt template."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )

        with patch.object(session, '_send_to_agent', side_effect=NotImplementedError):
            with patch.object(session, '_render_prompt', return_value="Rendered prompt") as mock_render:
                try:
                    await session.send_turn("test.jinja2", {"key": "value"})
                except NotImplementedError:
                    pass

                mock_render.assert_called_once_with("test.jinja2", {"key": "value"})

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_send_turn_increments_count(self, test_workspace):
        """Test that send_turn increments turn count."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )

        initial_count = session.turn_count

        with patch.object(session, '_render_prompt', return_value="Rendered prompt"):
            with patch.object(session, '_send_to_agent', return_value={"content": "Response", "session_id": "123"}):
                with patch.object(session, '_save_conversation_history'):
                    with patch.object(session, '_save_session_id'):
                        with patch.object(session.state_manager, 'update_sessions'):
                            await session.send_turn("test.jinja2", {})

        assert session.turn_count == initial_count + 1

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_send_turn_captures_session_id(self, test_workspace):
        """Test that first turn captures session ID."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )

        with patch.object(session, '_render_prompt', return_value="Rendered prompt"):
            with patch.object(session, '_send_to_agent', return_value={"content": "Response", "session_id": "new-session-123"}):
                with patch.object(session, '_save_conversation_history'):
                    with patch.object(session, '_save_session_id') as mock_save:
                        with patch.object(session.state_manager, 'update_sessions'):
                            await session.send_turn("test.jinja2", {})

        assert session.session_id == "new-session-123"
        mock_save.assert_called_once()

    @pytest.mark.high
    @pytest.mark.asyncio
    async def test_send_turn_updates_state_manager(self, test_workspace):
        """Test that send_turn updates state manager."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )

        with patch.object(session, '_render_prompt', return_value="Rendered prompt"):
            with patch.object(session, '_send_to_agent', return_value={"content": "Response"}):
                with patch.object(session, '_save_conversation_history'):
                    with patch.object(session.state_manager, 'update_sessions') as mock_update:
                        await session.send_turn("test.jinja2", {})

                        mock_update.assert_called_once()


class TestRenderPrompt:
    """Test _render_prompt method."""

    @pytest.mark.high
    def test_render_expert_prompt(self, test_workspace):
        """Test rendering expert prompt."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )

        # Mock the Jinja2 template
        mock_template = Mock()
        mock_template.render.return_value = "Rendered expert prompt"

        with patch.object(session.jinja_env, 'get_template', return_value=mock_template) as mock_get:
            result = session._render_prompt("test.jinja2", {"key": "value"})

            # Should look in experts/ subdirectory
            mock_get.assert_called_once_with("experts/test.jinja2")
            assert result == "Rendered expert prompt"

    @pytest.mark.high
    def test_render_synthesis_prompt(self, test_workspace):
        """Test rendering synthesis prompt."""
        session = conversational_session.ConversationalSession(
            agent_type="synthesis",
            agent_id="synthesis",
            workspace=test_workspace
        )

        mock_template = Mock()
        mock_template.render.return_value = "Rendered synthesis prompt"

        with patch.object(session.jinja_env, 'get_template', return_value=mock_template) as mock_get:
            result = session._render_prompt("test.jinja2", {})

            mock_get.assert_called_once_with("synthesis/test.jinja2")

    @pytest.mark.high
    def test_render_finalization_prompt(self, test_workspace):
        """Test rendering finalization prompt."""
        session = conversational_session.ConversationalSession(
            agent_type="finalization",
            agent_id="finalization",
            workspace=test_workspace
        )

        mock_template = Mock()
        mock_template.render.return_value = "Rendered finalization prompt"

        with patch.object(session.jinja_env, 'get_template', return_value=mock_template) as mock_get:
            result = session._render_prompt("test.jinja2", {})

            mock_get.assert_called_once_with("finalization/test.jinja2")

    @pytest.mark.high
    def test_render_template_not_found_raises(self, test_workspace):
        """Test rendering non-existent template raises ValueError."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )

        with patch.object(session.jinja_env, 'get_template', side_effect=Exception("Template not found")):
            with pytest.raises(ValueError, match="Failed to render template"):
                session._render_prompt("nonexistent.jinja2", {})


class TestSessionPersistence:
    """Test session persistence methods."""

    @pytest.mark.high
    def test_save_session_id(self, test_workspace):
        """Test saving session ID to state."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )
        session.session_id = "test-session-123"

        with patch.object(session.state_manager, 'update_session') as mock_update:
            session._save_session_id()

            mock_update.assert_called_once_with(
                agent_id="typescript",
                session_id="test-session-123",
                turn=0,
                prompt=""
            )

    @pytest.mark.high
    def test_save_session_id_no_id_does_nothing(self, test_workspace):
        """Test that saving with no session ID does nothing."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )
        session.session_id = None

        with patch.object(session.state_manager, 'update_session') as mock_update:
            session._save_session_id()

            mock_update.assert_not_called()

    @pytest.mark.high
    def test_save_conversation_history(self, test_workspace):
        """Test saving conversation history to file."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )
        session.session_id = "session-123"
        session.turn_count = 2
        session.conversation_history = [
            {"turn": 1, "prompt": "test1"},
            {"turn": 2, "prompt": "test2"}
        ]

        session._save_conversation_history()

        history_file = test_workspace / "session-typescript.json"
        assert history_file.exists()

        data = json.loads(history_file.read_text())
        assert data["agent_id"] == "typescript"
        assert data["turn_count"] == 2
        assert len(data["conversation"]) == 2

    @pytest.mark.high
    def test_load_session_data(self, test_workspace):
        """Test loading session data from file."""
        # Create history file
        history_file = test_workspace / "session-typescript.json"
        history_data = {
            "agent_type": "expert",
            "agent_id": "typescript",
            "session_id": "loaded-session",
            "turn_count": 3,
            "conversation": [
                {"turn": 1},
                {"turn": 2},
                {"turn": 3}
            ]
        }
        history_file.write_text(json.dumps(history_data))

        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace,
            session_id="loaded-session"
        )

        assert session.turn_count == 3
        assert len(session.conversation_history) == 3

    @pytest.mark.high
    def test_load_session_data_file_missing(self, test_workspace, capsys):
        """Test loading when history file doesn't exist."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="nonexistent",
            workspace=test_workspace,
            session_id="test"
        )

        # Should handle gracefully
        assert session.turn_count == 0
        assert len(session.conversation_history) == 0

    @pytest.mark.high
    def test_load_session_data_invalid_json(self, test_workspace, capsys):
        """Test loading corrupted history file."""
        # Create invalid JSON file
        history_file = test_workspace / "session-corrupted.json"
        history_file.write_text("invalid json {")

        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="corrupted",
            workspace=test_workspace,
            session_id="test"
        )

        # Should handle gracefully
        captured = capsys.readouterr()
        assert "Failed to load session history" in captured.out or len(captured.out) == 0


class TestSummarizeResponse:
    """Test _summarize_response method."""

    @pytest.mark.high
    def test_summarize_short_response(self, test_workspace):
        """Test summarizing response shorter than 200 chars."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )

        response = {"content": "Short response"}
        summary = session._summarize_response(response)

        assert summary == "Short response"

    @pytest.mark.high
    def test_summarize_long_response(self, test_workspace):
        """Test summarizing response longer than 200 chars."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )

        long_content = "A" * 300
        response = {"content": long_content}
        summary = session._summarize_response(response)

        assert len(summary) == 203  # 200 + "..."
        assert summary.endswith("...")

    @pytest.mark.high
    def test_summarize_empty_response(self, test_workspace):
        """Test summarizing empty response."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )

        response = {}
        summary = session._summarize_response(response)

        assert summary == ""


class TestUtilityMethods:
    """Test utility methods."""

    @pytest.mark.high
    def test_get_context_summary(self, test_workspace):
        """Test getting context summary."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )
        session.session_id = "test-session"
        session.turn_count = 2

        summary = session.get_context_summary()

        assert "typescript" in summary
        assert "expert" in summary
        assert "2 turns" in summary
        assert "test-session" in summary

    @pytest.mark.high
    def test_get_next_turn_number(self, test_workspace):
        """Test getting next turn number."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )
        session.turn_count = 3

        next_turn = session.get_next_turn_number()

        assert next_turn == 4

    @pytest.mark.high
    def test_to_dict(self, test_workspace):
        """Test exporting session to dictionary."""
        session = conversational_session.ConversationalSession(
            agent_type="expert",
            agent_id="typescript",
            workspace=test_workspace
        )
        session.session_id = "test-session"
        session.turn_count = 2
        session.conversation_history = [{"turn": 1}, {"turn": 2}]

        data = session.to_dict()

        assert data["agent_type"] == "expert"
        assert data["agent_id"] == "typescript"
        assert data["session_id"] == "test-session"
        assert data["turn_count"] == 2
        assert len(data["conversation_history"]) == 2


class TestGetNextPromptName:
    """Test get_next_prompt_name utility function."""

    @pytest.mark.high
    def test_expert_turn_1(self):
        """Test expert turn 1 prompt name."""
        name = conversational_session.get_next_prompt_name("expert", 1)
        assert name == "01-review-topic.jinja2"

    @pytest.mark.high
    def test_expert_turn_2(self):
        """Test expert turn 2 prompt name."""
        name = conversational_session.get_next_prompt_name("expert", 2)
        assert name == "02-refine-with-synthesis.jinja2"

    @pytest.mark.high
    def test_expert_turn_3(self):
        """Test expert turn 3 prompt name."""
        name = conversational_session.get_next_prompt_name("expert", 3)
        assert name == "03-final-refinement.jinja2"

    @pytest.mark.high
    def test_expert_turn_4(self):
        """Test expert turn 4 prompt name."""
        name = conversational_session.get_next_prompt_name("expert", 4)
        assert name == "04-review-artifact.jinja2"

    @pytest.mark.high
    def test_expert_invalid_turn_raises(self):
        """Test expert invalid turn raises ValueError."""
        with pytest.raises(ValueError, match="No prompt defined"):
            conversational_session.get_next_prompt_name("expert", 5)

    @pytest.mark.high
    def test_synthesis_turn_1(self):
        """Test synthesis turn 1 prompt name."""
        name = conversational_session.get_next_prompt_name("synthesis", 1)
        assert name == "01-initial-synthesis.jinja2"

    @pytest.mark.high
    def test_synthesis_turn_2(self):
        """Test synthesis turn 2 prompt name."""
        name = conversational_session.get_next_prompt_name("synthesis", 2)
        assert name == "02-refine-synthesis.jinja2"

    @pytest.mark.high
    def test_synthesis_turn_3(self):
        """Test synthesis turn 3 prompt name."""
        name = conversational_session.get_next_prompt_name("synthesis", 3)
        assert name == "03-final-synthesis.jinja2"

    @pytest.mark.high
    def test_synthesis_invalid_turn_raises(self):
        """Test synthesis invalid turn raises ValueError."""
        with pytest.raises(ValueError, match="No prompt defined"):
            conversational_session.get_next_prompt_name("synthesis", 4)

    @pytest.mark.high
    def test_finalization_review_turn_1(self):
        """Test finalization review mode turn 1."""
        name = conversational_session.get_next_prompt_name(
            "finalization", 1, {"mode": "review"}
        )
        assert name == "01-generate-adr.jinja2"

    @pytest.mark.high
    def test_finalization_improve_turn_1(self):
        """Test finalization improve mode turn 1."""
        name = conversational_session.get_next_prompt_name(
            "finalization", 1, {"mode": "improve"}
        )
        assert name == "01-generate-plan.jinja2"

    @pytest.mark.high
    def test_finalization_create_turn_1(self):
        """Test finalization create mode turn 1."""
        name = conversational_session.get_next_prompt_name(
            "finalization", 1, {"mode": "create"}
        )
        assert name == "01-generate-architecture.jinja2"

    @pytest.mark.high
    def test_finalization_turn_2(self):
        """Test finalization turn 2."""
        name = conversational_session.get_next_prompt_name("finalization", 2)
        assert name == "02-regenerate-with-veto.jinja2"

    @pytest.mark.high
    def test_finalization_turn_3(self):
        """Test finalization turn 3."""
        name = conversational_session.get_next_prompt_name("finalization", 3)
        assert name == "03-apply-tweaks.jinja2"

    @pytest.mark.high
    def test_unknown_agent_type_raises(self):
        """Test unknown agent type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown agent type"):
            conversational_session.get_next_prompt_name("invalid", 1)
