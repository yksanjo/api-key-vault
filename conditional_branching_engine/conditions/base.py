"""
Base condition classes for the Conditional Branching Engine.

Defines the abstract base class for all condition types and the result
structure for condition evaluation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ConditionResult:
    """
    Result of evaluating a condition.
    
    Attributes:
        matched: Whether the condition evaluated to True.
        confidence: A confidence score (0.0-1.0) for the match.
        reason: Human-readable explanation of why the condition matched or not.
        metadata: Additional metadata from the evaluation.
    """
    matched: bool
    confidence: float = 1.0
    reason: str = ""
    metadata: dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        # Clamp confidence to valid range
        self.confidence = max(0.0, min(1.0, self.confidence))


class Condition(ABC):
    """
    Abstract base class for all condition types.
    
    All condition implementations should inherit from this class
    and implement the evaluate method.
    """
    
    def __init__(self, name: str = ""):
        """
        Initialize the condition.
        
        Args:
            name: Optional name/identifier for this condition.
        """
        self.name = name or self.__class__.__name__
    
    @abstractmethod
    def evaluate(self, message: Any) -> ConditionResult:
        """
        Evaluate the condition against a message.
        
        Args:
            message: The message to evaluate.
            
        Returns:
            ConditionResult with the evaluation outcome.
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __call__(self, message: Any) -> ConditionResult:
        """Allow calling the condition directly."""
        return self.evaluate(message)


class CompoundCondition(Condition):
    """
    A condition that combines multiple conditions with AND/OR logic.
    
    Example:
        # Match if both keyword AND score threshold are met
        cond = CompoundCondition(
            conditions=[keyword_cond, score_cond],
            operator="AND"
        )
    """
    
    def __init__(
        self,
        conditions: list[Condition],
        operator: str = "AND",
        name: str = ""
    ):
        """
        Initialize compound condition.
        
        Args:
            conditions: List of conditions to combine.
            operator: "AND" for all must match, "OR" for any must match.
            name: Optional name for this compound condition.
        """
        super().__init__(name)
        self.conditions = conditions
        self.operator = operator.upper()
        
        if self.operator not in ("AND", "OR"):
            raise ValueError("Operator must be 'AND' or 'OR'")
    
    def evaluate(self, message: Any) -> ConditionResult:
        """Evaluate all conditions and combine results."""
        if not self.conditions:
            return ConditionResult(matched=False, reason="No conditions to evaluate")
        
        results = [cond.evaluate(message) for cond in self.conditions]
        
        if self.operator == "AND":
            all_matched = all(r.matched for r in results)
            avg_confidence = sum(r.confidence for r in results) / len(results)
            return ConditionResult(
                matched=all_matched,
                confidence=avg_confidence,
                reason=f"AND: {'all matched' if all_matched else 'not all matched'}"
            )
        else:  # OR
            any_matched = any(r.matched for r in results)
            # For OR, use max confidence of matching conditions
            matching_confidences = [r.confidence for r in results if r.matched]
            max_confidence = max(matching_confidences) if matching_confidences else 0.0
            return ConditionResult(
                matched=any_matched,
                confidence=max_confidence,
                reason=f"OR: {'at least one matched' if any_matched else 'none matched'}"
            )
