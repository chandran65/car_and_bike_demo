# Mahindra Bot Core System

A sophisticated AI agent system for car recommendations, insurance queries, and test drive bookings. The system uses intent classification, skill-based routing, and dynamic tool execution to provide intelligent, context-aware assistance.

## Features

- **Intent Classification**: Automatically classifies user queries into 4 intent types
- **Skill-Based Routing**: Loads appropriate skills and tools based on detected intent
- **Dynamic Tool Execution**: Executes relevant tools from car and FAQ services
- **Streaming Responses**: Real-time streaming of agent responses
- **State Management**: In-memory OTP management for booking flow
- **Error Handling**: Graceful error handling with user-friendly messages

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Initialize Services                     │
│  (CarService, FAQService) → AgentToolKit → Agent            │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                     User Query Input                         │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Intent Classification (Last Message)            │
│  → general_qna | car_recommendation | car_comparison | ...  │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                 Load Skill + Filter Tools                    │
│  Each skill has: instructions + relevant tools               │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│            StreamingChatWithTools Agent                      │
│  Executes tools → Generates response → Streams back          │
└─────────────────────────────────────────────────────────────┘
```

## Intent Types

The system supports 4 intent types:

### 1. general_qna
Questions about insurance, documentation, processes, and policies.

**Tools**: `search_faq`

**Examples**:
- "What documents are needed for RC transfer?"
- "How does car insurance work?"
- "What is the process for vehicle registration?"

### 2. car_recommendation
Finding the right car based on preferences and budget.

**Tools**: `list_cars`, `search_car`

**Examples**:
- "I want a car under 15 lakhs"
- "Show me SUVs with good mileage"
- "What cars do you have with automatic transmission?"

### 3. car_comparison
Comparing multiple cars to make informed decisions.

**Tools**: `get_car_comparison`, `search_car`, `list_cars`

**Examples**:
- "Compare Thar and Scorpio"
- "Which is better between XUV700 and Fortuner?"
- "What's the difference between these two cars?"

### 4. book_ride
Booking a test drive with OTP verification.

**Tools**: `book_ride`, `confirm_ride`, `search_car`, `list_cars`

**Examples**:
- "I want to book a test drive"
- "Schedule a test drive for XUV700"
- "Book a ride for tomorrow"

## Installation

1. Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
# or
uv sync
```

2. Set up environment variables:
```bash
# Required
export OPENAI_API_KEY="your-openai-api-key"

# Optional (for OTP notifications)
export SLACK_WEBHOOK_URL="your-slack-webhook-url"
```

3. Ensure data files are in place:
- Car data: `data/cars/*.json`
- FAQ data: `data/consolidated_faqs.json`

## Usage

### Quick Start

```python
from src.mahindrabot.core import run_mahindra_bot, AgentToolKit
from src.mahindrabot.services import CarService, FAQService
from src.mahindrabot.services.llm_service import LLMConfig

# Initialize services
car_service = CarService("data/cars")
faq_service = FAQService("data/consolidated_faqs.json")

# Create toolkit
toolkit = AgentToolKit(
    car_service=car_service,
    faq_service=faq_service
)

# Configure LLM
llm_config = LLMConfig(model_id="gpt-4o-mini")

# Run conversation
messages = []
user_input = "I want a car under 15 lakhs"

for response in run_mahindra_bot(user_input, messages, toolkit, llm_config):
    if response.final_message:
        print(response.final_message.content)
```

### Interactive Mode

```python
messages = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break
    
    for response in run_mahindra_bot(user_input, messages, toolkit, llm_config):
        if response.final_message:
            print(f"Bot: {response.final_message.content}")
```

### Running the Demo

Run the comprehensive demo showcasing all 4 intent flows:

```bash
python demo_mahindra_bot.py
```

The demo includes:
1. General Q&A example (insurance questions)
2. Car recommendation example (budget-based search)
3. Car comparison example (comparing multiple cars)
4. Test drive booking example (OTP flow)
5. Interactive mode for free-form conversation

## API Reference

### Core Components

#### `run_mahindra_bot`

Main function to run the bot with a user query.

```python
def run_mahindra_bot(
    user_input: str,
    messages: list[MessageType],
    toolkit: AgentToolKit,
    llm_config: LLMConfig,
) -> Generator[AgentResponse, None, AgentResponse]:
    """
    Run the bot with user input and stream responses.
    
    Args:
        user_input: User's query
        messages: Conversation history (modified in place)
        toolkit: AgentToolKit with registered tools
        llm_config: LLM configuration
    
    Yields:
        AgentResponse updates during streaming
    
    Returns:
        Final AgentResponse
    """
```

#### `AgentToolKit`

Toolkit that wraps services and provides 6 tools:

```python
class AgentToolKit:
    def __init__(self, car_service: CarService, faq_service: FAQService):
        """Initialize with car and FAQ services."""
    
    def get_tools(self) -> list:
        """Get all registered tools."""
    
    # Tools:
    # - list_cars: List cars with filters
    # - search_car: Search cars by query
    # - get_car_comparison: Compare multiple cars
    # - search_faq: Search FAQ database
    # - book_ride: Initiate test drive booking
    # - confirm_ride: Confirm booking with OTP
```

### Models

#### `IntentType`

Enum defining the 4 supported intent types:

```python
class IntentType(str, Enum):
    GENERAL_QNA = "general_qna"
    CAR_RECOMMENDATION = "car_recommendation"
    CAR_COMPARISON = "car_comparison"
    BOOK_RIDE = "book_ride"
```

#### `Intent`

Classified user intent with confidence and reasoning:

```python
class Intent(BaseModel):
    intent_name: IntentType
    confidence: float  # 0.0 to 1.0
    reasoning: str
```

#### `Skill`

Skill definition with instructions and tools:

```python
class Skill(BaseModel):
    name: str
    instruction: str
    relevant_tools: list[str]
```

## How It Works

### 1. Intent Classification

When a user sends a message, the system:
- Extracts the **last user message** from history
- Uses LLM structured output to classify intent
- Returns intent type, confidence score, and reasoning

### 2. Skill Loading

Based on the classified intent:
- Loads the appropriate `Skill` from the skills dictionary
- Each skill has specific instructions and relevant tools
- System prompt is updated with skill instructions

### 3. Tool Filtering

Only tools relevant to the current skill are made available:
- `general_qna`: Only `search_faq`
- `car_recommendation`: `list_cars`, `search_car`
- `car_comparison`: `get_car_comparison`, `search_car`, `list_cars`
- `book_ride`: `book_ride`, `confirm_ride`, `search_car`, `list_cars`

### 4. Agent Execution

The `StreamingChatWithTools` agent:
- Uses the filtered tools to execute user requests
- Streams responses in real-time
- Handles tool errors gracefully
- Never reveals tool details to users

## Tools Details

### list_cars

Lists cars with optional filters and pagination.

**Parameters**:
- `limit`: Maximum results
- `offset`: Skip results
- `min_price`, `max_price`: Price range (INR)
- `brand`: Brand name filter
- `body_type`: Body type (SUV, Sedan, etc.)
- `fuel_type`: Fuel type (Petrol, Diesel, etc.)
- `mileage_more_than`, `mileage_less_than`: Mileage range
- `seating_capacity`: Number of seats
- `transmission`: Manual/Automatic
- `engine_displacement_more_than`, `engine_displacement_less_than`: Engine size

**Returns**: JSON string of car list

### search_car

Searches cars by query string with filters.

**Parameters**: Same as `list_cars` plus:
- `query`: Search query string

**Returns**: JSON string of matching cars

### get_car_comparison

Compares multiple cars side-by-side.

**Parameters**:
- `car_ids`: List of car IDs to compare

**Returns**: JSON string with comparison matrix

### search_faq

Searches FAQ database for relevant Q&A pairs.

**Parameters**:
- `query`: Search query
- `limit`: Max results (default 5, hard limit 15)

**Returns**: JSON string of FAQ results or no-results message

**Special Handling**: Returns helpful message if no relevant FAQs found

### book_ride

Initiates test drive booking with OTP generation.

**Parameters**:
- `name`: User's name
- `phone_number`: User's phone number

**Returns**: Confirmation message (OTP sent separately)

**Side Effects**:
- Generates 6-digit OTP
- Stores OTP in state (10-minute expiry)
- Sends Slack notification with OTP

### confirm_ride

Confirms booking by verifying OTP.

**Parameters**:
- `otp`: OTP code to verify

**Returns**: Success or failure message

**Side Effects**: Clears OTP from state on success

## Design Decisions

1. **Functional Architecture**: State passed explicitly, no global state
2. **Service Injection**: Services created externally and injected into toolkit
3. **IntentType Enum**: Strongly typed intent names for safety
4. **ToolKit.register()**: No decorators, explicit tool registration
5. **Last Message Only**: Intent classification focuses on most recent message
6. **FAQ Handling**: `search_faq` only in general_qna skill
7. **Dynamic System Prompts**: Updated based on classified intent
8. **Streaming Support**: Generators throughout for real-time responses
9. **Error Isolation**: Tools handle errors, never leak to user
10. **In-Memory State**: Simple OTP management (10-minute expiry)

## Troubleshooting

### Intent Classification Issues

If intents are misclassified:
- Check the intent classification prompt in `intents.py`
- Adjust confidence thresholds
- Review examples in the prompt

### Tool Execution Errors

If tools fail:
- Check service initialization (CarService, FAQService)
- Verify data files exist and are valid
- Check filter values against available options

### OTP Flow Issues

If OTP verification fails:
- Check 10-minute expiry window
- Verify phone number matches between book_ride and confirm_ride
- Check Slack webhook URL if notifications aren't sent

### Streaming Issues

If responses don't stream:
- Ensure you're iterating through the generator
- Check LLM configuration (model availability)
- Verify network connectivity to OpenAI

## Development

### Adding a New Intent

1. Add to `IntentType` enum in `models.py`
2. Update intent classification prompt in `intents.py`
3. Define skill in `skills.py` with instructions and tools
4. Add to `SKILLS` dictionary

### Adding a New Tool

1. Implement tool method in `AgentToolKit` class
2. Register in `_register_tools()` method
3. Add tool name to relevant skills
4. Update documentation

### Testing

Run tests for each component:

```bash
# Test models
python -m pytest tests/test_core_models.py

# Test toolkit
python -m pytest tests/test_core_toolkit.py

# Test intent classification
python -m pytest tests/test_core_intents.py

# Test agent flow
python -m pytest tests/test_core_agent.py
```

## Future Enhancements

1. **Persistent State**: Replace in-memory OTP storage with Redis/database
2. **Multi-turn Context**: Use conversation history for intent classification
3. **Tool Metrics**: Track tool usage and success rates
4. **Intent Confidence**: Handle low-confidence classifications better
5. **Custom Tools**: Plugin system for adding custom tools
6. **Async Support**: Async versions of all functions
7. **Caching**: Cache FAQ embeddings and car data
8. **Multi-language**: Support for multiple languages

## License

Copyright © 2024 Mahindra Bot Project

## Support

For issues, questions, or contributions, please contact the development team.
