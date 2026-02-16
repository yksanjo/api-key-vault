"""
Deterministic resolution for the Conditional Branching Engine.

Implements priority-based resolution where the highest priority
(lowest number) matching edge is always selected.
"""

from typing import Any, Optional

from ..core.workflow import ConditionalEdge
from ..core.message import Message


class DeterministicResolver:
    """
    Resolver that selects the highest priority matching edge.
    
    Resolution Logic:
    1. Evaluate all conditions and find matching edges
    2. Sort by priority (lower number = higher priority)
    3. Return the first match
    
    This provides predictable, reproducible routing behavior.
    
    Example:
        edges = [
            ConditionalEdge(destination="urgent", priority=1, condition=is_urgent),
            ConditionalEdge(destination="normal", priority=10, condition=is_normal),
        ]
        
        resolver = DeterministicResolver()
        selected = resolver.resolve(edges, message)  # Returns "urgent" or "normal"
    """
    
    def __init__(self, fallback_edge: Optional[str] = None):
        """
        Initialize deterministic resolver.
        
        Args:
            fallback_edge: Default destination if no conditions match.
        """
        self.fallback_edge = fallback_edge
    
    def resolve(
        self,
        edges: list[ConditionalEdge],
        message: Message
    ) -> Optional[str]:
        """
        Resolve the next destination using deterministic priority ordering.
        
        Args:
            edges: List of conditional edges to evaluate.
            message: The message to evaluate against conditions.
            
        Returns:
            The destination name of the selected edge, or fallback if provided.
        """
        if not edges:
            return self.fallback_edge
        
        # Find all matching edges
        matching_edges = []
        for edge in edges:
            try:
                if edge.evaluate(message):
                    matching_edges.append(edge)
            except Exception as e:
                # Skip edges that error during evaluation
                print(f"Error evaluating edge to {edge.destination}: {e}")
                continue
        
        if not matching_edges:
            return self.fallback_edge
        
        # Sort by priority (lowest first) and return the first match
        matching_edges.sort(key=lambda e: e.priority)
        
        return matching_edges[0].destination
    
    def resolve_with_confidence(
        self,
        edges: list[ConditionalEdge],
        message: Message
    ) -> tuple[Optional[str], float]:
        """
        Resolve with confidence score for the selected edge.
        
        Args:
            edges: List of conditional edges to evaluate.
            message: The message to evaluate against conditions.
            
        Returns:
            Tuple of (destination, confidence).
        """
        if not edges:
            return self.fallback_edge, 0.0
        
        # Find all matching edges
        matching_edges = []
        for edge in edges:
            try:
                if edge.evaluate(message):
                    matching_edges.append(edge)
            except Exception:
                continue
        
        if not matching_edges:
            return self.fallback_edge, 0.0
        
        # Sort by priority
        matching_edges.sort(key=lambda e: e.priority)
        
        # Return the highest priority match with confidence of 1.0
        return matching_edges[0].destination, 1.0


class PriorityResolver(DeterministicResolver):
    """
    Alias for DeterministicResolver for clarity.
    
    Use this when you want to emphasize the priority-based nature
    of the resolution.
    """
    pass
