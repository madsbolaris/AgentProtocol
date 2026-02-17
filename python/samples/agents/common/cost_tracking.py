"""
Cost tracking for OpenAI API with prompt caching support.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class OpenAIPricing:
    """Pricing for OpenAI models (per million tokens)."""
    input_per_million: float
    output_per_million: float
    cache_write_per_million: float  # Same as input for OpenAI
    cache_read_per_million: float   # 90% discount


# Pricing as of February 2026
OPENAI_PRICING = {
    "gpt-4o": OpenAIPricing(
        input_per_million=2.50,
        output_per_million=10.00,
        cache_write_per_million=2.50,  # Cache creation costs same as input
        cache_read_per_million=0.25    # 90% discount on cache reads
    ),
    "gpt-4o-mini": OpenAIPricing(
        input_per_million=0.150,
        output_per_million=0.600,
        cache_write_per_million=0.150,
        cache_read_per_million=0.015
    ),
}


@dataclass
class TokenUsage:
    """Token usage with cache support."""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0  # Tokens written to cache
    cache_read_tokens: int = 0      # Tokens read from cache

    @property
    def total_tokens(self) -> int:
        """Total tokens across all categories."""
        return (
            self.input_tokens +
            self.output_tokens +
            self.cache_creation_tokens +
            self.cache_read_tokens
        )

    @property
    def cache_hit_rate(self) -> float:
        """Percentage of input tokens from cache."""
        total_input = self.input_tokens + self.cache_creation_tokens + self.cache_read_tokens
        if total_input == 0:
            return 0.0
        return (self.cache_read_tokens / total_input) * 100

    def calculate_cost(self, model: str) -> float:
        """
        Calculate total cost in USD.

        Args:
            model: Model name (e.g., "gpt-4o", "gpt-4o-mini")

        Returns:
            Total cost in USD

        Raises:
            ValueError: If model is not in OPENAI_PRICING
        """
        pricing = OPENAI_PRICING.get(model)
        if not pricing:
            raise ValueError(f"Unknown model: {model}")

        cost = (
            (self.input_tokens / 1_000_000) * pricing.input_per_million +
            (self.output_tokens / 1_000_000) * pricing.output_per_million +
            (self.cache_creation_tokens / 1_000_000) * pricing.cache_write_per_million +
            (self.cache_read_tokens / 1_000_000) * pricing.cache_read_per_million
        )
        return cost

    def cache_savings_usd(self, model: str) -> float:
        """
        Calculate savings from cache hits vs full input cost.

        Args:
            model: Model name (e.g., "gpt-4o", "gpt-4o-mini")

        Returns:
            Savings in USD from cache hits

        Raises:
            ValueError: If model is not in OPENAI_PRICING
        """
        pricing = OPENAI_PRICING.get(model)
        if not pricing or self.cache_read_tokens == 0:
            return 0.0

        # Savings = (full input cost - discounted cache cost) for cache_read_tokens
        full_cost = (self.cache_read_tokens / 1_000_000) * pricing.input_per_million
        cache_cost = (self.cache_read_tokens / 1_000_000) * pricing.cache_read_per_million
        return full_cost - cache_cost

    def __str__(self) -> str:
        """String representation of token usage."""
        return (
            f"TokenUsage(input={self.input_tokens}, output={self.output_tokens}, "
            f"cache_creation={self.cache_creation_tokens}, cache_read={self.cache_read_tokens}, "
            f"hit_rate={self.cache_hit_rate:.1f}%)"
        )
