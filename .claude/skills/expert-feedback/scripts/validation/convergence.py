"""
Explicit convergence calculation for expert-feedback workflow.

This module provides programmatic convergence calculation to make the logic
visible, testable, and debuggable. It can validate LLM-calculated convergence
and eventually replace it.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any


@dataclass
class ConvergenceMetrics:
    """
    Convergence calculation results.

    Convergence measures how much experts agree on recommendations:
    - High agreement (≥75% experts): Recommendation has strong consensus
    - Partial agreement (50-74% experts): Recommendation has moderate support
    - Low agreement (<50% experts): Recommendation lacks consensus

    The convergence percentage weighs these levels:
    - High agreement: 100% weight
    - Partial agreement: 50% weight
    - Low agreement: 0% weight
    """

    convergence_percent: int
    high_agreement_count: int
    partial_agreement_count: int
    low_agreement_count: int
    total_recommendations: int
    consensus_reached: bool
    target_percent: int

    def __post_init__(self):
        """Validate convergence metrics."""
        if not (0 <= self.convergence_percent <= 100):
            raise ValueError(
                f"Invalid convergence: {self.convergence_percent}% "
                f"(must be 0-100)"
            )

        total = (self.high_agreement_count +
                self.partial_agreement_count +
                self.low_agreement_count)

        if total != self.total_recommendations:
            raise ValueError(
                f"Agreement counts ({total}) don't match total "
                f"recommendations ({self.total_recommendations})"
            )

    def __str__(self) -> str:
        """Human-readable summary."""
        return (
            f"Convergence: {self.convergence_percent}% "
            f"(high: {self.high_agreement_count}, "
            f"partial: {self.partial_agreement_count}, "
            f"low: {self.low_agreement_count})"
        )


def calculate_convergence(
    recommendations: List[Dict],
    expert_count: int,
    target_percent: int = 80,
    logger: Optional[Any] = None
) -> ConvergenceMetrics:
    """
    Calculate convergence from recommendation agreement levels.

    Formula:
    - High agreement (≥75% experts): 100% weight per recommendation
    - Partial agreement (50-74% experts): 50% weight per recommendation
    - Low agreement (<50% experts): 0% weight per recommendation

    Convergence % = (high*100 + partial*50) / total_recommendations

    Args:
        recommendations: List of recommendations with agreement_level field
        expert_count: Total number of experts in this iteration
        target_percent: Target convergence threshold (default: 80)
        logger: Optional logger for detailed calculation logging

    Returns:
        ConvergenceMetrics with calculated values

    Example:
        recommendations = [
            {"id": "rec-001", "agreement_level": "high"},    # 100% weight
            {"id": "rec-002", "agreement_level": "partial"}, # 50% weight
            {"id": "rec-003", "agreement_level": "low"}      # 0% weight
        ]
        metrics = calculate_convergence(recommendations, expert_count=5)
        # metrics.convergence_percent = (100 + 50 + 0) / 3 = 50%

    Raises:
        ValueError: If recommendations have invalid agreement_level
    """
    if logger:
        logger.info(
            f"Calculating convergence for {len(recommendations)} recommendations "
            f"from {expert_count} experts (target: {target_percent}%)"
        )

    if not recommendations:
        if logger:
            logger.info("No recommendations → 100% convergence (nothing to disagree on)")
        # No recommendations = perfect convergence (nothing to disagree on)
        return ConvergenceMetrics(
            convergence_percent=100,
            high_agreement_count=0,
            partial_agreement_count=0,
            low_agreement_count=0,
            total_recommendations=0,
            consensus_reached=True,
            target_percent=target_percent
        )

    # Count recommendations by agreement level
    high = 0
    partial = 0
    low = 0

    for i, rec in enumerate(recommendations):
        level = rec.get("agreement_level", "").lower()
        rec_id = rec.get("id", f"rec-{i}")

        if level == "high":
            high += 1
            if logger:
                logger.debug(f"  {rec_id}: HIGH agreement (≥75% experts)")
        elif level == "partial":
            partial += 1
            if logger:
                logger.debug(f"  {rec_id}: PARTIAL agreement (50-74% experts)")
        elif level == "low":
            low += 1
            if logger:
                logger.debug(f"  {rec_id}: LOW agreement (<50% experts)")
        else:
            if logger:
                logger.error(f"  {rec_id}: INVALID agreement_level '{level}'")
            raise ValueError(
                f"Invalid agreement_level: '{level}' for recommendation {rec_id}. "
                f"Must be 'high', 'partial', or 'low'"
            )

    total = len(recommendations)

    # Calculate weighted convergence
    # High = 100%, Partial = 50%, Low = 0%
    convergence = int((high * 100 + partial * 50) / total)

    consensus = convergence >= target_percent

    if logger:
        logger.info(
            f"Convergence calculation complete: {convergence}% "
            f"(high={high}, partial={partial}, low={low})"
        )
        logger.info(
            f"  Formula: ({high} * 100 + {partial} * 50) / {total} = {convergence}%"
        )
        logger.info(
            f"  Consensus: {'YES (target met)' if consensus else f'NO (need {target_percent}%)'}"
        )

    return ConvergenceMetrics(
        convergence_percent=convergence,
        high_agreement_count=high,
        partial_agreement_count=partial,
        low_agreement_count=low,
        total_recommendations=total,
        consensus_reached=consensus,
        target_percent=target_percent
    )


def validate_llm_convergence(
    llm_convergence: int,
    programmatic_convergence: int,
    tolerance: int = 5,
    logger: Optional[Any] = None
) -> tuple[bool, str]:
    """
    Validate LLM-calculated convergence against programmatic calculation.

    This helps catch cases where the LLM miscalculates convergence or
    where our formula doesn't match the LLM's logic.

    Args:
        llm_convergence: Convergence calculated by LLM (0-100)
        programmatic_convergence: Convergence calculated programmatically (0-100)
        tolerance: Maximum acceptable difference in percentage points
        logger: Optional logger for validation logging

    Returns:
        (is_valid, message): True if difference is within tolerance, with explanation

    Example:
        is_valid, msg = validate_llm_convergence(
            llm_convergence=82,
            programmatic_convergence=80,
            tolerance=5
        )
        # is_valid = True, msg = "LLM convergence validated (diff: 2%)"
    """
    if logger:
        logger.info(
            f"Validating LLM convergence: LLM={llm_convergence}%, "
            f"programmatic={programmatic_convergence}%, tolerance=±{tolerance}%"
        )

    if not (0 <= llm_convergence <= 100):
        msg = f"Invalid LLM convergence: {llm_convergence}% (must be 0-100)"
        if logger:
            logger.error(msg)
        return False, msg

    if not (0 <= programmatic_convergence <= 100):
        msg = f"Invalid programmatic convergence: {programmatic_convergence}% (must be 0-100)"
        if logger:
            logger.error(msg)
        return False, msg

    diff = abs(llm_convergence - programmatic_convergence)

    if diff <= tolerance:
        msg = f"LLM convergence validated (diff: {diff}%)"
        if logger:
            logger.info(f"✓ Validation passed (diff: {diff}%)")
        return True, msg
    else:
        msg = (
            f"LLM convergence ({llm_convergence}%) differs from "
            f"programmatic ({programmatic_convergence}%) by {diff}% "
            f"(tolerance: {tolerance}%)"
        )
        if logger:
            logger.warning(
                f"✗ Validation failed: LLM={llm_convergence}%, "
                f"programmatic={programmatic_convergence}%, diff={diff}% (tolerance: {tolerance}%)"
            )
        return False, msg


def parse_recommendations_from_state(state: Dict) -> List[Dict]:
    """
    Extract recommendations with agreement levels from consolidated state.

    The state should contain a 'recommendations' field with structured data
    from the consolidation phase.

    Args:
        state: Consolidated state dictionary

    Returns:
        List of recommendations with agreement_level field

    Example state structure:
        {
            "recommendations": [
                {
                    "id": "rec-001",
                    "title": "Add input validation",
                    "agreement_level": "high",
                    "supporting_experts": ["security", "typescript", "dx"]
                }
            ]
        }
    """
    recommendations = state.get("recommendations", [])

    # Ensure each recommendation has required fields
    for rec in recommendations:
        if "agreement_level" not in rec:
            # Try to infer from supporting_experts count
            supporting_count = len(rec.get("supporting_experts", []))
            total_experts = state.get("expert_count", 5)

            if supporting_count >= int(total_experts * 0.75):
                rec["agreement_level"] = "high"
            elif supporting_count >= int(total_experts * 0.50):
                rec["agreement_level"] = "partial"
            else:
                rec["agreement_level"] = "low"

    return recommendations


def calculate_convergence_from_state(
    state: Dict,
    expert_count: int,
    target_percent: int = 80
) -> ConvergenceMetrics:
    """
    Calculate convergence directly from consolidated state.

    Convenience function that parses recommendations and calculates convergence
    in one step.

    Args:
        state: Consolidated state dictionary
        expert_count: Total number of experts
        target_percent: Target convergence threshold

    Returns:
        ConvergenceMetrics with calculated values
    """
    recommendations = parse_recommendations_from_state(state)
    return calculate_convergence(recommendations, expert_count, target_percent)
