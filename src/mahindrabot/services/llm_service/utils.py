"""Internal utility functions for LLM service interactions."""

import re
from collections.abc import Callable
try:
    from typing import TypeAlias
except ImportError:
    from typing_extensions import TypeAlias

import jiter
from openai.types.responses import Response as OAIResponse
from openai.types.responses import ResponseStreamEvent

from .messages import (
    AIMessage,
    MessageType,
    Reasoning,
    SystemMessage,
    ToolCallRequest,
    UserMessage,
)
from .tools import Tool

# Pattern for detecting incomplete Unicode escape sequences
PARTIAL_UNICODE_PATTERN = re.compile(r"\\u[0-9a-fA-F]{0,3}$")

from typing import Any, Optional, Union

# Type alias for JSON values
JSONTYPE: TypeAlias = Union[dict, list, str, int, float, bool, None]


def parse_partial_json(json_str: str) -> JSONTYPE:
    """
    Parse potentially incomplete JSON strings from streaming responses.
    
    This function handles partial JSON that may be received during streaming,
    including incomplete strings and Unicode escape sequences.
    
    Args:
        json_str: The JSON string to parse (may be incomplete)
        
    Returns:
        Parsed JSON value (dict, list, str, int, float, bool, or None)
        
    Note:
        Based on: https://github.com/globalaiplatform/langdiff/blob/eb072a1829844e3d8ef5d733e31ed0011c0c4870/py/src/langdiff/parser/parser.py#L34
    """
    if not json_str.strip():
        return ""

    if (
        json_str.endswith('"') and not json_str.endswith('\\"') and not json_str.endswith(':"')
    ) or (json_str.endswith("\\") and not json_str.endswith("\\\\")):
        json_str = json_str[:-1]
    else:
        # Workaround for https://github.com/pydantic/jiter/issues/207
        m = PARTIAL_UNICODE_PATTERN.search(json_str)
        if m:
            json_str = json_str[: -len(m.group(0))]

    return jiter.from_json(
        json_str.encode("utf-8"), cache_mode="keys", partial_mode="trailing-strings"
    )


def _get_oai_messages(messages: list[MessageType]) -> list[dict]:
    """
    Convert internal message format to OpenAI API message format.
    
    This function transforms our internal message types (SystemMessage, UserMessage,
    AIMessage) into the format expected by OpenAI's API.
    
    Args:
        messages: List of internal message objects
        
    Returns:
        List of message dictionaries in OpenAI format
        
    Note:
        - System messages are excluded (handled separately as instructions)
        - User messages may include tool results
        - AI messages may include function calls
    """
    result = []
    for message in messages:
        if isinstance(message, SystemMessage):
            # System messages are sent as instructions to the model
            continue
        elif isinstance(message, UserMessage):
            if message.content:
                result.append({"role": "user", "content": message.content})
            result.extend(
                [
                    {
                        "type": "function_call_output",
                        "call_id": tool_result.id,
                        "output": tool_result.output,
                    }
                    for tool_result in message.tool_results
                ]
            )
        elif isinstance(message, AIMessage):
            if message.content:
                result.append({"role": "assistant", "content": message.content})
            result.extend(
                [
                    {
                        "type": "function_call",
                        "call_id": tool_call_request.id,
                        "name": tool_call_request.name,
                        "arguments": tool_call_request.raw_input,
                    }
                    for tool_call_request in message.tool_call_requests
                ]
            )
    return result

def _get_instruction_from_messages(messages: list[MessageType]) -> str:
    """
    Extract system instructions from messages.
    
    Combines all SystemMessage content into a single instruction string.
    
    Args:
        messages: List of messages to extract instructions from
        
    Returns:
        Combined instruction text from all system messages
    """
    return "\n".join(
        [message.content for message in messages if isinstance(message, SystemMessage)]
    )


def _get_aoi_tool(tool: Union[Tool, Callable]) -> dict:
    """
    Convert a Tool or callable to OpenAI tool format.
    
    Transforms our internal Tool representation into the format expected
    by OpenAI's function calling API.
    
    Args:
        tool: Tool instance or callable function
        
    Returns:
        Dictionary in OpenAI tool format with type, name, description, and parameters
    """
    if not isinstance(tool, Tool) and isinstance(tool, Callable):
        tool = Tool.from_function(tool)
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.args_schema.model_json_schema(),
    }


def _get_ai_message_from_oai_response(response: OAIResponse) -> AIMessage:
    """
    Convert OpenAI API response to internal AIMessage format.
    
    Parses the OpenAI response and extracts text content, tool calls,
    and reasoning information into our internal message format.
    
    Args:
        response: OpenAI API response object
        
    Returns:
        AIMessage with parsed content, tool calls, and reasoning
        
    Raises:
        ValueError: If an unknown content or output type is encountered
    """
    ai_message = AIMessage(id=response.id, content="")
    for output in response.output:
        if output.type == "message":
            for content in output.content:
                if content.type == "output_text":
                    ai_message.content += content.text
                else:
                    raise ValueError(
                        f"Unknown content type: {content.type} data: {content}"
                    )
        elif output.type == "function_call":
            parsed_input = parse_partial_json(output.arguments)
            if not isinstance(parsed_input, dict):
                parsed_input = {}
            ai_message.tool_call_requests.append(
                ToolCallRequest(
                    id=output.call_id,
                    name=output.name,
                    raw_input=output.arguments,
                    input=parsed_input,
                )
            )
        elif output.type == "reasoning":
            ai_message.reasoning = Reasoning(
                id=output.id,
                summaries=[summary.text for summary in output.summary]
                if output.summary
                else [],
                contents=[content.text for content in output.content] if output.content else [],
            )

        else:
            raise ValueError(f"Unknown output type: {output.type}")
    return ai_message


class OAIStreamMessageBuilder:
    """
    Builder for constructing AIMessage from streaming OpenAI responses.
    
    This class accumulates streaming events from OpenAI's API and builds
    a complete response object incrementally.
    
    Attributes:
        events: List of all received stream events
        
    Example:
        >>> builder = OAIStreamMessageBuilder()
        >>> for event in stream:
        ...     response = builder.add_event(event)
        ...     # Process incremental response
        >>> final_response = builder.response
    """
    
    def __init__(self):
        """Initialize an empty message builder."""
        self._response: OAIResponse | None = None
        self.events: list[ResponseStreamEvent] = []

    @property
    def response(self) -> OAIResponse:
        """
        Get the current response object.
        
        Returns:
            The accumulated response
            
        Raises:
            ValueError: If response has not been initialized yet
        """
        if self._response is None:
            raise ValueError("Response not initialized")
        return self._response

    def add_event(self, event: ResponseStreamEvent) -> OAIResponse:
        """
        Add a streaming event and update the response.
        
        Processes different event types and updates the internal response
        object accordingly. Handles text deltas, function call arguments,
        reasoning content, and completion events.
        
        Args:
            event: The stream event to process
            
        Returns:
            The updated response object
            
        Raises:
            ValueError: If an unknown event type is encountered
        """
        self.events.append(event)
        self.events.append(event)
        if event.type in ("response.created", "response.in_progress"):
            self._response = event.response.model_copy()
        elif event.type == "response.output_item.added":
            self.response.output.append(event.item.model_copy())
        elif event.type == "response.content_part.added":
            self.response.output[  # type: ignore[attr-defined]
                event.output_index
            ].content.append(event.part)
        elif event.type == "response.reasoning_summary_part.added":
            self.response.output[  # type: ignore[attr-defined]
                event.output_index
            ].summary.append(event.part)
        elif event.type == "response.reasoning_summary_text.delta":
            self.response.output[  # type: ignore[attr-defined]
                event.output_index
            ].summary[event.summary_index].text += event.delta
        elif event.type == "response.reasoning_summary_text.done":
            self.response.output[  # type: ignore[attr-defined]
                event.output_index
            ].summary[event.summary_index].text = event.text
        elif event.type == "response.reasoning_summary_part.done":
            self.response.output[  # type: ignore[attr-defined]
                event.output_index
            ].summary[event.summary_index] = event.part.model_copy()
        elif event.type == "response.output_text.delta":
            self.response.output[  # type: ignore[attr-defined]
                event.output_index
            ].content[event.content_index].text += event.delta
        elif event.type == "response.output_text.done":
            self.response.output[  # type: ignore[attr-defined]
                event.output_index
            ].content[event.content_index].text = event.text
        elif event.type == "response.content_part.done":
            self.response.output[  # type: ignore[attr-defined]
                event.output_index
            ].content[event.content_index] = event.part.model_copy()
        elif event.type == "response.output_item.done":
            self.response.output[event.output_index] = event.item.model_copy()
        elif event.type == "response.function_call_arguments.delta":
            self.response.output[  # type: ignore[attr-defined]
                event.output_index
            ].arguments += event.delta
        elif event.type == "response.function_call_arguments.done":
            self.response.output[  # type: ignore[attr-defined]
                event.output_index
            ].arguments = event.arguments
        elif event.type == "response.completed":
            self._response = event.response.model_copy()
        else:
            raise ValueError(f"Unknown event type: {event.type}")
        return self.response
