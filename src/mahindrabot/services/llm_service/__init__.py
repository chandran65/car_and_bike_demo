"""
LLM Service - Comprehensive toolkit for LLM interactions.

This package provides a complete suite of tools for working with Large Language Models,
including message types, tool/function calling, structured output, streaming, and
agent-based workflows.

Main Components:
    - Configuration: LLMConfig, ModelArgs
    - Messages: SystemMessage, UserMessage, AIMessage
    - Tools: Tool, ToolKit, @tool decorator
    - Core Functions: get_llm_response, get_llm_structured_response, streaming variants
    - Agent System: StreamingChatWithTools for multi-turn tool-using conversations

Example:
    >>> from mahindrabot.services.llm_service import (
    ...     LLMConfig,
    ...     SystemMessage,
    ...     UserMessage,
    ...     get_llm_response
    ... )
    >>> 
    >>> config = LLMConfig(model_id="gpt-4")
    >>> messages = [
    ...     SystemMessage(content="You are a helpful assistant"),
    ...     UserMessage(content="What is 2+2?")
    ... ]
    >>> response = get_llm_response(config, messages)
    >>> print(response.content)
"""

# Configuration
from .config import LLMConfig, ModelArgs

# Messages and tool data types
from .messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    MessageType,
    Reasoning,
    SystemMessage,
    ToolCallRequest,
    ToolOutput,
    ToolOutputStatus,
    ToolResult,
    UserMessage,
)

# Tool system
from .tools import Tool, ToolKit, tool

# Core LLM functions
from .core import (
    get_llm_response,
    get_llm_stream_response,
    get_llm_structured_response,
    get_llm_structured_stream_response,
)

# Agent system
from .agent import (
    AgentRequest,
    AgentResponse,
    AgentStep,
    StepStatus,
    StreamingChatWithTools,
)

__all__ = [
    # Configuration
    "LLMConfig",
    "ModelArgs",
    # Messages
    "BaseMessage",
    "SystemMessage",
    "UserMessage",
    "AIMessage",
    "AIMessageChunk",
    "MessageType",
    # Tool data types
    "ToolCallRequest",
    "ToolResult",
    "ToolOutput",
    "ToolOutputStatus",
    "Reasoning",
    # Tool system
    "Tool",
    "ToolKit",
    "tool",
    # Core functions
    "get_llm_response",
    "get_llm_structured_response",
    "get_llm_stream_response",
    "get_llm_structured_stream_response",
    # Agent system
    "AgentRequest",
    "AgentResponse",
    "AgentStep",
    "StepStatus",
    "StreamingChatWithTools",
]
