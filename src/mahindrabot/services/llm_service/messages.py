"""Message types and tool-related data models for LLM interactions."""

import uuid
from enum import IntEnum
from typing import Any, Optional, Union

from pydantic import BaseModel, Field


class ToolOutputStatus(IntEnum):
    """Status codes for tool execution results."""
    
    FAILURE = 0
    SUCCESS = 1


class ToolCallRequest(BaseModel):
    """
    Request to call a tool with specific arguments.
    
    Attributes:
        id: Unique identifier for the tool call
        name: Name of the tool to call
        input: Parsed input arguments as a dictionary
        raw_input: Raw input string before parsing
    """
    
    id: str
    name: str
    input: dict = {}
    raw_input: str = ""


class Reasoning(BaseModel):
    """
    Reasoning information from LLM response.
    
    Attributes:
        id: Unique identifier for the reasoning block
        summaries: List of summary texts
        contents: List of reasoning content texts
        signature: Signature or identifier for the reasoning
        redacted_content: Optional redacted content
    """
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    summaries: list[str] = []
    contents: list[str] = []
    signature: str = ""
    redacted_content: Optional[str] = None


class ToolOutput(BaseModel):
    """
    Output from a tool execution.
    
    Attributes:
        text: The text output from the tool
        metadata: Additional metadata about the execution
        status: Status of the tool execution (SUCCESS or FAILURE)
    """
    
    text: str
    metadata: dict[str, Any] = {}
    status: ToolOutputStatus = ToolOutputStatus.SUCCESS


class ToolResult(BaseModel):
    """
    Complete result of a tool execution including input and output.
    
    Attributes:
        id: Optional unique identifier for the result
        name: Name of the tool that was executed
        raw_input: Raw input string before parsing
        input: Parsed input arguments
        output: Output text from the tool
        metadata: Additional metadata
        status: Execution status (SUCCESS or FAILURE)
    """
    
    id: Optional[str] = None
    name: str
    raw_input: str = ""
    input: Optional[dict] = None
    output: Optional[str] = None
    metadata: dict[str, Any] = {}
    status: ToolOutputStatus = ToolOutputStatus.SUCCESS


class BaseMessage(BaseModel):
    """
    Base class for all message types.
    
    Attributes:
        id: Unique identifier for the message
        content: Text content of the message
        role: Role of the message sender (e.g., 'user', 'assistant', 'system')
    """
    
    id: str = Field(
        description="The id of the message.",
        default_factory=lambda: str(uuid.uuid4())
    )
    content: str = Field(description="The content of the message.")
    role: str = Field(description="The role of the message sender (e.g., 'user', 'assistant').")


class SystemMessage(BaseMessage):
    """
    System message containing instructions for the LLM.
    
    System messages are used to provide context, instructions, and guidelines
    to the language model.
    """
    
    role: str = "system"


class UserMessage(BaseMessage):
    """
    User message containing user input and optional tool results.
    
    Attributes:
        tool_results: List of tool execution results to include in this message
    """
    
    role: str = "user"
    tool_results: list[ToolResult] = []


class AIMessage(BaseMessage):
    """
    AI assistant message with optional tool calls and reasoning.
    
    Attributes:
        tool_call_requests: List of tool calls requested by the AI
        reasoning: Optional reasoning information from the model
    """
    
    role: str = "ai"
    tool_call_requests: list[ToolCallRequest] = []
    reasoning: Optional[Reasoning] = None


class AIMessageChunk(AIMessage):
    """
    A chunk of an AI message during streaming.
    
    This is used for incremental message building during streaming responses.
    """
    
    pass


# Type alias for any message type
MessageType = Union[SystemMessage, UserMessage, AIMessage]
