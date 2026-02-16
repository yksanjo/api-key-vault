"""
Probabilistic resolution for the Conditional Branching Engine.

Implements weighted random selection for handling ambiguous or
multi-matching edge scenarios.
"""

import random
from typing import Any, Optional

from ..core.workflow import ConditionalEdge
from ..core.message import Message


class ProbabilisticResolver:
    """
    Resolver that selects edges using weighted random selection.
    
    Resolution Logic:
    1. Evaluate all conditions and find matching edges
    2. Calculate weight sum for all matching edges
    3. Randomly select based on weight distribution
    
    This provides probabilistic routing for handling uncertainty
    and load distribution scenarios.
    
    Example:
        edges = [
            ConditionalEdge(destination="route_a", weight=1.0, condition=is_a),
            ConditionalEdge(destination="route_b", weight=3.0, condition=is_b),
        ]
        
        # route_b is 3x more likely to be selected when both match
        resolver = ProbabilisticResolver()
        selected = resolver.resolve(edges, message)
    """
    
    def __init__(
        self,
        fallback_edge: Optional[str] = None,
        seed: Optional[int] = None
    ):
        """
        Initialize probabilistic resolver.
        
        Args:
            fallback_edge: Default destination if no conditions match.
            seed: Optional random seed for reproducible results.
        """
        self.fallback_edge = fallback_edge
        self.seed = seed
        if seed is not None:
            random.seed(seed)
    
    def resolve(
        self,
        edges: list[ConditionalEdge],
        message: Message
    ) -> Optional[str]:
        """
        Resolve the next destination using weighted random selection.
        
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
        
        # Calculate total weight
        total_weight = sum(edge.weight for edge in matching_edges)
        
        if total_weight <= 0:
            return self.fallback_edge
        
        # Weighted random selection
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for edge in matching_edges:
            cumulative += edge.weight
            if r <= cumulative:
                return edge.destination
        
        # Fallback to last edge (shouldn't normally be reached)
        return matching_edges[-1].destination
    
    def resolve_with_confidence(
        self,
        edges: list[ConditionalEdge],
        message: Message
    ) -> tuple[Optional[str], float]:
        """
        Resolve with confidence based on edge weight.
        
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
        
        # Calculate total weight
        total_weight = sum(edge.weight for edge in matching_edges)
        
        if total_weight <= 0:
            return self.fallback_edge, 0.0
        
        # Weighted random selection
        r = random.uniform(0, total_weight)
        cumulative = 0
        
        for edge in matching_edges:
            cumulative += edge.weight
            if r <= cumulative:
                # Confidence is the proportion of this edge's weight
                confidence = edge.weight / total_weight
                return edge.destination, confidence
        
        return matching_edges[-1].destination, 0.0


class WeightedResolver(ProbabilisticResolver):
    """
    Alias for ProbabilisticResolver for clarity.
    
    Use this when you want to emphasize the weighted nature
    of the resolution.
    """
    pass


class LoadBalancingResolver(ProbabilisticResolver):
    """
    A probabilistic resolver optimized for load balancing.
    
    This resolver uses equal weights by default, distributing
    traffic evenly across all matching paths.
    
    Example:
        # Distribute evenly across handlers
        resolver = LoadBalancingResolver()
        selected = resolver.resolve(edges, message)
    """
    
    def __init__(
        self,
        fallback_edge: Optional[str] = None,
        seed: Optional[int] = None,
        normalize_weights: bool = True
    ):
        """
        Initialize load balancing resolver.
        
        Args:
            fallback_edge: Default destination if no conditions match.
            seed: Optional random seed for reproducible results.
            normalize_weights: If True, normalize weights to be equal.
        """
        super().__init__(fallback_edge, seed)
        self.normalize_weights = normalize_weights
    
    def resolve(
        self,
        edges: list[ConditionalEdge],
        message: Message
    ) -> Optional[str]:
        """Resolve using equal weights for load balancing."""
        if not edges:
            return self.fallback_edge
        
        # If normalization is enabled, create copies with equal weights
        if self.normalize_weights:
            equal_weight_edges = [
                ConditionalEdge(
                    destination=edge.destination,
                    condition=edge.condition,
                    weight=1.0,  # Equal weight
                    priority=edge.priority,
                    description=edge.description
                )
                for edge in edges
            ]
            return super().resolve(equal_weight_edges, message)
        
        return super().resolve(edges, message)
