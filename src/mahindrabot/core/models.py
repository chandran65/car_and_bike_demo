"""Core data models for the Mahindra Bot agent system."""

from enum import Enum

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """Enum for supported intent types."""
    
    GREETING = "greeting"
    GENERAL_QNA = "general_qna"
    CAR_RECOMMENDATION = "car_recommendation"
    CAR_COMPARISON = "car_comparison"
    BOOK_RIDE = "book_ride"
    FIND_EV_CHARGER_LOCATION = "find_ev_charger_location"
    BIKE_RECOMMENDATION = "bike_recommendation"
    BIKE_COMPARISON = "bike_comparison"


class Intent(BaseModel):
    """Classified user intent with confidence."""
    
    intent_name: IntentType = Field(..., description="The classified intent type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")


class Skill(BaseModel):
    """Skill definition with instructions and associated tools."""
    
    name: str = Field(..., description="Name of the skill")
    instruction: str = Field(..., description="Detailed instructions for the agent when using this skill")
    relevant_tools: list[str] = Field(..., description="List of tool names relevant to this skill")
