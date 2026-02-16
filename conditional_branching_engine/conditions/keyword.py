"""
Keyword and Regex condition classes for the Conditional Branching Engine.

Provides fast text-based filtering using substring matching and regex patterns.
"""

import re
from typing import Any, Optional

from .base import Condition, ConditionResult


class KeywordCondition(Condition):
    """
    Condition that matches messages containing specific keywords.
    
    Supports both case-sensitive and case-insensitive matching,
    as well as multiple keywords with different match strategies.
    
    Example:
        # Match if message contains "CATEGORY_A"
        cond = KeywordCondition(keyword="CATEGORY_A")
        
        # Match if contains any of these keywords
        cond = KeywordCondition(keywords=["urgent", "asap", "emergency"], match_any=True)
    """
    
    def __init__(
        self,
        keyword: Optional[str] = None,
        keywords: Optional[list[str]] = None,
        case_sensitive: bool = False,
        match_any: bool = False,
        name: str = ""
    ):
        """
        Initialize keyword condition.
        
        Args:
            keyword: Single keyword to match.
            keywords: List of keywords to match.
            case_sensitive: Whether to match case-sensitively.
            match_any: If True, match any keyword (OR). If False, match all (AND).
            name: Optional name for this condition.
        """
        super().__init__(name)
        
        if keyword is not None:
            self.keywords = [keyword]
        elif keywords is not None:
            self.keywords = keywords
        else:
            raise ValueError("Either 'keyword' or 'keywords' must be provided")
        
        self.case_sensitive = case_sensitive
        self.match_any = match_any
    
    def evaluate(self, message: Any) -> ConditionResult:
        """Check if message content contains the keyword(s)."""
        # Extract content from message
        content = self._extract_content(message)
        
        if content is None:
            return ConditionResult(
                matched=False,
                confidence=0.0,
                reason="Could not extract content from message"
            )
        
        # Perform matching
        if self.match_any:
            return self._match_any(content)
        else:
            return self._match_all(content)
    
    def _extract_content(self, message: Any) -> Optional[str]:
        """Extract string content from various message types."""
        if hasattr(message, 'content'):
            return str(message.content)
        elif isinstance(message, str):
            return message
        else:
            return str(message)
    
    def _match_any(self, content: str) -> ConditionResult:
        """Match if any keyword is found."""
        matched_keywords = []
        
        for keyword in self.keywords:
            if self.case_sensitive:
                if keyword in content:
                    matched_keywords.append(keyword)
            else:
                if keyword.lower() in content.lower():
                    matched_keywords.append(keyword)
        
        if matched_keywords:
            confidence = len(matched_keywords) / len(self.keywords)
            return ConditionResult(
                matched=True,
                confidence=confidence,
                reason=f"Found keywords: {matched_keywords}",
                metadata={"matched_keywords": matched_keywords}
            )
        
        return ConditionResult(
            matched=False,
            reason=f"None of the keywords found: {self.keywords}"
        )
    
    def _match_all(self, content: str) -> ConditionResult:
        """Match if all keywords are found."""
        missing_keywords = []
        
        for keyword in self.keywords:
            if self.case_sensitive:
                if keyword not in content:
                    missing_keywords.append(keyword)
            else:
                if keyword.lower() not in content.lower():
                    missing_keywords.append(keyword)
        
        if not missing_keywords:
            return ConditionResult(
                matched=True,
                confidence=1.0,
                reason=f"All keywords found: {self.keywords}",
                metadata={"matched_keywords": self.keywords}
            )
        
        return ConditionResult(
            matched=False,
            reason=f"Missing keywords: {missing_keywords}"
        )
    
    def __repr__(self) -> str:
        return f"KeywordCondition(keywords={self.keywords}, case_sensitive={self.case_sensitive})"


class RegexCondition(Condition):
    """
    Condition that matches messages using regular expressions.
    
    Provides sophisticated pattern matching for routing decisions.
    
    Example:
        # Match email addresses
        cond = RegexCondition(pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Match specific format
        cond = RegexCondition(pattern=r'^(URGENT|ASAP):\s*')
    """
    
    def __init__(
        self,
        pattern: str,
        flags: int = 0,
        name: str = ""
    ):
        """
        Initialize regex condition.
        
        Args:
            pattern: Regular expression pattern to match.
            flags: Regex flags (e.g., re.IGNORECASE).
            name: Optional name for this condition.
        """
        super().__init__(name)
        self.pattern = pattern
        self.flags = flags
        self._compiled = re.compile(pattern, flags)
    
    def evaluate(self, message: Any) -> ConditionResult:
        """Check if message content matches the regex pattern."""
        content = self._extract_content(message)
        
        if content is None:
            return ConditionResult(
                matched=False,
                confidence=0.0,
                reason="Could not extract content from message"
            )
        
        match = self._compiled.search(content)
        
        if match:
            return ConditionResult(
                matched=True,
                confidence=1.0,
                reason=f"Pattern matched: {self.pattern}",
                metadata={"match": match.group(0), "span": match.span()}
            )
        
        return ConditionResult(
            matched=False,
            reason=f"Pattern not found: {self.pattern}"
        )
    
    def _extract_content(self, message: Any) -> Optional[str]:
        """Extract string content from various message types."""
        if hasattr(message, 'content'):
            return str(message.content)
        elif isinstance(message, str):
            return message
        else:
            return str(message)
    
    def __repr__(self) -> str:
        return f"RegexCondition(pattern='{self.pattern}')"
