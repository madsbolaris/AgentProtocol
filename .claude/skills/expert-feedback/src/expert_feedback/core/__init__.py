"""
Expert-feedback skill core utilities.

Phase 1.3 additions:
- cost.py: Accurate cost calculation for Claude API

Phase 1.4 additions:
- state_machine.py: Phase validation and transition management
"""
from .cost import (
    ModelTier,
    Pricing,
    PRICING_TABLE,
    TokenUsage,
    calculate_cost,
    estimate_session_cost,
    format_cost_estimate,
)
from .state_machine import (
    Phase,
    InvalidTransitionError,
    PhaseTransition,
    StateMachine,
)

__all__ = [
    # Cost calculation (Phase 1.3)
    "ModelTier",
    "Pricing",
    "PRICING_TABLE",
    "TokenUsage",
    "calculate_cost",
    "estimate_session_cost",
    "format_cost_estimate",
    # State machine (Phase 1.4)
    "Phase",
    "InvalidTransitionError",
    "PhaseTransition",
    "StateMachine",
]
