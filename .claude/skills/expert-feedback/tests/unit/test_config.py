"""
Unit tests for configuration system (config.py).

Tests configuration loading, environment variable overrides, validation,
and singleton behavior.
"""
import os
import pytest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from config import SkillConfig, get_config, reset_config, get_config_with_overrides


@pytest.fixture(autouse=True)
def reset_config_singleton():
    """Reset config singleton and clean environment vars before each test to ensure test isolation."""
    # Save original environment
    original_env = {}
    expert_env_vars = [k for k in os.environ.keys() if k.startswith('EXPERT_')]
    for key in expert_env_vars:
        original_env[key] = os.environ[key]

    reset_config()
    yield
    reset_config()

    # Restore original environment
    for key in [k for k in os.environ.keys() if k.startswith('EXPERT_')]:
        if key in original_env:
            os.environ[key] = original_env[key]
        else:
            del os.environ[key]


class TestSkillConfig:
    """Test SkillConfig dataclass."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = SkillConfig()

        assert config.convergence_target == 80
        assert config.max_questions_per_iteration is None  # Removed limit
        assert config.default_expert_count == 7
        assert config.max_iterations == 3
        assert config.expert_timeout_seconds == 900
        assert config.expert_warning_first == 600
        assert config.expert_warning_interval == 60
        assert config.repo_staleness_days == 7
        assert config.auto_update_repos is True
        assert config.workspace_base == Path(".workspace")
        assert config.organize_by_iteration is True
        assert config.default_mode == "review"

    def test_validation_convergence_target(self):
        """Test convergence target validation."""
        # Valid values
        config = SkillConfig(convergence_target=50)
        config.validate()

        config = SkillConfig(convergence_target=100)
        config.validate()

        # Invalid values
        with pytest.raises(ValueError, match="convergence_target must be between 1 and 100"):
            config = SkillConfig(convergence_target=0)
            config.validate()

        with pytest.raises(ValueError, match="convergence_target must be between 1 and 100"):
            config = SkillConfig(convergence_target=101)
            config.validate()

    def test_validation_timeout(self):
        """Test timeout validation."""
        # Valid
        config = SkillConfig(expert_timeout_seconds=300, expert_warning_first=180)
        config.validate()

        # Invalid - negative timeout
        with pytest.raises(ValueError, match="expert_timeout_seconds must be positive"):
            config = SkillConfig(expert_timeout_seconds=-1)
            config.validate()

        # Invalid - warning after timeout
        with pytest.raises(ValueError, match="expert_warning_first .* must be less than timeout"):
            config = SkillConfig(expert_timeout_seconds=300, expert_warning_first=400)
            config.validate()

    def test_validation_mode(self):
        """Test mode validation."""
        # Valid modes
        for mode in ["review", "adr", "create", "improve"]:
            config = SkillConfig(default_mode=mode)
            config.validate()

        # Invalid mode
        with pytest.raises(ValueError, match="default_mode must be one of"):
            config = SkillConfig(default_mode="invalid")
            config.validate()

    def test_validation_iterations(self):
        """Test iterations validation."""
        # Valid
        config = SkillConfig(max_iterations=5)
        config.validate()

        # Invalid
        with pytest.raises(ValueError, match="max_iterations must be positive"):
            config = SkillConfig(max_iterations=0)
            config.validate()


class TestConfigLoading:
    """Test configuration loading from environment."""

    def setup_method(self):
        """Reset config before each test."""
        reset_config()

    def teardown_method(self):
        """Clean up environment variables after each test."""
        env_vars = [
            "EXPERT_CONVERGENCE_TARGET",
            "EXPERT_TIMEOUT",
            "EXPERT_WARNING_FIRST",
            "EXPERT_DEFAULT_COUNT",
            "EXPERT_MAX_ITERATIONS",
            "EXPERT_DEFAULT_MODE",
            "EXPERT_VERBOSE_LOGGING",
            "EXPERT_SHOW_WORKSPACE_LINK",
        ]
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
        reset_config()

    def test_from_env_defaults(self):
        """Test loading defaults when no env vars set."""
        config = SkillConfig.from_env()

        assert config.convergence_target == 80
        assert config.expert_timeout_seconds == 900
        assert config.default_expert_count == 7

    def test_from_env_overrides(self):
        """Test environment variable overrides."""
        os.environ["EXPERT_CONVERGENCE_TARGET"] = "70"
        os.environ["EXPERT_TIMEOUT"] = "600"
        os.environ["EXPERT_DEFAULT_COUNT"] = "5"
        os.environ["EXPERT_DEFAULT_MODE"] = "improve"

        config = SkillConfig.from_env()

        assert config.convergence_target == 70
        assert config.expert_timeout_seconds == 600
        assert config.default_expert_count == 5
        assert config.default_mode == "improve"

    def test_from_env_boolean_parsing(self):
        """Test boolean environment variable parsing."""
        # True values
        os.environ["EXPERT_VERBOSE_LOGGING"] = "true"
        os.environ["EXPERT_SHOW_WORKSPACE_LINK"] = "True"

        config = SkillConfig.from_env()

        assert config.verbose_logging is True
        assert config.show_workspace_link is True

        # False values
        os.environ["EXPERT_VERBOSE_LOGGING"] = "false"
        os.environ["EXPERT_SHOW_WORKSPACE_LINK"] = "False"

        reset_config()
        config = SkillConfig.from_env()

        assert config.verbose_logging is False
        assert config.show_workspace_link is False


class TestConfigSingleton:
    """Test singleton behavior of get_config()."""

    def setup_method(self):
        """Reset config before each test."""
        reset_config()

    def teardown_method(self):
        """Clean up after each test."""
        reset_config()

    def test_singleton_returns_same_instance(self):
        """Test that get_config() returns the same instance."""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2

    def test_reset_config_clears_singleton(self):
        """Test that reset_config() clears the singleton."""
        config1 = get_config()
        reset_config()
        config2 = get_config()

        assert config1 is not config2

    def test_get_config_validates(self):
        """Test that get_config() validates configuration."""
        os.environ["EXPERT_CONVERGENCE_TARGET"] = "150"  # Invalid

        with pytest.raises(ValueError, match="convergence_target must be between 1 and 100"):
            get_config()


class TestConfigOverrides:
    """Test per-session configuration overrides."""

    def setup_method(self):
        """Reset config before each test."""
        reset_config()

    def teardown_method(self):
        """Clean up after each test."""
        reset_config()

    def test_get_config_with_overrides(self):
        """Test creating config with overrides."""
        base_config = get_config()

        # Create config with override
        config = get_config_with_overrides(convergence_target=70)

        assert config.convergence_target == 70
        assert base_config.convergence_target == 80  # Singleton unchanged

    def test_overrides_validation(self):
        """Test that overrides are validated."""
        with pytest.raises(ValueError, match="convergence_target must be between 1 and 100"):
            get_config_with_overrides(convergence_target=150)

    def test_multiple_overrides(self):
        """Test multiple overrides at once."""
        config = get_config_with_overrides(
            convergence_target=70,
            expert_timeout_seconds=700,
            default_expert_count=5
        )

        assert config.convergence_target == 70
        assert config.expert_timeout_seconds == 700
        assert config.default_expert_count == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
