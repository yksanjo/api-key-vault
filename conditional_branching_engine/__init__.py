"""
Conditional Branching Engine
Runtime-Adaptive Execution Paths

A rules-based approach for handling input variability and contextual emergence
in workflow pipelines, inspired by LangChain's StateGraph.
"""

from .core.message import Message, MessageMetadata
from .core.workflow import WorkflowBuilder, ConditionalEdge, ResolutionMode
from .conditions.base import Condition, ConditionResult, CompoundCondition
from .conditions.keyword import KeywordCondition, RegexCondition
from .conditions.lambda_condition import LambdaCondition
from .conditions.llm import LLMCondition
from .conditions.hybrid import HybridCondition, ThresholdCondition
from .resolution.deterministic import DeterministicResolver
from .resolution.probabilistic import ProbabilisticResolver

__all__ = [
    "Message",
    "MessageMetadata",
    "WorkflowBuilder",
    "ConditionalEdge",
    "Condition",
    "ConditionResult",
    "KeywordCondition",
    "RegexCondition",
    "LambdaCondition",
    "LLMCondition",
    "HybridCondition",
    "ThresholdCondition",
    "CompoundCondition",
    "DeterministicResolver",
    "ProbabilisticResolver",
]
