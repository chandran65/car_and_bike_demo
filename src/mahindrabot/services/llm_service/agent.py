"""Agent system for multi-step LLM interactions with tool calling."""

import inspect
import traceback
from collections.abc import Callable, Generator
from enum import StrEnum
from typing import Literal, cast

from langfuse import observe
from pydantic import BaseModel

from .config import LLMConfig
from .core import get_llm_stream_response
from .messages import (
    AIMessage,
    MessageType,
    ToolOutput,
    ToolOutputStatus,
    ToolResult,
    UserMessage,
)
from .tools import Tool, ToolCallable


class AgentRequest(BaseModel):
    """
    Request to an agent with user input.
    
    Attributes:
        type: Type identifier for the request
        user_input: The user's input text
    """
    
    type: Literal["agent_request"] = "agent_request"
    user_input: str


class StepStatus(StrEnum):
    """Status of an agent execution step."""
    
    PENDING = "pending"
    DONE = "done"


class AgentStep(BaseModel):
    """
    A single step in an agent's execution.
    
    Represents one turn of the agent making tool calls and receiving results.
    
    Attributes:
        ai_message: The AI's message including any tool call requests
        tool_results: Results from executing the requested tools
        status: Current status of this step (PENDING or DONE)
    """
    
    ai_message: AIMessage
    tool_results: list[ToolResult]
    status: StepStatus = StepStatus.PENDING


class AgentResponse(BaseModel):
    """
    Complete response from an agent interaction.
    
    Contains all intermediate steps (tool calls) and the final message.
    
    Attributes:
        type: Type identifier for the response
        steps: List of agent steps (tool call rounds)
        final_message: The final AI message when no more tools are needed
    """
    
    type: Literal["agent_response"] = "agent_response"
    steps: list[AgentStep] = []
    final_message: AIMessage | None = None


def ai_message_to_agent_response(ai_message: AIMessage) -> AgentResponse:
    """
    Convert an AIMessage to an AgentResponse.
    
    If the message has tool calls, creates a response with a pending step.
    Otherwise, sets it as the final message.
    
    Args:
        ai_message: The AI message to convert
        
    Returns:
        AgentResponse with either steps or a final message
    """
    if not ai_message.tool_call_requests:
        return AgentResponse(final_message=ai_message)
    tool_results = []
    tool_results = [
        ToolResult(
            id=tool_call_request.id,
            name=tool_call_request.name,
            raw_input=tool_call_request.raw_input,
            input=tool_call_request.input,
        )
        for tool_call_request in ai_message.tool_call_requests
    ]
    return AgentResponse(steps=[AgentStep(ai_message=ai_message, tool_results=tool_results)])


def update_agent_response_with_ai_message(
    agent_response: AgentResponse, ai_message: AIMessage
) -> AgentResponse:
    """
    Update an existing AgentResponse with a new or updated AIMessage.
    
    If the message has no tool calls, it becomes the final message.
    If it has tool calls, updates an existing step or adds a new one.
    
    Args:
        agent_response: The response to update
        ai_message: The new AI message
        
    Returns:
        The updated AgentResponse
    """
    if not ai_message.tool_call_requests:
        agent_response.final_message = ai_message
        return agent_response

    agent_response.final_message = None

    tool_results = [
        ToolResult(
            id=tool_call_request.id,
            name=tool_call_request.name,
            raw_input=tool_call_request.raw_input,
            input=tool_call_request.input,
        )
        for tool_call_request in ai_message.tool_call_requests
    ]

    for step in agent_response.steps:
        if step.ai_message.id == ai_message.id:
            # Existing step found, updating it
            step.ai_message = ai_message
            step.tool_results = tool_results
            return agent_response

    # No existing step found, adding a new one
    agent_response.steps.append(AgentStep(ai_message=ai_message, tool_results=tool_results))

    return agent_response


def _execute_tool(
    tool_func: ToolCallable | None, tool_name: str, tool_input: dict
) -> Generator[ToolOutput, None, None]:
    """
    Execute a tool function and yield its output(s).
    
    Handles both regular functions and generator functions. Converts
    return values to ToolOutput objects and catches exceptions.
    
    Args:
        tool_func: The tool function to execute (or None if not found)
        tool_name: Name of the tool (for error messages)
        tool_input: Dictionary of arguments to pass to the tool
        
    Yields:
        ToolOutput objects with the tool's results or error messages
    """
    if not tool_func:
        yield ToolOutput(
            text=f"Error: Tool '{tool_name}' not found.", status=ToolOutputStatus.FAILURE
        )
        return

    try:
        if inspect.isgeneratorfunction(tool_func):
            for output in tool_func(**tool_input):
                if isinstance(output, ToolOutput):
                    yield output
                elif isinstance(output, str):
                    yield ToolOutput(text=output, status=ToolOutputStatus.SUCCESS)
                else:
                    yield ToolOutput(text=str(output), status=ToolOutputStatus.SUCCESS)
        else:
            result = tool_func(**tool_input)
            if isinstance(result, ToolOutput):
                yield result
            else:
                yield ToolOutput(text=str(result), status=ToolOutputStatus.SUCCESS)
    except Exception as e:
        traceback.print_exc()
        yield ToolOutput(text=f"Error: {e}", status=ToolOutputStatus.FAILURE)


def execute_tool_calls(
    agent_response: AgentResponse, name_to_tool: dict[str, ToolCallable]
) -> Generator[AgentResponse, None, tuple[AgentResponse, list[UserMessage]]]:
    """
    Execute all pending tool calls in an agent response.
    
    Iterates through agent steps, executes requested tools, and updates
    the results. Yields the response after each tool output for streaming.
    
    Args:
        agent_response: The response containing tool call requests
        name_to_tool: Mapping of tool names to their callable functions
        
    Yields:
        Updated AgentResponse after each tool execution
        
    Returns:
        Tuple of (final AgentResponse, list of UserMessages with tool results)
    """
    user_messages = []
    for step in agent_response.steps:
        if step.status == StepStatus.DONE:
            continue
        for tool_result in step.tool_results:
            tool_func = name_to_tool.get(tool_result.name)
            for output in _execute_tool(tool_func, tool_result.name, tool_result.input or {}):
                tool_result.output = output.text
                tool_result.status = output.status
                tool_result.metadata = output.metadata
                yield agent_response
        user_messages.append(UserMessage(content="", tool_results=step.tool_results))
        step.status = StepStatus.DONE
    return agent_response, user_messages


class StreamingChatWithTools:
    """
    Agent for multi-turn conversations with streaming and tool calling.
    
    This agent maintains conversation history, can call tools/functions,
    and streams responses in real-time. It automatically manages the
    agent loop: LLM response -> tool execution -> LLM response.
    
    Attributes:
        llm_config: Configuration for the LLM
        tools: List of available tools the agent can use
        raw_messages: Internal message history
        agent_messages: High-level agent request/response history
        
    Example:
        >>> from llm_service import LLMConfig, StreamingChatWithTools, AgentRequest, tool
        >>> 
        >>> @tool
        ... def get_weather(location: str) -> str:
        ...     return f"Weather in {location}: Sunny, 72°F"
        >>> 
        >>> config = LLMConfig(model_id="gpt-4")
        >>> agent = StreamingChatWithTools(config, tools=[get_weather])
        >>> 
        >>> request = AgentRequest(user_input="What's the weather in Paris?")
        >>> for response in agent.ask(request):
        ...     if response.final_message:
        ...         print(response.final_message.content)
        'The weather in Paris is sunny and 72°F.'
    """
    
    def __init__(
        self,
        llm_config: LLMConfig,
        tools: list[Tool | Callable] | None = None,
        messages: list[MessageType] | None = None,
    ):
        """
        Initialize the streaming chat agent.
        
        Args:
            llm_config: Configuration for the LLM
            tools: Optional list of tools/functions the agent can use
            messages: Optional initial message history
        """
        self.llm_config = llm_config
        self.tools = (
            [
                Tool.from_function(tool)
                if isinstance(tool, Callable) and not isinstance(tool, Tool)
                else tool
                for tool in tools
            ]
            if tools
            else []
        )
        self.raw_messages = messages or []
        self.agent_messages: list[AgentRequest | AgentResponse] = []

    @observe(name="ask")
    def ask(self, message: AgentRequest) -> Generator[AgentResponse, None, AgentResponse]:
        """
        Send a message to the agent and get a streaming response.
        
        The agent will:
        1. Send the message to the LLM
        2. If tools are requested, execute them
        3. Send tool results back to the LLM
        4. Repeat until the LLM provides a final answer
        
        Args:
            message: The user's request
            
        Yields:
            AgentResponse objects with incremental updates during streaming
            and tool execution
            
        Returns:
            The final AgentResponse with the complete answer
            
        Example:
            >>> request = AgentRequest(user_input="Calculate 15 * 23")
            >>> for response in agent.ask(request):
            ...     # Display streaming updates
            ...     for step in response.steps:
            ...         print(f"Tool: {step.ai_message.tool_call_requests}")
            ...     if response.final_message:
            ...         print(f"Final: {response.final_message.content}")
        """
        self.agent_messages.append(message)
        self.raw_messages.append(UserMessage(content=message.user_input))
        agent_response = AgentResponse()
        while True:
            for ai_message in get_llm_stream_response(
                self.llm_config, self.raw_messages, cast("list[Tool | Callable]", self.tools)
            ):
                yield update_agent_response_with_ai_message(agent_response, ai_message)
            self.raw_messages.append(ai_message)

            if agent_response.final_message:
                yield agent_response
                self.agent_messages.append(agent_response)
                return agent_response

            agent_response, user_messages = yield from execute_tool_calls(
                agent_response, name_to_tool={tool.name: tool.func for tool in self.tools}
            )
            self.raw_messages.extend(user_messages)
