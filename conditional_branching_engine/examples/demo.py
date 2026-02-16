"""
Demo examples for the Conditional Branching Engine.

This file demonstrates various usage patterns including:
- Basic keyword and regex matching
- Lambda functions for complex logic
- LLM-based conditions (with mock)
- Hybrid conditions
- Deterministic and probabilistic resolution
"""

import asyncio
from conditional_branching_engine import (
    Message,
    MessageMetadata,
    WorkflowBuilder,
    ResolutionMode,
    KeywordCondition,
    RegexCondition,
    LambdaCondition,
    LLMCondition,
    HybridCondition,
    ThresholdCondition,
    CompoundCondition,
    DeterministicResolver,
    ProbabilisticResolver,
)
from conditional_branching_engine.conditions.llm import MockLLM


# =============================================================================
# Node Processors
# =============================================================================

def process_entry(message: Message) -> Message:
    """Entry point processor."""
    print(f"[Entry] Processing: {message.content[:50]}...")
    return message


def process_category_a(message: Message) -> Message:
    """Process messages matching Category A."""
    print(f"[Category A] Handling specialized content")
    message.content += " [Processed by Category A Handler]"
    return message


def process_category_b(message: Message) -> Message:
    """Process messages matching Category B."""
    print(f"[Category B] Handling high-score content")
    message.content += " [Processed by Category B Handler]"
    return message


def process_default(message: Message) -> Message:
    """Default processor."""
    print(f"[Default] Using standard handling")
    message.content += " [Processed by Default Handler]"
    return message


def process_urgent(message: Message) -> Message:
    """Process urgent messages."""
    print(f"[URGENT] Priority handling!")
    message.content += " [URGENT HANDLER]"
    return message


def process_normal(message: Message) -> Message:
    """Process normal priority messages."""
    print(f"[Normal] Standard handling")
    message.content += " [NORMAL HANDLER]"
    return message


# =============================================================================
# Example 1: Basic Conditional Edges with Lambdas
# =============================================================================

def demo_basic_conditional_edges():
    """Demonstrate basic conditional edges using lambda functions."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Conditional Edges with Lambdas")
    print("=" * 60)
    
    # Create workflow builder
    builder = WorkflowBuilder()
    
    # Add nodes
    builder.add_node("entry", process_entry, "Entry point")
    builder.add_node("category_a", process_category_a, "Category A handler", is_terminal=True)
    builder.add_node("category_b", process_category_b, "Category B handler", is_terminal=True)
    builder.add_node("default", process_default, "Default handler", is_terminal=True)
    
    # Add conditional edges (exactly as shown in the spec!)
    builder.add_conditional_edges(
        "entry",
        {
            "category_a": lambda msg: "CATEGORY_A" in msg.content,
            "category_b": lambda msg: msg.metadata.score > 0.7,
        }
    )
    
    # Set start node
    builder.set_start("entry")
    
    # Visualize
    print(builder.visualize())
    
    # Build and test
    graph = builder.build()
    
    # Test case 1: Contains CATEGORY_A
    msg1 = Message(content="This is a CATEGORY_A message")
    result1 = asyncio.run(graph.execute(msg1))
    print(f"\nTest 1 Result: {result1.content}")
    
    # Test case 2: High score
    msg2 = Message(content="High priority message", metadata=MessageMetadata(score=0.85))
    result2 = asyncio.run(graph.execute(msg2))
    print(f"Test 2 Result: {result2.content}")
    
    # Test case 3: Neither matches
    msg3 = Message(content="Regular message", metadata=MessageMetadata(score=0.3))
    result3 = asyncio.run(graph.execute(msg3))
    print(f"Test 3 Result: {result3.content}")


# =============================================================================
# Example 2: Keyword and Regex Conditions
# =============================================================================

def demo_keyword_regex_conditions():
    """Demonstrate keyword and regex conditions."""
    print("\n" + "=" * 60)
    print("Example 2: Keyword and Regex Conditions")
    print("=" * 60)
    
    # Create keyword condition
    keyword_cond = KeywordCondition(keywords=["urgent", "asap"], match_any=True)
    
    # Create regex condition
    email_cond = RegexCondition(pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    # Test messages
    messages = [
        Message(content="This is an URGENT matter please help!"),
        Message(content="Please respond ASAP to my request."),
        Message(content="Contact me at john@example.com for details."),
        Message(content="Just a normal message."),
    ]
    
    print("\nKeyword Condition (urgent/asap):")
    for msg in messages:
        result = keyword_cond.evaluate(msg)
        print(f"  '{msg.content[:40]}...' -> matched={result.matched}")
    
    print("\nRegex Condition (email):")
    for msg in messages:
        result = email_cond.evaluate(msg)
        print(f"  '{msg.content[:40]}...' -> matched={result.matched}")


# =============================================================================
# Example 3: Lambda Conditions for Complex Logic
# =============================================================================

def demo_lambda_conditions():
    """Demonstrate lambda conditions for arbitrary Python logic."""
    print("\n" + "=" * 60)
    print("Example 3: Lambda Conditions for Complex Logic")
    print("=" * 60)
    
    # Complex condition: high priority AND contains specific keywords
    complex_condition = LambdaCondition(
        func=lambda msg: (
            msg.metadata.priority <= 2 and
            ("help" in msg.content.lower() or "issue" in msg.content.lower())
        ),
        name="complex_priority_route"
    )
    
    # Threshold condition for score-based routing
    threshold_condition = ThresholdCondition(
        field="metadata.score",
        threshold=0.7,
        comparison=">="
    )
    
    messages = [
        Message(
            content="I need help with my account",
            metadata=MessageMetadata(priority=1, score=0.5)
        ),
        Message(
            content="Critical issue detected",
            metadata=MessageMetadata(priority=1, score=0.9)
        ),
        Message(
            content="Just a question",
            metadata=MessageMetadata(priority=5, score=0.3)
        ),
    ]
    
    print("\nComplex Priority Condition:")
    for msg in messages:
        result = complex_condition.evaluate(msg)
        print(f"  '{msg.content}' (priority={msg.metadata.priority}) -> matched={result.matched}")
    
    print("\nThreshold Condition (score >= 0.7):")
    for msg in messages:
        result = threshold_condition.evaluate(msg)
        print(f"  '{msg.content}' (score={msg.metadata.score}) -> matched={result.matched}")


# =============================================================================
# Example 4: LLM-Based Conditions
# =============================================================================

def demo_llm_conditions():
    """Demonstrate LLM-based conditions with mock."""
    print("\n" + "=" * 60)
    print("Example 4: LLM-Based Conditions")
    print("=" * 60)
    
    # Create mock LLM that returns specific responses
    mock_llm = MockLLM({
        "frustration": "yes",
        "urgent": "yes",
    })
    
    # Create LLM condition
    frustration_cond = LLMCondition(
        llm=mock_llm,
        prompt="Is the customer expressing frustration? Answer yes or no. Message: {content}",
        expected_labels=["yes", "no"],
        name="frustration_detector"
    )
    
    messages = [
        Message(content="I'm so frustrated with this service!"),
        Message(content="I'd like to know more about your products."),
        Message(content="This is absolutely terrible, I've been waiting for hours!"),
    ]
    
    print("\nLLM Frustration Detection:")
    for msg in messages:
        result = frustration_cond.evaluate(msg)
        print(f"  '{msg.content}' -> matched={result.matched}, reason={result.reason}")


# =============================================================================
# Example 5: Hybrid Conditions
# =============================================================================

def demo_hybrid_conditions():
    """Demonstrate hybrid conditions (fast filter + slow analysis)."""
    print("\n" + "=" * 60)
    print("Example 5: Hybrid Conditions")
    print("=" * 60)
    
    # Mock LLM for the slow part
    mock_llm = MockLLM({"complaint": "yes"})
    
    # Create hybrid condition
    hybrid_cond = HybridCondition(
        fast_conditions=[
            KeywordCondition(keywords=["refund", "cancel", "complaint"], match_any=True),
        ],
        slow_condition=LLMCondition(
            llm=mock_llm,
            prompt="Is this a formal complaint? Answer yes or no.",
            expected_labels=["yes"]
        ),
        name="hybrid_complaint_detector"
    )
    
    messages = [
        Message(content="I want a refund for my purchase"),
        Message(content="Please cancel my subscription"),
        Message(content="Just wondering about pricing"),
    ]
    
    print("\nHybrid Complaint Detection:")
    for msg in messages:
        result = hybrid_cond.evaluate(msg)
        print(f"  '{msg.content}' -> matched={result.matched}, reason={result.reason[:50]}...")


# =============================================================================
# Example 6: Compound Conditions
# =============================================================================

def demo_compound_conditions():
    """Demonstrate compound conditions (AND/OR logic)."""
    print("\n" + "=" * 60)
    print("Example 6: Compound Conditions")
    print("=" * 60)
    
    # AND condition: both must match
    and_condition = CompoundCondition(
        conditions=[
            KeywordCondition(keywords=["urgent"], match_any=True),
            ThresholdCondition(field="metadata.score", threshold=0.5, comparison=">="),
        ],
        operator="AND",
        name="urgent_and_high_score"
    )
    
    # OR condition: either can match
    or_condition = CompoundCondition(
        conditions=[
            KeywordCondition(keywords=["urgent", "asap"], match_any=True),
            ThresholdCondition(field="metadata.priority", threshold=2, comparison="<="),
        ],
        operator="OR",
        name="urgent_or_high_priority"
    )
    
    messages = [
        Message(content="URGENT: System down!", metadata=MessageMetadata(score=0.8, priority=1)),
        Message(content="Normal message", metadata=MessageMetadata(score=0.9, priority=3)),
        Message(content="ASAP request", metadata=MessageMetadata(score=0.3, priority=2)),
    ]
    
    print("\nAND Condition (urgent AND score >= 0.5):")
    for msg in messages:
        result = and_condition.evaluate(msg)
        print(f"  '{msg.content}' -> matched={result.matched}")
    
    print("\nOR Condition (urgent/asap OR priority <= 2):")
    for msg in messages:
        result = or_condition.evaluate(msg)
        print(f"  '{msg.content}' -> matched={result.matched}")


# =============================================================================
# Example 7: Probabilistic Resolution
# =============================================================================

def demo_probabilistic_resolution():
    """Demonstrate probabilistic (weighted) resolution."""
    print("\n" + "=" * 60)
    print("Example 7: Probabilistic Resolution")
    print("=" * 60)
    
    from conditional_branching_engine.core.workflow import ConditionalEdge
    
    # Create edges with different weights
    edges = [
        ConditionalEdge(
            destination="handler_a",
            condition=lambda msg: "A" in msg.content,
            weight=1.0,
            priority=1
        ),
        ConditionalEdge(
            destination="handler_b", 
            condition=lambda msg: "B" in msg.content,
            weight=3.0,
            priority=2
        ),
    ]
    
    resolver = ProbabilisticResolver(seed=42)  # Fixed seed for reproducibility
    
    # Test message that matches both
    msg = Message(content="A and B are both here")
    
    print(f"\nTesting with message: '{msg.content}'")
    print("Running 10 iterations (weights: A=1, B=3):")
    
    results = {"handler_a": 0, "handler_b": 0}
    for i in range(10):
        # Reset seed for each iteration to see distribution
        import random
        random.seed(i)
        
        destination = resolver.resolve(edges, msg)
        results[destination] = results.get(destination, 0) + 1
        print(f"  Iteration {i+1}: {destination}")
    
    print(f"\nResults: {results}")
    print("(handler_b should appear ~3x more often due to weight)")


# =============================================================================
# Example 8: Full Workflow with Priorities
# =============================================================================

def demo_full_workflow():
    """Demonstrate a complete workflow with priority-based routing."""
    print("\n" + "=" * 60)
    print("Example 8: Full Workflow with Priorities")
    print("=" * 60)
    
    # Create builder with deterministic resolution
    builder = WorkflowBuilder(resolution_mode=ResolutionMode.DETERMINISTIC)
    
    # Add nodes with processors
    builder.add_node("entry", process_entry, "Entry point")
    builder.add_node("urgent", process_urgent, "Urgent handler", is_terminal=True)
    builder.add_node("normal", process_normal, "Normal handler", is_terminal=True)
    builder.add_node("default", process_default, "Default handler", is_terminal=True)
    
    # Add conditional edges with priorities
    builder.add_conditional_edges(
        "entry",
        {
            "urgent": lambda msg: msg.metadata.priority <= 1,
            "normal": lambda msg: msg.metadata.priority <= 3,
        },
        priorities={"urgent": 1, "normal": 10}  # urgent has higher priority
    )
    
    # Add fallback edge
    builder.add_edge("entry", "default")
    
    builder.set_start("entry")
    
    print(builder.visualize())
    
    graph = builder.build()
    
    # Test cases
    test_messages = [
        Message(content="Critical emergency!", metadata=MessageMetadata(priority=1)),
        Message(content="Important request", metadata=MessageMetadata(priority=2)),
        Message(content="Regular inquiry", metadata=MessageMetadata(priority=4)),
        Message(content="Some message", metadata=MessageMetadata(priority=5)),
    ]
    
    print("\nExecution Results:")
    for msg in test_messages:
        result = asyncio.run(graph.execute(msg))
        print(f"  priority={msg.metadata.priority} -> {result.content}")


# =============================================================================
# Run All Demos
# =============================================================================

if __name__ == "__main__":
    demo_basic_conditional_edges()
    demo_keyword_regex_conditions()
    demo_lambda_conditions()
    demo_llm_conditions()
    demo_hybrid_conditions()
    demo_compound_conditions()
    demo_probabilistic_resolution()
    demo_full_workflow()
    
    print("\n" + "=" * 60)
    print("All demos completed!")
    print("=" * 60)
