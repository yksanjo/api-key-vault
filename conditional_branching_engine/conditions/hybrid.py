"""
Hybrid condition class for the Conditional Branching Engine.

Combines fast filters (keyword, regex) with expensive analysis (LLM)
for efficient routing decisions.
"""

from typing import Any, Callable, Optional

from .base import Condition, ConditionResult


class HybridCondition(Condition):
    """
    Condition that combines fast filters with expensive analysis.
    
    Uses a two-stage evaluation approach:
    1. Fast pre-filter using lightweight conditions (keyword, regex)
    2. Expensive analysis (LLM) only if pre-filter passes
    
    This provides the best of both worlds: speed for common cases
    with sophisticated analysis for edge cases.
    
    Example:
        # First filter by keyword, then use LLM for nuance
        cond = HybridCondition(
            fast_conditions=[
                KeywordCondition(keyword="complaint", match_any=True),
                KeywordCondition(keywords=["refund", "cancel"], match_any=True),
            ],
            slow_condition=LLMCondition(
                llm=llm,
                prompt="Is the customer expressing frustration? Answer yes or no."
            ),
            name="frustration_detector"
        )
    """
    
    def __init__(
        self,
        fast_conditions: list[Condition],
        slow_condition: Condition,
        fast_threshold: float = 1.0,
        use_slow_on_uncertain: bool = True,
        name: str = ""
    ):
        """
        Initialize hybrid condition.
        
        Args:
            fast_conditions: List of fast conditions for pre-filtering.
            slow_condition: The expensive condition to evaluate if pre-filter passes.
            fast_threshold: Minimum confidence from fast conditions to proceed.
            use_slow_on_uncertain: If True, use slow condition when fast is uncertain.
            name: Optional name for this condition.
        """
        super().__init__(name)
        self.fast_conditions = fast_conditions
        self.slow_condition = slow_condition
        self.fast_threshold = fast_threshold
        self.use_slow_on_uncertain = use_slow_on_uncertain
    
    def evaluate(self, message: Any) -> ConditionResult:
        """Evaluate using the hybrid approach."""
        # Stage 1: Fast pre-filter
        fast_results = []
        for condition in self.fast_conditions:
            result = condition.evaluate(message)
            fast_results.append(result)
        
        # Combine fast results
        combined_fast = self._combine_fast_results(fast_results)
        
        # Check if we should skip slow evaluation
        if combined_fast.confidence < self.fast_threshold:
            # Fast conditions didn't pass strongly enough
            if not self.use_slow_on_uncertain:
                return combined_fast
        
        # Stage 2: Slow evaluation (if needed)
        slow_result = self.slow_condition.evaluate(message)
        
        # If slow condition passed, return its result
        if slow_result.matched:
            return slow_result
        
        # If slow didn't match but fast did with high confidence, trust fast
        if combined_fast.matched and combined_fast.confidence >= self.fast_threshold:
            return combined_fast
        
        # Default to slow result
        return slow_result
    
    def _combine_fast_results(self, results: list[ConditionResult]) -> ConditionResult:
        """Combine multiple fast condition results."""
        if not results:
            return ConditionResult(matched=False, confidence=0.0)
        
        # Check if any matched
        matched_results = [r for r in results if r.matched]
        
        if not matched_results:
            return ConditionResult(
                matched=False,
                confidence=0.0,
                reason="No fast conditions matched"
            )
        
        # Use the highest confidence match
        best_match = max(matched_results, key=lambda r: r.confidence)
        
        return ConditionResult(
            matched=best_match.matched,
            confidence=best_match.confidence,
            reason=f"Fast match: {best_match.reason}",
            metadata={"fast_results": [r.reason for r in results]}
        )
    
    def __repr__(self) -> str:
        return f"HybridCondition(fast_conditions={len(self.fast_conditions)}, slow={self.slow_condition.name})"


class ThresholdCondition(Condition):
    """
    Condition that checks if a numeric value exceeds a threshold.
    
    Useful for score-based routing decisions.
    
    Example:
        # Route high-confidence messages to special handler
        cond = ThresholdCondition(
            field="metadata.score",
            threshold=0.7,
            comparison=">",
            name="high_score"
        )
    """
    
    def __init__(
        self,
        field: str,
        threshold: float,
        comparison: str = ">",
        name: str = ""
    ):
        """
        Initialize threshold condition.
        
        Args:
            field: Dot-notation path to the numeric field (e.g., "metadata.score").
            threshold: The threshold value to compare against.
            comparison: Comparison operator: ">", "<", ">=", "<=", "==", "!=".
            name: Optional name for this condition.
        """
        super().__init__(name)
        self.field = field
        self.threshold = threshold
        self.comparison = comparison
    
    def evaluate(self, message: Any) -> ConditionResult:
        """Check if the field value meets the threshold."""
        value = self._get_field_value(message, self.field)
        
        if value is None:
            return ConditionResult(
                matched=False,
                confidence=0.0,
                reason=f"Could not find field: {self.field}"
            )
        
        try:
            value = float(value)
        except (TypeError, ValueError):
            return ConditionResult(
                matched=False,
                confidence=0.0,
                reason=f"Field value is not numeric: {value}"
            )
        
        # Perform comparison
        matched = self._compare(value, self.threshold)
        
        return ConditionResult(
            matched=matched,
            confidence=1.0 if matched else 0.0,
            reason=f"{value} {self.comparison} {self.threshold}",
            metadata={"value": value, "threshold": self.threshold}
        )
    
    def _get_field_value(self, message: Any, field: str) -> Any:
        """Get a value from nested object using dot notation."""
        parts = field.split('.')
        current = message
        
        for part in parts:
            if current is None:
                return None
            if isinstance(current, dict):
                current = current.get(part)
            elif hasattr(current, part):
                current = getattr(current, part)
            else:
                return None
        
        return current
    
    def _compare(self, value: float, threshold: float) -> bool:
        """Perform the comparison."""
        ops = {
            ">": lambda v, t: v > t,
            "<": lambda v, t: v < t,
            ">=": lambda v, t: v >= t,
            "<=": lambda v, t: v <= t,
            "==": lambda v, t: v == t,
            "!=": lambda v, t: v != t,
        }
        
        op = ops.get(self.comparison)
        if op is None:
            raise ValueError(f"Invalid comparison operator: {self.comparison}")
        
        return op(value, threshold)
    
    def __repr__(self) -> str:
        return f"ThresholdCondition(field='{self.field}', threshold={self.threshold})"
