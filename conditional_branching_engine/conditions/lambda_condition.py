"""
Lambda condition class for the Conditional Branching Engine.

Provides arbitrary Python computation for complex routing logic.
"""

from typing import Any, Callable, Optional

from .base import Condition, ConditionResult


class LambdaCondition(Condition):
    """
    Condition that uses a lambda/function for arbitrary evaluation.
    
    Enables sophisticated condition evaluation with full access to message
    content, metadata, and any other attribute through Python code.
    
    Example:
        # Route based on score threshold
        cond = LambdaCondition(
            func=lambda msg: msg.metadata.score > 0.7,
            name="high_score"
        )
        
        # Complex logic with multiple conditions
        cond = LambdaCondition(
            func=lambda msg: (
                "CATEGORY_A" in msg.content and 
                msg.metadata.score > 0.5 and
                msg.metadata.priority <= 2
            ),
            name="complex_route"
        )
    """
    
    def __init__(
        self,
        func: Callable[[Any], bool],
        name: str = "",
        description: str = ""
    ):
        """
        Initialize lambda condition.
        
        Args:
            func: A callable that takes a message and returns a boolean.
            name: Optional name for this condition.
            description: Optional human-readable description.
        """
        super().__init__(name)
        self.func = func
        self.description = description
    
    def evaluate(self, message: Any) -> ConditionResult:
        """Evaluate the lambda function against the message."""
        try:
            result = self.func(message)
            
            if isinstance(result, bool):
                return ConditionResult(
                    matched=result,
                    confidence=1.0 if result else 0.0,
                    reason=f"Lambda evaluation: {result}" if self.description else "Lambda returned result"
                )
            elif isinstance(result, tuple) and len(result) == 2:
                # Support (matched, confidence) return
                matched, confidence = result
                return ConditionResult(
                    matched=bool(matched),
                    confidence=float(confidence),
                    reason=self.description or "Lambda returned tuple"
                )
            else:
                return ConditionResult(
                    matched=bool(result),
                    reason="Lambda returned non-boolean"
                )
                
        except Exception as e:
            return ConditionResult(
                matched=False,
                confidence=0.0,
                reason=f"Lambda evaluation error: {str(e)}"
            )
    
    def __repr__(self) -> str:
        return f"LambdaCondition(name='{self.name}')"
    
    def __call__(self, message: Any) -> ConditionResult:
        """Allow direct calling of the condition."""
        return self.evaluate(message)
