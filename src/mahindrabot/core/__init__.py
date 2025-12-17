"""
Mahindra Bot Core - Agent system for car recommendations, insurance queries, and bookings.

This module provides the core functionality for the Mahindra Bot agent system:
- Intent classification
- Skill-based routing
- Tool execution via AgentToolKit
- Streaming agent responses

Example:
    >>> from mahindrabot.core import run_mahindra_bot, AgentToolKit, IntentType
    >>> from mahindrabot.services import CarService, FAQService
    >>> from mahindrabot.services.llm_service import LLMConfig
    >>> 
    >>> # Initialize services
    >>> car_service = CarService("data/cars")
    >>> faq_service = FAQService("data/consolidated_faqs.json")
    >>> 
    >>> # Create toolkit
    >>> toolkit = AgentToolKit(car_service=car_service, faq_service=faq_service)
    >>> 
    >>> # Run bot
    >>> config = LLMConfig(model_id="gpt-4o-mini")
    >>> messages = []
    >>> 
    >>> for response in run_mahindra_bot("I want a car under 15 lakhs", messages, toolkit, config):
    ...     if response.final_message:
    ...         print(response.final_message.content)
"""

from .agent import run_mahindra_bot
from .models import Intent, IntentType, Skill
from .skills import SKILLS
from .toolkit import AgentToolKit

__all__ = [
    "run_mahindra_bot",
    "AgentToolKit",
    "Skill",
    "Intent",
    "IntentType",
    "SKILLS",
]

__version__ = "0.1.0"
