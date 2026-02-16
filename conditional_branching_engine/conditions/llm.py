"""
LLM-based condition class for the Conditional Branching Engine.

Provides natural language interpretation for routing decisions using LLMs.
"""

from typing import Any, Callable, Optional

from .base import Condition, ConditionResult


class LLMCondition(Condition):
    """
    Condition that uses an LLM for natural language interpretation.
    
    Enables semantic understanding and contextual routing decisions
    that go beyond pattern matching.
    
    Example:
        # Route based on intent classification
        cond = LLMCondition(
            llm=openai_llm,
            prompt="Classify this message as 'urgent' or 'normal'",
            expected_labels=["urgent", "normal"],
            name="intent_classifier"
        )
        
        # Sentiment-based routing
        cond = LLMCondition(
            llm=llm,
            prompt="Is this message expressing frustration? Answer yes or no.",
            name="frustration_detector"
        )
    """
    
    def __init__(
        self,
        llm: Any,  # Can be any LLM interface (OpenAI, Anthropic, etc.)
        prompt: str,
        expected_labels: Optional[list[str]] = None,
        temperature: float = 0.0,
        name: str = ""
    ):
        """
        Initialize LLM condition.
        
        Args:
            llm: LLM instance with a chat/complete method.
            prompt: Prompt template for classification (use {content} placeholder).
            expected_labels: List of possible labels to match against.
            temperature: Temperature for LLM generation.
            name: Optional name for this condition.
        """
        super().__init__(name)
        self.llm = llm
        self.prompt = prompt
        self.expected_labels = expected_labels or []
        self.temperature = temperature
    
    def evaluate(self, message: Any) -> ConditionResult:
        """Use LLM to evaluate the message."""
        # Extract content from message
        content = self._extract_content(message)
        
        if content is None:
            return ConditionResult(
                matched=False,
                confidence=0.0,
                reason="Could not extract content from message"
            )
        
        # Build the full prompt
        full_prompt = self.prompt.format(content=content)
        
        try:
            # Call the LLM (assuming standard interface)
            response = self._call_llm(full_prompt)
            
            # Parse the response
            return self._parse_response(response, content)
            
        except Exception as e:
            return ConditionResult(
                matched=False,
                confidence=0.0,
                reason=f"LLM evaluation error: {str(e)}"
            )
    
    def _extract_content(self, message: Any) -> Optional[str]:
        """Extract string content from various message types."""
        if hasattr(message, 'content'):
            return str(message.content)
        elif isinstance(message, str):
            return message
        else:
            return str(message)
    
    def _call_llm(self, prompt: str) -> str:
        """Call the LLM and return the response text."""
        # Try different LLM interfaces
        if hasattr(self.llm, 'invoke'):
            # LangChain style
            return self.llm.invoke(prompt).content
        elif hasattr(self.llm, 'complete'):
            # OpenAI style
            return self.llm.complete(prompt).text
        elif hasattr(self.llm, 'generate'):
            # Generic generate
            result = self.llm.generate([prompt])
            return result.generations[0][0].text
        elif callable(self.llm):
            # Direct callable
            return self.llm(prompt)
        else:
            raise ValueError("LLM must have invoke, complete, or generate method, or be callable")
    
    def _parse_response(self, response: str, original_content: str) -> ConditionResult:
        """Parse the LLM response to determine match."""
        response_lower = response.lower().strip()
        
        # If we have expected labels, check for them
        if self.expected_labels:
            for label in self.expected_labels:
                if label.lower() in response_lower:
                    return ConditionResult(
                        matched=True,
                        confidence=1.0,
                        reason=f"Matched label: {label}",
                        metadata={"label": label, "llm_response": response}
                    )
            
            return ConditionResult(
                matched=False,
                confidence=0.5,
                reason=f"No expected label found in response: {response}",
                metadata={"llm_response": response}
            )
        
        # Otherwise, look for yes/no patterns
        yes_indicators = ['yes', 'true', 'correct', 'positive', '1', 'y']
        no_indicators = ['no', 'false', 'incorrect', 'negative', '0', 'n']
        
        for indicator in yes_indicators:
            if indicator in response_lower:
                return ConditionResult(
                    matched=True,
                    confidence=0.9,
                    reason=f"LLM indicated yes: {response}",
                    metadata={"llm_response": response}
                )
        
        for indicator in no_indicators:
            if indicator in response_lower:
                return ConditionResult(
                    matched=False,
                    confidence=0.9,
                    reason=f"LLM indicated no: {response}",
                    metadata={"llm_response": response}
                )
        
        # Fallback: treat as non-matching
        return ConditionResult(
            matched=False,
            confidence=0.5,
            reason=f"Could not parse LLM response: {response}",
            metadata={"llm_response": response}
        )
    
    def __repr__(self) -> str:
        return f"LLMCondition(name='{self.name}', prompt='{self.prompt[:50]}...')"


# Mock LLM for testing without actual API calls
class MockLLM:
    """A mock LLM for testing purposes."""
    
    def __init__(self, responses: dict[str, str] = None):
        """
        Initialize mock LLM.
        
        Args:
            responses: Dict mapping prompt patterns to responses.
        """
        self.responses = responses or {}
    
    def invoke(self, prompt: str) -> type('obj', (object,), {'content': 'yes'}):
        """Mock invoke method."""
        # Find matching response
        for pattern, response in self.responses.items():
            if pattern.lower() in prompt.lower():
                return type('obj', (object,), {'content': response})()
        
        # Default response
        return type('obj', (object,), {'content': 'no'})()
    
    def __call__(self, prompt: str) -> str:
        """Allow calling as a function."""
        return self.invoke(prompt).content
