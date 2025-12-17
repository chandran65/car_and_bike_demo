"""Configuration models for LLM service."""

from pydantic import BaseModel, Field


class ModelArgs(BaseModel):
    """
    Arguments for configuring LLM model behavior.
    
    Attributes:
        temperature: Controls randomness in generation (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum number of tokens to generate in the response
    """
    
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for sampling (0.0-2.0)"
    )
    max_tokens: int = Field(
        default=2000,
        gt=0,
        description="Maximum tokens in response"
    )


class LLMConfig(BaseModel):
    """
    Configuration for LLM service interactions.
    
    Attributes:
        model_id: The identifier of the model to use (e.g., 'gpt-4', 'gpt-3.5-turbo')
        model_args: Model-specific arguments for generation behavior
        
    Example:
        >>> config = LLMConfig(model_id="gpt-4")
        >>> config.model_args.temperature
        0.7
        >>> custom_config = LLMConfig(
        ...     model_id="gpt-3.5-turbo",
        ...     model_args=ModelArgs(temperature=0.9, max_tokens=1000)
        ... )
    """
    
    model_id: str = Field(
        default="gpt-4",
        description="Model identifier (e.g., 'gpt-4', 'gpt-3.5-turbo')"
    )
    model_args: ModelArgs = Field(
        default_factory=ModelArgs,
        description="Model generation arguments"
    )
