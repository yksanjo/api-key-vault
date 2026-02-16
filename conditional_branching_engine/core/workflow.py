"""
Workflow builder and conditional edge classes for the Conditional Branching Engine.

This module provides the core building blocks for creating workflow graphs
with conditional routing based on message content and metadata.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum

from .message import Message


class ResolutionMode(Enum):
    """Resolution mode for conditional edge evaluation."""
    DETERMINISTIC = "deterministic"  # First match wins
    PROBABILISTIC = "probabilistic"   # Weighted selection


@dataclass
class ConditionalEdge:
    """
    Represents a conditional edge in the workflow graph.
    
    An edge consists of a destination node name and a condition that
    determines whether the flow should follow this edge.
    
    Attributes:
        destination: The name of the node to route to if condition is true.
        condition: A callable that takes a Message and returns a bool.
        weight: Weight for probabilistic resolution (higher = more likely).
        priority: Priority for deterministic resolution (lower = evaluated first).
        description: Human-readable description of this routing rule.
    """
    destination: str
    condition: Callable[[Message], bool]
    weight: float = 1.0
    priority: int = 100
    description: str = ""
    
    def evaluate(self, message: Message) -> bool:
        """Evaluate if this edge should be taken."""
        try:
            return self.condition(message)
        except Exception as e:
            # Log error but don't crash - return False for safety
            print(f"Condition evaluation error for {self.destination}: {e}")
            return False
    
    def __repr__(self) -> str:
        return f"ConditionalEdge(destination='{self.destination}', priority={self.priority})"


@dataclass
class GraphNode:
    """
    Represents a node in the workflow graph.
    
    Attributes:
        name: Unique identifier for the node.
        processor: The function/callable that processes messages at this node.
        description: Human-readable description of what this node does.
        is_terminal: Whether this node is an endpoint (no outgoing edges).
    """
    name: str
    processor: Callable[[Message], Message]
    description: str = ""
    is_terminal: bool = False


class WorkflowBuilder:
    """
    Builder for creating workflow graphs with conditional edges.
    
    Inspired by LangChain's StateGraph, this builder allows defining
    nodes and conditional edges that route messages based on content
    and metadata.
    
    Example:
        builder = WorkflowBuilder()
        builder.add_node("analyzer", analyze_message)
        builder.add_conditional_edges(
            "analyzer",
            {
                "route_a": lambda msg: "CATEGORY_A" in msg.content,
                "route_b": lambda msg: msg.metadata.score > 0.7,
            }
        )
    """
    
    def __init__(self, resolution_mode: ResolutionMode = ResolutionMode.DETERMINISTIC):
        """
        Initialize the workflow builder.
        
        Args:
            resolution_mode: How to resolve multiple matching conditions.
        """
        self._nodes: dict[str, GraphNode] = {}
        self._edges: dict[str, list[ConditionalEdge]] = {}
        self._start_node: Optional[str] = None
        self._end_nodes: set[str] = set()
        self._resolution_mode = resolution_mode
    
    def add_node(
        self,
        name: str,
        processor: Callable[[Message], Message],
        description: str = "",
        is_terminal: bool = False
    ) -> "WorkflowBuilder":
        """
        Add a node to the workflow.
        
        Args:
            name: Unique identifier for the node.
            processor: Function that processes messages at this node.
            description: Human-readable description.
            is_terminal: Whether this is an endpoint node.
            
        Returns:
            Self for method chaining.
        """
        self._nodes[name] = GraphNode(
            name=name,
            processor=processor,
            description=description,
            is_terminal=is_terminal
        )
        if is_terminal:
            self._end_nodes.add(name)
        return self
    
    def add_edge(self, source: str, destination: str) -> "WorkflowBuilder":
        """
        Add a direct (unconditional) edge between nodes.
        
        Args:
            source: Source node name.
            destination: Destination node name.
            
        Returns:
            Self for method chaining.
        """
        if source not in self._nodes:
            raise ValueError(f"Source node '{source}' does not exist")
        if destination not in self._nodes:
            raise ValueError(f"Destination node '{destination}' does not exist")
        
        # Add a default conditional edge that always evaluates to True
        edge = ConditionalEdge(
            destination=destination,
            condition=lambda msg: True,
            priority=999,
            description="Default unconditional edge"
        )
        
        if source not in self._edges:
            self._edges[source] = []
        self._edges[source].append(edge)
        return self
    
    def add_conditional_edges(
        self,
        source: str,
        conditions: dict[str, Callable[[Message], bool]],
        weights: Optional[dict[str, float]] = None,
        priorities: Optional[dict[str, int]] = None
    ) -> "WorkflowBuilder":
        """
        Add conditional edges from a source node.
        
        This method creates conditional edges based on the provided conditions.
        Each condition is a mapping from destination name to a callable that
        returns True if the message should be routed to that destination.
        
        Args:
            source: Source node name.
            conditions: Dict mapping destination names to condition callables.
            weights: Optional weights for probabilistic resolution.
            priorities: Optional priorities for deterministic resolution.
            
        Returns:
            Self for method chaining.
            
        Example:
            builder.add_conditional_edges(
                "analyzer",
                {
                    "route_a": lambda msg: "CATEGORY_A" in msg.content,
                    "route_b": lambda msg: msg.metadata.score > 0.7,
                }
            )
        """
        if source not in self._nodes:
            raise ValueError(f"Source node '{source}' does not exist")
        
        if source not in self._edges:
            self._edges[source] = []
        
        for destination, condition in conditions.items():
            if destination not in self._nodes:
                raise ValueError(f"Destination node '{destination}' does not exist")
            
            weight = weights.get(destination, 1.0) if weights else 1.0
            priority = priorities.get(destination, 100) if priorities else 100
            
            edge = ConditionalEdge(
                destination=destination,
                condition=condition,
                weight=weight,
                priority=priority,
                description=f"Conditional edge to {destination}"
            )
            self._edges[source].append(edge)
        
        return self
    
    def set_start(self, node_name: str) -> "WorkflowBuilder":
        """
        Set the starting node for the workflow.
        
        Args:
            node_name: Name of the starting node.
            
        Returns:
            Self for method chaining.
        """
        if node_name not in self._nodes:
            raise ValueError(f"Start node '{node_name}' does not exist")
        self._start_node = node_name
        return self
    
    def get_edges(self, node_name: str) -> list[ConditionalEdge]:
        """Get all outgoing edges from a node."""
        return self._edges.get(node_name, [])
    
    def get_node(self, node_name: str) -> Optional[GraphNode]:
        """Get a node by name."""
        return self._nodes.get(node_name)
    
    def build(self) -> "WorkflowGraph":
        """
        Build the workflow graph.
        
        Returns:
            A WorkflowGraph instance ready for execution.
        """
        if self._start_node is None:
            raise ValueError("Start node not set. Call set_start() first.")
        
        return WorkflowGraph(
            nodes=self._nodes,
            edges=self._edges,
            start_node=self._start_node,
            end_nodes=self._end_nodes,
            resolution_mode=self._resolution_mode
        )
    
    def visualize(self) -> str:
        """Generate a text representation of the workflow."""
        lines = ["Workflow Graph:", "=" * 50]
        
        lines.append(f"\nStart Node: {self._start_node}")
        lines.append(f"Resolution Mode: {self._resolution_mode.value}")
        
        lines.append("\nNodes:")
        for name, node in self._nodes.items():
            terminal = " (TERMINAL)" if node.is_terminal else ""
            lines.append(f"  - {name}{terminal}: {node.description or 'No description'}")
        
        lines.append("\nEdges:")
        for source, edges in self._edges.items():
            for edge in edges:
                lines.append(f"  {source} -> {edge.destination} (priority: {edge.priority})")
        
        return "\n".join(lines)


class WorkflowGraph:
    """
    The compiled workflow graph ready for execution.
    
    This class manages the execution flow, routing messages through
    nodes based on conditional edges.
    """
    
    def __init__(
        self,
        nodes: dict[str, GraphNode],
        edges: dict[str, list[ConditionalEdge]],
        start_node: str,
        end_nodes: set[str],
        resolution_mode: ResolutionMode
    ):
        self._nodes = nodes
        self._edges = edges
        self._start_node = start_node
        self._end_nodes = end_nodes
        self._resolution_mode = resolution_mode
    
    async def execute(self, message: Message) -> Message:
        """
        Execute the workflow starting from the start node.
        
        Args:
            message: The input message to process.
            
        Returns:
            The final processed message after flowing through the graph.
        """
        current_node_name = self._start_node
        
        while current_node_name is not None:
            # Process the current node
            node = self._nodes[current_node_name]
            message = node.processor(message)
            
            # Check if we've reached a terminal node
            if current_node_name in self._end_nodes:
                break
            
            # Determine next node via conditional edges
            current_node_name = self._resolve_next_node(current_node_name, message)
        
        return message
    
    def _resolve_next_node(self, current_node_name: str, message: Message) -> Optional[str]:
        """Resolve the next node based on conditional edges."""
        edges = self._edges.get(current_node_name, [])
        
        if not edges:
            return None
        
        # Filter edges that evaluate to True
        matching_edges = [edge for edge in edges if edge.evaluate(message)]
        
        if not matching_edges:
            return None
        
        if self._resolution_mode == ResolutionMode.DETERMINISTIC:
            # Return the highest priority (lowest number) match
            return min(matching_edges, key=lambda e: e.priority).destination
        else:
            # Probabilistic: weighted random selection
            import random
            total_weight = sum(e.weight for e in matching_edges)
            r = random.uniform(0, total_weight)
            cumulative = 0
            for edge in matching_edges:
                cumulative += edge.weight
                if r <= cumulative:
                    return edge.destination
            return matching_edges[-1].destination
    
    @property
    def start_node(self) -> str:
        return self._start_node
    
    @property
    def end_nodes(self) -> set[str]:
        return self._end_nodes
