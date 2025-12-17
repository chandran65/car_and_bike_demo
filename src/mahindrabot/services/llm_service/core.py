"""Core LLM interaction functions for text generation and streaming."""

import contextlib
from collections.abc import Callable, Generator
from typing import TypeVar, cast

from langfuse import observe
from langfuse.openai import openai
from pydantic import BaseModel, ValidationError

from .config import LLMConfig
from .messages import AIMessage, MessageType
from .tools import Tool
from .utils import (
    OAIStreamMessageBuilder,
    _get_ai_message_from_oai_response,
    _get_aoi_tool,
    _get_instruction_from_messages,
    _get_oai_messages,
    parse_partial_json,
)

# Type variable for structured output schemas
OutputSchemaType = TypeVar("OutputSchemaType", bound=BaseModel)


@observe(name="get_llm_response")
def get_llm_response(
    llm_config: LLMConfig, messages: list[MessageType], tools: list[Tool | Callable] | None = None
) -> AIMessage:
    """
    Get a synchronous response from the LLM.
    
    Makes a single API call and returns the complete response. Supports
    tool/function calling if tools are provided.
    
    Args:
        llm_config: Configuration for the LLM (model, temperature, etc.)
        messages: List of conversation messages
        tools: Optional list of tools/functions the LLM can call
        
    Returns:
        AIMessage containing the LLM's response, potentially with tool calls
        
    Example:
        >>> from llm_service import LLMConfig, SystemMessage, UserMessage, get_llm_response
        >>> config = LLMConfig(model_id="gpt-4")
        >>> messages = [
        ...     SystemMessage(content="You are a helpful assistant"),
        ...     UserMessage(content="What is 2+2?")
        ... ]
        >>> response = get_llm_response(config, messages)
        >>> print(response.content)
        '2+2 equals 4'
    """
    response = openai.OpenAI().responses.create(  # type: ignore[call-overload]
        model=llm_config.model_id,
        input=_get_oai_messages(messages),
        tools=[_get_aoi_tool(tool) for tool in tools] if tools else [],
        temperature=llm_config.model_args.temperature,
        max_output_tokens=llm_config.model_args.max_tokens,
        instructions=_get_instruction_from_messages(messages),
    )
    return _get_ai_message_from_oai_response(response)


@observe(name="get_llm_structured_response")
def get_llm_structured_response(
    llm_config: LLMConfig, messages: list[MessageType], response_model: type[OutputSchemaType]
) -> OutputSchemaType:
    """
    Get a structured response parsed into a Pydantic model.
    
    Forces the LLM to respond with JSON that conforms to the provided
    Pydantic model schema, with automatic validation.
    
    Args:
        llm_config: Configuration for the LLM
        messages: List of conversation messages
        response_model: Pydantic model class defining the expected response structure
        
    Returns:
        Instance of response_model populated with the LLM's structured response
        
    Example:
        >>> from pydantic import BaseModel
        >>> class Recipe(BaseModel):
        ...     name: str
        ...     ingredients: list[str]
        ...     steps: list[str]
        >>> 
        >>> messages = [
        ...     UserMessage(content="Give me a recipe for chocolate chip cookies")
        ... ]
        >>> recipe = get_llm_structured_response(config, messages, Recipe)
        >>> print(recipe.name)
        'Chocolate Chip Cookies'
    """
    response = openai.OpenAI().responses.parse(
        model=llm_config.model_id,
        input=_get_oai_messages(messages),  # type: ignore[arg-type]
        text_format=response_model,
        temperature=llm_config.model_args.temperature,
        max_output_tokens=llm_config.model_args.max_tokens,
        instructions=_get_instruction_from_messages(messages),
    )
    return cast("OutputSchemaType", response.output_parsed)


@observe(name="get_llm_stream_response")
def get_llm_stream_response(
    llm_config: LLMConfig,
    messages: list[MessageType],
    tools: list[Tool | Callable] | None = None,
    return_delta_response: bool = False,
) -> Generator[AIMessage, None, AIMessage]:
    """
    Get a streaming response from the LLM.
    
    Yields incremental AIMessage updates as tokens are received, allowing
    for real-time display of the response. The final return value is the
    complete AIMessage.
    
    Args:
        llm_config: Configuration for the LLM
        messages: List of conversation messages
        tools: Optional list of tools/functions the LLM can call
        return_delta_response: If True, yield only deltas (not yet implemented)
        
    Yields:
        AIMessage objects with incrementally more content
        
    Returns:
        The final, complete AIMessage
        
    Raises:
        NotImplementedError: If return_delta_response is True
        ValueError: If no response is received
        
    Example:
        >>> messages = [UserMessage(content="Write a short poem")]
        >>> for partial_msg in get_llm_stream_response(config, messages):
        ...     print(partial_msg.content, end="", flush=True)
        ...     # Displays tokens as they arrive
    """
    if return_delta_response:
        raise NotImplementedError("return_delta_response is not implemented")
    builder = OAIStreamMessageBuilder()
    with openai.OpenAI().responses.stream(  # type: ignore[call-overload]
        model=llm_config.model_id,
        input=_get_oai_messages(messages),
        tools=[_get_aoi_tool(tool) for tool in tools] if tools else [],
        max_output_tokens=llm_config.model_args.max_tokens,
        instructions=_get_instruction_from_messages(messages),
    ) as stream:
        for event in stream:
            yield _get_ai_message_from_oai_response(builder.add_event(event))
    if builder.response is None:
        raise ValueError("No response received")
    return _get_ai_message_from_oai_response(builder.response)


@observe(name="get_llm_structured_stream_response")
def get_llm_structured_stream_response(
    llm_config: LLMConfig, messages: list[MessageType], output_schema: type[OutputSchemaType]
) -> Generator[OutputSchemaType, None, OutputSchemaType]:
    """
    Get a streaming structured response parsed into a Pydantic model.
    
    Combines streaming and structured output - yields partially parsed
    Pydantic models as JSON is received. Only yields when the partial
    JSON is valid according to the schema.
    
    Args:
        llm_config: Configuration for the LLM
        messages: List of conversation messages
        output_schema: Pydantic model class for the response structure
        
    Yields:
        Partially or fully populated instances of output_schema
        
    Returns:
        The final, complete instance of output_schema
        
    Example:
        >>> class Story(BaseModel):
        ...     title: str
        ...     paragraphs: list[str]
        >>> 
        >>> messages = [UserMessage(content="Write a short story")]
        >>> for partial_story in get_llm_structured_stream_response(config, messages, Story):
        ...     print(f"Title so far: {partial_story.title}")
        ...     print(f"Paragraphs: {len(partial_story.paragraphs)}")
    """
    builder = OAIStreamMessageBuilder()
    with openai.OpenAI().responses.stream(  # type: ignore[call-overload]
        model=llm_config.model_id,
        input=_get_oai_messages(messages),
        text_format=output_schema,
        temperature=llm_config.model_args.temperature,
        max_output_tokens=llm_config.model_args.max_tokens,
        instructions=_get_instruction_from_messages(messages),
    ) as stream:
        for event in stream:
            ai_message = _get_ai_message_from_oai_response(builder.add_event(event))
            parsed_json = parse_partial_json(ai_message.content)
            if not parsed_json:
                continue
            with contextlib.suppress(ValidationError):
                yield output_schema(**parsed_json)
    return output_schema(
        **parse_partial_json(_get_ai_message_from_oai_response(builder.response).content)
    )
