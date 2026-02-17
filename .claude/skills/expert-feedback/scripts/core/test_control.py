"""
Test control mechanism for deterministic recording generation.

This module provides test control instructions that can be injected into
agent prompts during recording mode to ensure specific behaviors are triggered.

CRITICAL: Test controls are ONLY active during recording mode (EXPERT_FEEDBACK_TEST_MODE=record).
They are NEVER used during replay mode or production usage.

Why test controls are needed:
- Without controls, agents may or may not find concerns (non-deterministic)
- We need to reliably test all workflow branches (concerns, no concerns, disagreements)
- Controls ensure comprehensive test coverage of all scenarios

Ethical considerations:
- Controls are clearly marked as "TEST RECORDING MODE"
- Controls are only for testing infrastructure, not production use
- Controls help ensure the system handles all real-world scenarios correctly
"""

import os
from typing import Dict, Any, Optional


# Template strings for different test control types
CONTROL_TEMPLATES = {
    "force_concerns": """
==================================================
TEST RECORDING MODE: This is a test recording session.
==================================================

For testing purposes, please identify significant concerns in the artifact 
related to: {concern_types}.

Generate {num_concerns} distinct concerns that would require addressing before 
production deployment. These concerns should be realistic and actionable.

Focus on concerns that are:
- Specific and clearly explained
- Backed by technical reasoning
- Addressable with concrete improvements

This is necessary for testing the concern resolution workflow.
==================================================
""",

    "force_clean_analysis": """
==================================================
TEST RECORDING MODE: This is a test recording session.
==================================================

For testing purposes, analyze this artifact and find it to be generally 
well-designed with no major concerns that would block production deployment.

You may note minor suggestions or optional improvements, but do not identify 
any critical issues or blocking concerns.

This is necessary for testing the clean approval workflow.
==================================================
""",

    "force_disagreement": """
==================================================
TEST RECORDING MODE: This is a test recording session.
==================================================

For testing purposes, disagree with the other expert's approach to {disagreement_area}.

Provide an alternative perspective that differs from their recommendation. 
Your disagreement should be:
- Based on valid technical reasoning
- Focused on a different approach or priority
- Respectful but clearly distinct from the other expert's view

This is necessary for testing the disagreement resolution mechanism.
==================================================
"""
}


def format_control_instructions(test_control: Dict[str, Any]) -> str:
    """
    Format test control instructions for injection into agent prompts.
    
    Args:
        test_control: Dictionary with control parameters. Examples:
            - {"force_concerns": True, "concern_types": ["validation", "error_handling"], "num_concerns": 4}
            - {"force_clean_analysis": True}
            - {"force_disagreement": True, "disagreement_area": "validation approach"}
    
    Returns:
        Formatted control instruction string, or empty string if no controls
    
    Notes:
        - Only formats controls when in recording mode (EXPERT_FEEDBACK_TEST_MODE=record)
        - Returns empty string in all other modes (replay, production)
        - Controls are clearly marked as "TEST RECORDING MODE"
    """
    if not test_control:
        return ""
    
    # Check if we're in recording mode
    test_mode = os.environ.get("EXPERT_FEEDBACK_TEST_MODE", "").lower()
    if test_mode != "record":
        # Not in recording mode - don't inject any controls
        return ""
    
    # Check if test controls are explicitly enabled
    control_mode = os.environ.get("TEST_CONTROL_MODE", "").lower()
    if control_mode != "enabled":
        # Test controls not enabled - don't inject
        return ""
    
    # Determine which control to apply
    if test_control.get("force_concerns"):
        template = CONTROL_TEMPLATES["force_concerns"]
        concern_types = test_control.get("concern_types", ["validation", "error_handling", "type_safety"])
        num_concerns = test_control.get("num_concerns", 3)
        
        # Format the template
        return template.format(
            concern_types=", ".join(concern_types),
            num_concerns=num_concerns
        )
    
    elif test_control.get("force_clean_analysis"):
        return CONTROL_TEMPLATES["force_clean_analysis"]
    
    elif test_control.get("force_disagreement"):
        template = CONTROL_TEMPLATES["force_disagreement"]
        disagreement_area = test_control.get("disagreement_area", "implementation approach")
        
        return template.format(
            disagreement_area=disagreement_area
        )
    
    else:
        # Unknown control type
        return ""


def inject_test_control(base_prompt: str, test_control: Optional[Dict[str, Any]]) -> str:
    """
    Inject test control instructions into a prompt.
    
    This is a convenience function that combines prompt building with control injection.
    
    Args:
        base_prompt: The base prompt without controls
        test_control: Test control parameters (see format_control_instructions)
    
    Returns:
        Prompt with test controls injected (if in recording mode), or base prompt unchanged
    
    Example:
        >>> base_prompt = "Review this code: ..."
        >>> test_control = {"force_concerns": True, "num_concerns": 3}
        >>> final_prompt = inject_test_control(base_prompt, test_control)
        # In recording mode with TEST_CONTROL_MODE=enabled:
        # Returns: base_prompt + test control instructions
        # In other modes: Returns base_prompt unchanged
    """
    if not test_control:
        return base_prompt
    
    control_instructions = format_control_instructions(test_control)
    if not control_instructions:
        return base_prompt
    
    # Inject controls at the end of the prompt
    return f"{base_prompt}\n\n{control_instructions}"


# Export public API
__all__ = [
    "CONTROL_TEMPLATES",
    "format_control_instructions",
    "inject_test_control"
]
