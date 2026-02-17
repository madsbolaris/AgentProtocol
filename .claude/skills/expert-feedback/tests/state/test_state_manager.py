"""
Unit tests for state management (state_manager.py).

Tests WorkspaceState, StateManager, atomic updates, and session management.
"""
import json
import pytest
from pathlib import Path
import sys
import tempfile
import shutil

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from state.manager import WorkspaceState, StateManager


class TestWorkspaceState:
    """Test WorkspaceState dataclass."""

    def test_default_values(self):
        """Test default values for WorkspaceState."""
        state = WorkspaceState(
            topic="Test topic",
            experts=["typescript", "python"],
            iteration=1
        )

        assert state.topic == "Test topic"
        assert state.experts == ["typescript", "python"]
        assert state.iteration == 1
        assert state.mode == "review"
        assert state.convergence_percent == 0
        assert state.consensus_reached is False
        assert state.convergence_target == 80
        assert state.expert_sessions == {}
        assert state.synthesis_session_id is None
        assert state.artifact_generation_session_id is None
        assert state.artifact_review_needed is False

    def test_custom_values(self):
        """Test custom values for WorkspaceState."""
        state = WorkspaceState(
            topic="Test topic",
            experts=["typescript"],
            iteration=2,
            mode="improve",
            convergence_percent=75,
            convergence_target=70,
            expert_sessions={"typescript": "session-123"}
        )

        assert state.mode == "improve"
        assert state.convergence_percent == 75
        assert state.convergence_target == 70
        assert state.expert_sessions == {"typescript": "session-123"}

    def test_post_init_initializes_sessions(self):
        """Test that __post_init__ initializes expert_sessions if None."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1,
            expert_sessions=None
        )

        assert state.expert_sessions == {}


class TestStateManager:
    """Test StateManager class."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.manager = StateManager(self.workspace)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_save_and_load(self):
        """Test saving and loading state."""
        state = WorkspaceState(
            topic="Test topic",
            experts=["typescript", "python"],
            iteration=1,
            mode="review",
            convergence_percent=50
        )

        # Save state
        self.manager.save(state)

        # Verify file exists
        assert self.manager.state_path.exists()

        # Load state
        loaded_state = self.manager.load()

        assert loaded_state.topic == "Test topic"
        assert loaded_state.experts == ["typescript", "python"]
        assert loaded_state.iteration == 1
        assert loaded_state.mode == "review"
        assert loaded_state.convergence_percent == 50

    def test_load_missing_file_raises_error(self):
        """Test that loading missing state file raises error."""
        with pytest.raises(FileNotFoundError, match="State file not found"):
            self.manager.load()

    def test_update_sessions(self):
        """Test atomically updating expert sessions."""
        # Create initial state
        state = WorkspaceState(
            topic="Test",
            experts=["typescript", "python"],
            iteration=1,
            expert_sessions={"typescript": "session-1"}
        )
        self.manager.save(state)

        # Update sessions
        self.manager.update_sessions({"python": "session-2"})

        # Load and verify
        loaded_state = self.manager.load()
        assert loaded_state.expert_sessions == {
            "typescript": "session-1",
            "python": "session-2"
        }

    def test_update_sessions_preserves_existing(self):
        """Test that update_sessions preserves existing sessions."""
        # Create initial state
        state = WorkspaceState(
            topic="Test",
            experts=["typescript", "python", "dotnet"],
            iteration=1,
            expert_sessions={"typescript": "session-1", "python": "session-2"}
        )
        self.manager.save(state)

        # Update with new session
        self.manager.update_sessions({"dotnet": "session-3"})

        # Load and verify all sessions present
        loaded_state = self.manager.load()
        assert loaded_state.expert_sessions == {
            "typescript": "session-1",
            "python": "session-2",
            "dotnet": "session-3"
        }

    def test_set_synthesizion_session(self):
        """Test setting synthesizion session ID."""
        # Create initial state
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Set synthesis session
        self.manager.set_synthesis_session("synthesis-session-123")

        # Load and verify
        loaded_state = self.manager.load()
        assert loaded_state.synthesis_session_id == "synthesis-session-123"

    def test_state_serialization(self):
        """Test that state serializes correctly to JSON."""
        state = WorkspaceState(
            topic="Test topic",
            experts=["typescript", "python"],
            iteration=1,
            expert_sessions={"typescript": "session-1"}
        )

        self.manager.save(state)

        # Read raw JSON
        with open(self.manager.state_path) as f:
            data = json.load(f)

        assert data["topic"] == "Test topic"
        assert data["experts"] == ["typescript", "python"]
        assert data["iteration"] == 1
        assert data["expert_sessions"] == {"typescript": "session-1"}

    def test_backwards_compatibility(self):
        """Test reading old state format without new fields."""
        # Create old-style state.json (missing new fields)
        old_state = {
            "topic": "Old topic",
            "experts": ["typescript"],
            "iteration": 1,
            "mode": "review"
        }

        with open(self.manager.state_path, 'w') as f:
            json.dump(old_state, f)

        # Should load with defaults for missing fields
        state = self.manager.load()

        assert state.topic == "Old topic"
        assert state.experts == ["typescript"]
        assert state.iteration == 1
        assert state.mode == "review"
        # New fields should have defaults
        assert state.convergence_percent == 0
        assert state.expert_sessions == {}

    def test_iteration_increment(self):
        """Test incrementing iteration number."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Increment iteration
        state.iteration = 2
        self.manager.save(state)

        # Verify
        loaded_state = self.manager.load()
        assert loaded_state.iteration == 2

    def test_convergence_tracking(self):
        """Test tracking convergence progress."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript", "python"],
            iteration=1,
            convergence_percent=0
        )
        self.manager.save(state)

        # Update convergence
        state.convergence_percent = 75
        state.iteration = 2
        self.manager.save(state)

        # Verify
        loaded_state = self.manager.load()
        assert loaded_state.convergence_percent == 75
        assert loaded_state.consensus_reached is False

        # Reach consensus
        state.convergence_percent = 85
        state.consensus_reached = True
        state.iteration = 3
        self.manager.save(state)

        loaded_state = self.manager.load()
        assert loaded_state.convergence_percent == 85
        assert loaded_state.consensus_reached is True


class TestAtomicUpdates:
    """Test atomic update operations."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.manager = StateManager(self.workspace)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_atomic_session_update(self):
        """Test that session updates are atomic."""
        # Create initial state
        state = WorkspaceState(
            topic="Test",
            experts=["typescript", "python"],
            iteration=1,
            expert_sessions={}
        )
        self.manager.save(state)

        # Multiple sequential updates
        self.manager.update_sessions({"typescript": "session-1"})
        self.manager.update_sessions({"python": "session-2"})

        # All updates should be present
        loaded_state = self.manager.load()
        assert "typescript" in loaded_state.expert_sessions
        assert "python" in loaded_state.expert_sessions


class TestGenericUpdate:
    """Test generic update() method."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.manager = StateManager(self.workspace)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_generic_update_single_field(self):
        """Test updating a single field."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Update single field
        updated = self.manager.update({"mode": "improve"})

        assert updated.mode == "improve"
        assert updated.iteration == 1  # Other fields preserved

    def test_generic_update_multiple_fields(self):
        """Test updating multiple fields at once."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Update multiple fields
        updated = self.manager.update({
            "mode": "improve",
            "convergence_percent": 85,
            "consensus_reached": True
        })

        assert updated.mode == "improve"
        assert updated.convergence_percent == 85
        assert updated.consensus_reached is True

    def test_generic_update_preserves_other_fields(self):
        """Test that update preserves non-updated fields."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript", "python"],
            iteration=3,
            convergence_percent=75
        )
        self.manager.save(state)

        # Update only mode
        updated = self.manager.update({"mode": "create"})

        # Check updated field
        assert updated.mode == "create"
        # Check preserved fields
        assert updated.experts == ["typescript", "python"]
        assert updated.iteration == 3
        assert updated.convergence_percent == 75


class TestSetIteration:
    """Test set_iteration() method."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.manager = StateManager(self.workspace)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_set_iteration_to_specific_value(self):
        """Test setting iteration to specific value."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Set to iteration 5
        updated = self.manager.set_iteration(5)

        assert updated.iteration == 5

    def test_set_iteration_backwards(self):
        """Test setting iteration to lower value (revert scenario)."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=10
        )
        self.manager.save(state)

        # Set back to iteration 3
        updated = self.manager.set_iteration(3)

        assert updated.iteration == 3

    def test_set_iteration_to_zero(self):
        """Test setting iteration to zero."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=5
        )
        self.manager.save(state)

        # Set to 0
        updated = self.manager.set_iteration(0)

        assert updated.iteration == 0


class TestExecutionState:
    """Test execution state management methods."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.manager = StateManager(self.workspace)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_initialize_execution_state(self):
        """Test initializing execution state."""
        default_state = self.manager.initialize_execution_state()

        assert default_state["status"] == "not_started"
        assert default_state["session_id"] is None
        assert default_state["iterations"] == 0
        assert default_state["steps_completed"] == 0
        assert default_state["files_modified"] == []
        assert default_state["deferred_questions_count"] == 0
        assert default_state["progress_percent"] == 0
        assert default_state["history"] == []

    def test_update_execution_progress_basic(self):
        """Test updating execution progress."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Update execution progress
        updated = self.manager.update_execution_progress(
            status="running",
            session_id="sess-exec-123",
            iterations=1,
            steps_completed=5,
            progress_percent=25
        )

        exec_state = updated.execution
        assert exec_state["status"] == "running"
        assert exec_state["session_id"] == "sess-exec-123"
        assert exec_state["iterations"] == 1
        assert exec_state["steps_completed"] == 5
        assert exec_state["progress_percent"] == 25
        assert exec_state["started_at"] is not None
        assert exec_state["last_activity"] is not None

    def test_update_execution_progress_incremental(self):
        """Test incrementally updating execution progress."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # First update
        self.manager.update_execution_progress(
            status="running",
            iterations=1,
            steps_completed=5
        )

        # Second update - incremental
        updated = self.manager.update_execution_progress(
            status="running",
            iterations=2,
            steps_completed=10,
            progress_percent=50
        )

        exec_state = updated.execution
        assert exec_state["iterations"] == 2
        assert exec_state["steps_completed"] == 10
        assert exec_state["progress_percent"] == 50

    def test_update_execution_progress_with_files(self):
        """Test updating execution progress with modified files."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        updated = self.manager.update_execution_progress(
            status="running",
            files_modified=["src/api.ts", "tests/api.test.ts"],
            steps_completed=3
        )

        exec_state = updated.execution
        assert exec_state["files_modified"] == ["src/api.ts", "tests/api.test.ts"]

    def test_update_execution_progress_with_questions(self):
        """Test updating execution progress with question counts."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        updated = self.manager.update_execution_progress(
            status="paused",
            deferred_questions_count=3,
            answered_questions_count=1
        )

        exec_state = updated.execution
        assert exec_state["status"] == "paused"
        assert exec_state["deferred_questions_count"] == 3
        assert exec_state["answered_questions_count"] == 1

    def test_add_execution_history_entry(self):
        """Test adding execution history entry."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        updated = self.manager.add_execution_history_entry(
            iteration=1,
            steps=["Created API endpoint", "Added tests"],
            files=["src/api.ts"],
            status="in_progress"
        )

        exec_state = updated.execution
        assert len(exec_state["history"]) == 1
        assert exec_state["history"][0]["iteration"] == 1
        assert exec_state["history"][0]["steps"] == ["Created API endpoint", "Added tests"]
        assert exec_state["history"][0]["files"] == ["src/api.ts"]
        assert exec_state["history"][0]["status"] == "in_progress"
        assert "timestamp" in exec_state["history"][0]

    def test_add_multiple_execution_history_entries(self):
        """Test adding multiple execution history entries."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Add first entry
        self.manager.add_execution_history_entry(
            iteration=1,
            steps=["Step 1"],
            files=["file1.ts"],
            status="in_progress"
        )

        # Add second entry
        updated = self.manager.add_execution_history_entry(
            iteration=2,
            steps=["Step 2"],
            files=["file2.ts"],
            status="completed"
        )

        exec_state = updated.execution
        assert len(exec_state["history"]) == 2
        assert exec_state["history"][0]["iteration"] == 1
        assert exec_state["history"][1]["iteration"] == 2

    def test_get_execution_state_initialized(self):
        """Test getting execution state when initialized."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Update execution state
        self.manager.update_execution_progress(
            status="running",
            iterations=3
        )

        # Get execution state
        exec_state = self.manager.get_execution_state()
        assert exec_state["status"] == "running"
        assert exec_state["iterations"] == 3

    def test_get_execution_state_uninitialized(self):
        """Test getting execution state when not yet initialized."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Get execution state without initializing
        exec_state = self.manager.get_execution_state()
        assert exec_state["status"] == "not_started"
        assert exec_state["iterations"] == 0


class TestCoverageState:
    """Test test coverage state management methods."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.manager = StateManager(self.workspace)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_initialize_test_coverage_state(self):
        """Test initializing test coverage state."""
        default_state = self.manager.initialize_test_coverage_state()

        assert default_state["status"] == "not_started"
        assert default_state["session_id"] is None
        assert default_state["initial_coverage"] == 0.0
        assert default_state["current_coverage"] == 0.0
        assert default_state["target_coverage"] == 90.0
        assert default_state["iterations"] == 0
        assert default_state["tests_written"] == 0
        assert default_state["history"] == []

    def test_update_test_coverage_progress_basic(self):
        """Test updating test coverage progress."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Update test coverage progress
        updated = self.manager.update_test_coverage_progress(
            status="running",
            session_id="sess-test-123",
            initial_coverage=67.5,
            current_coverage=75.2,
            target_coverage=90.0,
            iterations=1,
            tests_written=12
        )

        cov_state = updated.test_coverage
        assert cov_state["status"] == "running"
        assert cov_state["session_id"] == "sess-test-123"
        assert cov_state["initial_coverage"] == 67.5
        assert cov_state["current_coverage"] == 75.2
        assert cov_state["target_coverage"] == 90.0
        assert cov_state["iterations"] == 1
        assert cov_state["tests_written"] == 12
        assert cov_state["started_at"] is not None

    def test_update_test_coverage_progress_incremental(self):
        """Test incrementally updating test coverage progress."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # First update
        self.manager.update_test_coverage_progress(
            status="running",
            initial_coverage=67.5,
            current_coverage=72.0,
            iterations=1,
            tests_written=5
        )

        # Second update - incremental
        updated = self.manager.update_test_coverage_progress(
            status="running",
            current_coverage=85.2,
            iterations=5,
            tests_written=12
        )

        cov_state = updated.test_coverage
        assert cov_state["initial_coverage"] == 67.5  # Preserved
        assert cov_state["current_coverage"] == 85.2  # Updated
        assert cov_state["iterations"] == 5
        assert cov_state["tests_written"] == 12

    def test_update_test_coverage_progress_completed(self):
        """Test marking test coverage as completed."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        updated = self.manager.update_test_coverage_progress(
            status="completed",
            current_coverage=92.3,
            iterations=6,
            tests_written=20
        )

        cov_state = updated.test_coverage
        assert cov_state["status"] == "completed"
        assert cov_state["current_coverage"] == 92.3

    def test_add_test_coverage_history_entry(self):
        """Test adding test coverage history entry."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        updated = self.manager.add_test_coverage_history_entry(
            iteration=1,
            coverage=72.0,
            tests_written=["test_api_validation", "test_error_handling"]
        )

        cov_state = updated.test_coverage
        assert len(cov_state["history"]) == 1
        assert cov_state["history"][0]["iteration"] == 1
        assert cov_state["history"][0]["coverage"] == 72.0
        assert cov_state["history"][0]["tests_written"] == ["test_api_validation", "test_error_handling"]
        assert "timestamp" in cov_state["history"][0]

    def test_add_multiple_test_coverage_history_entries(self):
        """Test adding multiple test coverage history entries."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Add first entry
        self.manager.add_test_coverage_history_entry(
            iteration=1,
            coverage=72.0,
            tests_written=["test_1"]
        )

        # Add second entry
        self.manager.add_test_coverage_history_entry(
            iteration=2,
            coverage=78.5,
            tests_written=["test_2", "test_3"]
        )

        # Add third entry
        updated = self.manager.add_test_coverage_history_entry(
            iteration=3,
            coverage=85.2,
            tests_written=["test_4"]
        )

        cov_state = updated.test_coverage
        assert len(cov_state["history"]) == 3
        assert cov_state["history"][0]["coverage"] == 72.0
        assert cov_state["history"][1]["coverage"] == 78.5
        assert cov_state["history"][2]["coverage"] == 85.2

    def test_get_test_coverage_state_initialized(self):
        """Test getting test coverage state when initialized."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Update coverage state
        self.manager.update_test_coverage_progress(
            status="running",
            current_coverage=82.0,
            iterations=4
        )

        # Get coverage state
        cov_state = self.manager.get_test_coverage_state()
        assert cov_state["status"] == "running"
        assert cov_state["current_coverage"] == 82.0
        assert cov_state["iterations"] == 4

    def test_get_test_coverage_state_uninitialized(self):
        """Test getting test coverage state when not yet initialized."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        # Get coverage state without initializing
        cov_state = self.manager.get_test_coverage_state()
        assert cov_state["status"] == "not_started"
        assert cov_state["current_coverage"] == 0.0
        assert cov_state["target_coverage"] == 90.0


class TestLoggerIntegration:
    """Test StateManager with logging enabled."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_state_manager_with_logging_disabled(self):
        """Test that StateManager works without logger (default)."""
        from unittest.mock import patch, MagicMock

        # Mock config to disable logging
        mock_config = MagicMock()
        mock_config.log_state_transitions = False

        with patch('config.get_config', return_value=mock_config):
            manager = StateManager(self.workspace)
            assert manager.logger is None

    def test_state_manager_with_logging_enabled(self):
        """Test that StateManager creates logger when enabled."""
        from unittest.mock import patch, MagicMock

        # Mock config to enable logging
        mock_config = MagicMock()
        mock_config.log_state_transitions = True

        # Mock the logger setup
        mock_logger = MagicMock()

        with patch('config.get_config', return_value=mock_config):
            with patch('agent_logging.agent_logger.setup_agent_logger_v2', return_value=mock_logger):
                manager = StateManager(self.workspace, correlation_id="test-corr-123")
                assert manager.logger is not None
                assert manager.correlation_id == "test-corr-123"

    def test_load_with_logger(self):
        """Test load() logs debug and info when logger enabled."""
        from unittest.mock import patch, MagicMock

        # Create state first
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=2
        )
        manager_no_log = StateManager(self.workspace)
        manager_no_log.save(state)

        # Now test with logger
        mock_config = MagicMock()
        mock_config.log_state_transitions = True
        mock_logger = MagicMock()

        with patch('config.get_config', return_value=mock_config):
            with patch('agent_logging.agent_logger.setup_agent_logger_v2', return_value=mock_logger):
                manager = StateManager(self.workspace)
                loaded = manager.load()

                # Verify logger was called
                assert mock_logger.debug.called
                assert mock_logger.info.called
                assert loaded.iteration == 2

    def test_save_with_logger(self):
        """Test save() logs debug and info when logger enabled."""
        from unittest.mock import patch, MagicMock

        mock_config = MagicMock()
        mock_config.log_state_transitions = True
        mock_logger = MagicMock()

        with patch('config.get_config', return_value=mock_config):
            with patch('agent_logging.agent_logger.setup_agent_logger_v2', return_value=mock_logger):
                manager = StateManager(self.workspace)
                state = WorkspaceState(
                    topic="Test",
                    experts=["typescript"],
                    iteration=3
                )
                manager.save(state)

                # Verify logger was called
                assert mock_logger.debug.called
                assert mock_logger.info.called

    def test_update_with_logger(self):
        """Test update() logs when logger enabled."""
        from unittest.mock import patch, MagicMock

        # Create initial state
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        manager_no_log = StateManager(self.workspace)
        manager_no_log.save(state)

        # Test with logger
        mock_config = MagicMock()
        mock_config.log_state_transitions = True
        mock_logger = MagicMock()

        with patch('config.get_config', return_value=mock_config):
            with patch('agent_logging.agent_logger.setup_agent_logger_v2', return_value=mock_logger):
                manager = StateManager(self.workspace)
                manager.update({"mode": "improve"})

                # Verify logger.info was called
                assert mock_logger.info.called

    def test_update_sessions_with_logger(self):
        """Test update_sessions() logs when logger enabled."""
        from unittest.mock import patch, MagicMock

        # Create initial state
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        manager_no_log = StateManager(self.workspace)
        manager_no_log.save(state)

        # Test with logger
        mock_config = MagicMock()
        mock_config.log_state_transitions = True
        mock_logger = MagicMock()

        with patch('config.get_config', return_value=mock_config):
            with patch('agent_logging.agent_logger.setup_agent_logger_v2', return_value=mock_logger):
                manager = StateManager(self.workspace)
                manager.update_sessions({"typescript": "sess-123"})

                # Verify logger.info was called
                assert mock_logger.info.call_count >= 2  # At least 2 info calls

    def test_set_synthesis_session_with_logger(self):
        """Test set_synthesis_session() logs when logger enabled."""
        from unittest.mock import patch, MagicMock

        # Create initial state
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        manager_no_log = StateManager(self.workspace)
        manager_no_log.save(state)

        # Test with logger
        mock_config = MagicMock()
        mock_config.log_state_transitions = True
        mock_logger = MagicMock()

        with patch('config.get_config', return_value=mock_config):
            with patch('agent_logging.agent_logger.setup_agent_logger_v2', return_value=mock_logger):
                manager = StateManager(self.workspace)
                manager.set_synthesis_session("sess-synthesis-456")

                # Verify logger.info was called
                assert mock_logger.info.called

    def test_update_convergence_with_logger(self):
        """Test update_convergence() logs when logger enabled."""
        from unittest.mock import patch, MagicMock

        # Create initial state
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        manager_no_log = StateManager(self.workspace)
        manager_no_log.save(state)

        # Test with logger
        mock_config = MagicMock()
        mock_config.log_state_transitions = True
        mock_logger = MagicMock()

        with patch('config.get_config', return_value=mock_config):
            with patch('agent_logging.agent_logger.setup_agent_logger_v2', return_value=mock_logger):
                manager = StateManager(self.workspace)
                manager.update_convergence(
                    convergence_percent=85,
                    consensus_reached=True,
                    high_agreement=5,
                    partial_agreement=2,
                    low_agreement=1
                )

                # Verify logger.info was called
                assert mock_logger.info.call_count >= 2

    def test_set_iteration_with_logger(self):
        """Test set_iteration() logs when logger enabled."""
        from unittest.mock import patch, MagicMock

        # Create initial state
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        manager_no_log = StateManager(self.workspace)
        manager_no_log.save(state)

        # Test with logger
        mock_config = MagicMock()
        mock_config.log_state_transitions = True
        mock_logger = MagicMock()

        with patch('config.get_config', return_value=mock_config):
            with patch('agent_logging.agent_logger.setup_agent_logger_v2', return_value=mock_logger):
                manager = StateManager(self.workspace)
                manager.set_iteration(5)

                # Verify logger.info was called
                assert mock_logger.info.called

    def test_increment_iteration_with_logger(self):
        """Test increment_iteration() logs when logger enabled."""
        from unittest.mock import patch, MagicMock

        # Create initial state
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        manager_no_log = StateManager(self.workspace)
        manager_no_log.save(state)

        # Test with logger
        mock_config = MagicMock()
        mock_config.log_state_transitions = True
        mock_logger = MagicMock()

        with patch('config.get_config', return_value=mock_config):
            with patch('agent_logging.agent_logger.setup_agent_logger_v2', return_value=mock_logger):
                manager = StateManager(self.workspace)
                manager.increment_iteration()

                # Verify logger.info and debug were called
                assert mock_logger.info.called
                assert mock_logger.debug.called


class TestErrorPaths:
    """Test error handling and edge cases."""

    def setup_method(self):
        """Create temporary workspace for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.workspace = Path(self.temp_dir)
        self.manager = StateManager(self.workspace)

    def teardown_method(self):
        """Clean up temporary workspace after each test."""
        shutil.rmtree(self.temp_dir)

    def test_load_missing_file_error_message(self):
        """Test that load() provides helpful error message when file missing."""
        with pytest.raises(FileNotFoundError) as exc_info:
            self.manager.load()

        assert "State file not found" in str(exc_info.value)
        assert str(self.manager.state_path) in str(exc_info.value)

    def test_create_raises_error_if_exists(self):
        """Test that create() raises error if state already exists."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )

        # Create first time - should work
        self.manager.create(state)

        # Create second time - should raise error
        with pytest.raises(FileExistsError) as exc_info:
            self.manager.create(state)

        assert "already exists" in str(exc_info.value)

    def test_from_dict_missing_topic_raises_error(self):
        """Test that from_dict raises error when topic is missing."""
        invalid_data = {
            "experts": ["typescript"],
            "iteration": 1
        }

        with pytest.raises(ValueError) as exc_info:
            WorkspaceState.from_dict(invalid_data)

        assert "topic" in str(exc_info.value)

    def test_from_dict_empty_topic_raises_error(self):
        """Test that from_dict raises error when topic is empty."""
        invalid_data = {
            "topic": "",
            "experts": ["typescript"],
            "iteration": 1
        }

        with pytest.raises(ValueError) as exc_info:
            WorkspaceState.from_dict(invalid_data)

        assert "topic" in str(exc_info.value)

    def test_is_phase_complete_no_state_file(self):
        """Test is_phase_complete returns False when no state file."""
        result = self.manager.is_phase_complete("consolidating")
        assert result is False

    def test_is_phase_complete_corrupted_state(self):
        """Test is_phase_complete handles corrupted state gracefully."""
        # Write corrupted JSON
        self.manager.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.manager.state_path.write_text("{invalid json")

        result = self.manager.is_phase_complete("consolidating")
        assert result is False

    def test_get_phase_result_no_state_file(self):
        """Test get_phase_result returns None when no state file."""
        result = self.manager.get_phase_result("consolidating")
        assert result is None

    def test_get_phase_result_corrupted_state(self):
        """Test get_phase_result handles corrupted state gracefully."""
        # Write corrupted JSON
        self.manager.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.manager.state_path.write_text("{invalid json")

        result = self.manager.get_phase_result("consolidating")
        assert result is None

    def test_get_script_owner_no_state_file(self):
        """Test get_script_owner returns None when no state file."""
        result = self.manager.get_script_owner("test_script")
        assert result is None

    def test_get_script_owner_corrupted_state(self):
        """Test get_script_owner handles corrupted state gracefully."""
        # Write corrupted JSON
        self.manager.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.manager.state_path.write_text("{invalid json")

        result = self.manager.get_script_owner("test_script")
        assert result is None

    def test_get_completed_scripts_no_state_file(self):
        """Test get_completed_scripts returns empty dict when no state file."""
        result = self.manager.get_completed_scripts()
        assert result == {}

    def test_get_completed_scripts_corrupted_state(self):
        """Test get_completed_scripts handles corrupted state gracefully."""
        # Write corrupted JSON
        self.manager.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.manager.state_path.write_text("{invalid json")

        result = self.manager.get_completed_scripts()
        assert result == {}

    def test_set_phase_invalid_raises_error(self):
        """Test set_phase raises error for invalid phase."""
        state = WorkspaceState(
            topic="Test",
            experts=["typescript"],
            iteration=1
        )
        self.manager.save(state)

        with pytest.raises(ValueError) as exc_info:
            self.manager.set_phase("invalid_phase")

        assert "Invalid phase" in str(exc_info.value)
        assert "invalid_phase" in str(exc_info.value)

    def test_register_script_intent_exception_handling(self):
        """Test register_script_intent returns False on exception."""
        # Don't create state file - should cause exception
        result = self.manager.register_script_intent("typescript", "test_script")

        # Should handle exception gracefully and return False
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
