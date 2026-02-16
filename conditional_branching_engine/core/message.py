"""
Message and MessageMetadata classes for the Conditional Branching Engine.

These classes represent the data structure that flows through the workflow,
carrying content and metadata used for conditional routing decisions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class MessageMetadata:
    """
    Metadata associated with a message for routing decisions.
    
    Attributes:
        score: A float value (0.0-1.0) used for threshold-based routing.
        timestamp: When the message was created.
        source: Origin of the message (e.g., 'user', 'agent', 'api').
        context: Additional context dictionary for custom routing logic.
        tags: List of tags for categorization.
        priority: Message priority level (1-5, where 1 is highest).
    """
    score: float = 0.0
    timestamp: Optional[datetime] = None
    source: str = "unknown"
    context: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    priority: int = 3
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        # Clamp score to 0.0-1.0 range
        self.score = max(0.0, min(1.0, self.score))


@dataclass
class Message:
    """
    The primary data container that flows through the workflow.
    
    Attributes:
        content: The main content of the message (text, data, etc.).
        metadata: Metadata for routing decisions.
        sender: Who/what sent the message.
        conversation_id: Optional ID for tracking conversation context.
    """
    content: str
    metadata: MessageMetadata = field(default_factory=MessageMetadata)
    sender: str = "user"
    conversation_id: Optional[str] = None
    
    def __post_init__(self):
        # Ensure content is string
        if not isinstance(self.content, str):
            self.content = str(self.content)
    
    def has_keyword(self, keyword: str, case_sensitive: bool = False) -> bool:
        """Check if content contains a specific keyword."""
        if case_sensitive:
            return keyword in self.content
        return keyword.lower() in self.content.lower()
    
    def matches_pattern(self, pattern: str) -> bool:
        """Check if content matches a regex pattern."""
        import re
        return bool(re.search(pattern, self.content))
    
    def get_score(self) -> float:
        """Get the metadata score for threshold comparisons."""
        return self.metadata.score
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the message metadata."""
        if tag not in self.metadata.tags:
            self.metadata.tags.append(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if message has a specific tag."""
        return tag in self.metadata.tags


# Type alias for callable that processes messages
MessageProcessor = Any  # Can be a function or callable object
