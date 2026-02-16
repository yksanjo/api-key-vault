"""Core module for Conditional Branching Engine."""

from .message import Message, MessageMetadata
from .workflow import WorkflowBuilder, ConditionalEdge, GraphNode

__all__ = [
    "Message",
    "MessageMetadata",
    "WorkflowBuilder",
    "ConditionalEdge",
    "GraphNode",
]
