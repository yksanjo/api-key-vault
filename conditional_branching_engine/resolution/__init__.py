"""Resolution module for the Conditional Branching Engine."""

from .deterministic import DeterministicResolver
from .probabilistic import ProbabilisticResolver

__all__ = [
    "DeterministicResolver",
    "ProbabilisticResolver",
]
