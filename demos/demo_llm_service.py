"""
Demo script for the LLM Service.

This script demonstrates all major features of the refactored LLM service:
- Configuration and message creation
- Tool system with decorators
- Basic LLM interactions
- Structured output
- Streaming responses
- Agent with tool calling

Note: Some examples require OpenAI API key. Set OPENAI_API_KEY environment variable.
"""

import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from mahindrabot.services.llm_service import (
    AgentRequest,
    AIMessage,
    LLMConfig,
    ModelArgs,
    StreamingChatWithTools,
    SystemMessage,
    Tool,
    ToolKit,
    UserMessage,
    get_llm_response,
    get_llm_stream_response,
    get_llm_structured_response,
    get_llm_structured_stream_response,
    tool,
)

# Load environment variables
load_dotenv()


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_configuration():
    """Demonstrate configuration creation."""
    print_section("1. Configuration and Messages")
    
    # Create default config
    config = LLMConfig(model_id="gpt-4")
    print(f"✓ Default Config:")
    print(f"  - Model: {config.model_id}")
    print(f"  - Temperature: {config.model_args.temperature}")
    print(f"  - Max Tokens: {config.model_args.max_tokens}")
    
    # Create custom config
    custom_config = LLMConfig(
        model_id="gpt-3.5-turbo",
        model_args=ModelArgs(temperature=0.9, max_tokens=1000)
    )
    print(f"\n✓ Custom Config:")
    print(f"  - Model: {custom_config.model_id}")
    print(f"  - Temperature: {custom_config.model_args.temperature}")
    print(f"  - Max Tokens: {custom_config.model_args.max_tokens}")
    
    # Create messages
    system_msg = SystemMessage(content="You are a helpful assistant")
    user_msg = UserMessage(content="Hello, how are you?")
    ai_msg = AIMessage(content="I'm doing well, thank you!")
    
    print(f"\n✓ Messages created:")
    print(f"  - {system_msg.role}: {system_msg.content[:30]}...")
    print(f"  - {user_msg.role}: {user_msg.content}")
    print(f"  - {ai_msg.role}: {ai_msg.content}")
    print(f"  - Message IDs: {system_msg.id[:8]}..., {user_msg.id[:8]}..., {ai_msg.id[:8]}...")


def demo_tools():
    """Demonstrate tool system."""
    print_section("2. Tool System")
    
    # Simple tool with decorator
    @tool
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b
    
    print(f"✓ Tool created with @tool decorator:")
    print(f"  - Name: {add_numbers.name}")
    print(f"  - Description: {add_numbers.description}")
    print(f"  - Schema: {list(add_numbers.args_schema.model_fields.keys())}")
    print(f"  - Test call: add_numbers(5, 3) = {add_numbers(5, 3)}")
    
    # Tool with custom metadata
    @tool(name="multiply", description="Multiply two numbers")
    def mult(x: int, y: int) -> int:
        return x * y
    
    print(f"\n✓ Tool with custom metadata:")
    print(f"  - Name: {mult.name}")
    print(f"  - Description: {mult.description}")
    print(f"  - Test call: multiply(4, 6) = {mult(4, 6)}")
    
    # Tool from function
    def divide(numerator: float, denominator: float) -> float:
        """Divide two numbers."""
        if denominator == 0:
            raise ValueError("Cannot divide by zero")
        return numerator / denominator
    
    divide_tool = Tool.from_function(divide)
    print(f"\n✓ Tool from function:")
    print(f"  - Name: {divide_tool.name}")
    print(f"  - Description: {divide_tool.description}")
    print(f"  - Test call: divide(10, 2) = {divide_tool(10.0, 2.0)}")
    
    # ToolKit
    toolkit = ToolKit()
    toolkit.register(add_numbers.func, name="add")
    toolkit.register(mult.func, name="multiply")
    toolkit.register(divide_tool.func, name="divide")
    
    print(f"\n✓ ToolKit:")
    print(f"  - Registered {len(toolkit.get_tools())} tools")
    for t in toolkit.get_tools():
        print(f"    • {t.name}: {t.description}")


def demo_structured_output():
    """Demonstrate structured output models."""
    print_section("3. Structured Output Models")
    
    class WeatherReport(BaseModel):
        """Weather report structure."""
        location: str = Field(description="The location name")
        temperature: float = Field(description="Temperature in Fahrenheit")
        conditions: Literal["sunny", "cloudy", "rainy", "snowy"]
        humidity: int = Field(ge=0, le=100, description="Humidity percentage")
    
    print("✓ Defined WeatherReport model:")
    print(f"  Fields: {list(WeatherReport.model_fields.keys())}")
    
    # Create example instance
    weather = WeatherReport(
        location="San Francisco",
        temperature=65.5,
        conditions="cloudy",
        humidity=75
    )
    print(f"\n✓ Example instance:")
    print(f"  {weather.model_dump_json(indent=2)}")
    
    class Recipe(BaseModel):
        """Recipe structure."""
        name: str
        cuisine: str
        ingredients: list[str]
        steps: list[str]
        prep_time_minutes: int
        servings: int
    
    print(f"\n✓ Defined Recipe model:")
    print(f"  Fields: {list(Recipe.model_fields.keys())}")
    
    # Test structured output with LLM
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Skipping LLM structured output test: OPENAI_API_KEY not set")
        return
    
    try:
        config = LLMConfig(
            model_id="gpt-4o-mini",
            model_args=ModelArgs(temperature=0.7, max_tokens=300)
        )
        
        messages = [
            SystemMessage(content="You are a helpful weather assistant."),
            UserMessage(content="Give me a weather report for Tokyo, Japan.")
        ]
        
        print("\n✓ Testing get_llm_structured_response...")
        print("  Requesting structured weather report from LLM...")
        
        result = get_llm_structured_response(config, messages, WeatherReport)
        
        print(f"\n✓ Received structured response:")
        print(f"  Type: {type(result).__name__}")
        print(f"  Location: {result.location}")
        print(f"  Temperature: {result.temperature}°F")
        print(f"  Conditions: {result.conditions}")
        print(f"  Humidity: {result.humidity}%")
        print(f"\n  Full JSON:")
        print(f"  {result.model_dump_json(indent=2)}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_basic_llm_call():
    """Demonstrate basic LLM call (requires API key)."""
    print_section("4. Basic LLM Call")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Skipping: OPENAI_API_KEY not set")
        print("   Set the environment variable to test actual API calls")
        return
    
    try:
        config = LLMConfig(
            model_id="gpt-4o-mini",
            model_args=ModelArgs(temperature=0.7, max_tokens=100)
        )
        
        messages = [
            SystemMessage(content="You are a helpful math tutor."),
            UserMessage(content="What is 15 multiplied by 23? Just give the answer.")
        ]
        
        print("✓ Sending request to OpenAI...")
        print(f"  Model: {config.model_id}")
        print(f"  Messages: {len(messages)}")
        
        response = get_llm_response(config, messages)
        
        print(f"\n✓ Response received:")
        print(f"  ID: {response.id}")
        print(f"  Content: {response.content}")
        print(f"  Tool calls: {len(response.tool_call_requests)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_structured_streaming():
    """Demonstrate streaming structured output (requires API key)."""
    print_section("5. Streaming Structured Output")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Skipping: OPENAI_API_KEY not set")
        return
    
    try:
        class StoryOutline(BaseModel):
            """Story outline structure."""
            title: str
            genre: str
            characters: list[str]
            plot_points: list[str]
        
        print("✓ Defined StoryOutline model:")
        print(f"  Fields: {list(StoryOutline.model_fields.keys())}")
        
        config = LLMConfig(
            model_id="gpt-4o-mini",
            model_args=ModelArgs(temperature=0.8, max_tokens=300)
        )
        
        messages = [
            SystemMessage(content="You are a creative story planner."),
            UserMessage(content="Create an outline for a sci-fi short story about time travel.")
        ]
        
        print("\n✓ Sending streaming structured request...")
        print("  Streaming story outline as it's generated...\n")
        
        final_outline = None
        update_count = 0
        for partial_outline in get_llm_structured_stream_response(config, messages, StoryOutline):
            update_count += 1
            # Show progress
            if hasattr(partial_outline, 'title') and partial_outline.title:
                print(f"  [{update_count}] Title: {partial_outline.title}")
            if hasattr(partial_outline, 'genre') and partial_outline.genre:
                print(f"  [{update_count}] Genre: {partial_outline.genre}")
            if hasattr(partial_outline, 'characters') and partial_outline.characters:
                print(f"  [{update_count}] Characters: {len(partial_outline.characters)} character(s)")
            if hasattr(partial_outline, 'plot_points') and partial_outline.plot_points:
                print(f"  [{update_count}] Plot points: {len(partial_outline.plot_points)} point(s)")
            final_outline = partial_outline
        
        print(f"\n✓ Streaming complete ({update_count} updates):")
        print(f"  Title: {final_outline.title}")
        print(f"  Genre: {final_outline.genre}")
        print(f"  Characters: {', '.join(final_outline.characters)}")
        print(f"  Plot Points: {len(final_outline.plot_points)}")
        print(f"\n  Full structured output:")
        print(f"  {final_outline.model_dump_json(indent=2)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_streaming():
    """Demonstrate streaming response (requires API key)."""
    print_section("6. Text Streaming Response")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Skipping: OPENAI_API_KEY not set")
        return
    
    try:
        config = LLMConfig(
            model_id="gpt-4o-mini",
            model_args=ModelArgs(temperature=0.8, max_tokens=150)
        )
        
        messages = [
            SystemMessage(content="You are a creative writer."),
            UserMessage(content="Write a one-sentence story about a robot.")
        ]
        
        print("✓ Sending streaming request...")
        print("  Response: ", end="", flush=True)
        
        final_response = None
        token_count = 0
        for partial_response in get_llm_stream_response(config, messages):
            # Print content as it arrives
            if partial_response.content and (
                not final_response or 
                len(partial_response.content) > len(final_response.content)
            ):
                new_content = partial_response.content[
                    len(final_response.content) if final_response else 0:
                ]
                print(new_content, end="", flush=True)
                token_count += len(new_content.split())
            final_response = partial_response
        
        print(f"\n\n✓ Streaming complete:")
        print(f"  Total tokens: ~{token_count}")
        print(f"  Message ID: {final_response.id}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_tool_calling():
    """Demonstrate LLM with tool calling (requires API key)."""
    print_section("7. Tool Calling")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Skipping: OPENAI_API_KEY not set")
        return
    
    try:
        # Define tools
        @tool
        def get_current_weather(location: str, unit: str = "fahrenheit") -> str:
            """Get the current weather in a given location."""
            # Simulated weather data
            weather_data = {
                "san francisco": {"temp": 65, "condition": "cloudy"},
                "paris": {"temp": 72, "condition": "sunny"},
                "tokyo": {"temp": 58, "condition": "rainy"},
            }
            
            loc = location.lower()
            if loc in weather_data:
                data = weather_data[loc]
                return f"Weather in {location}: {data['temp']}°{unit[0].upper()}, {data['condition']}"
            return f"Weather data not available for {location}"
        
        @tool
        def calculate(expression: str) -> str:
            """Calculate a mathematical expression."""
            try:
                result = eval(expression)
                return f"{expression} = {result}"
            except Exception as e:
                return f"Error calculating: {e}"
        
        print("✓ Defined tools:")
        print(f"  - {get_current_weather.name}: {get_current_weather.description}")
        print(f"  - {calculate.name}: {calculate.description}")
        
        config = LLMConfig(model_id="gpt-4o-mini")
        messages = [
            SystemMessage(content="You are a helpful assistant with access to tools."),
            UserMessage(content="What's the weather in Paris?")
        ]
        
        print("\n✓ Sending request with tools...")
        response = get_llm_response(config, messages, tools=[get_current_weather, calculate])
        
        print(f"\n✓ Response:")
        print(f"  Content: {response.content}")
        print(f"  Tool calls: {len(response.tool_call_requests)}")
        
        if response.tool_call_requests:
            for tool_call in response.tool_call_requests:
                print(f"\n  Tool Call:")
                print(f"    - Name: {tool_call.name}")
                print(f"    - Arguments: {tool_call.input}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_agent():
    """Demonstrate agent with tools (requires API key)."""
    print_section("8. Agent with Tools")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Skipping: OPENAI_API_KEY not set")
        return
    
    try:
        # Define tools for the agent
        @tool
        def search_database(query: str) -> str:
            """Search a database for information."""
            # Simulated database
            db = {
                "python": "Python is a high-level programming language.",
                "openai": "OpenAI is an AI research company.",
                "gpt": "GPT stands for Generative Pre-trained Transformer.",
            }
            query_lower = query.lower()
            for key, value in db.items():
                if key in query_lower:
                    return value
            return f"No information found for: {query}"
        
        @tool
        def get_time() -> str:
            """Get the current time."""
            from datetime import datetime
            return datetime.now().strftime("%I:%M %p")
        
        print("✓ Created agent with tools:")
        print(f"  - search_database")
        print(f"  - get_time")
        
        config = LLMConfig(
            model_id="gpt-4o-mini",
            model_args=ModelArgs(temperature=0.7, max_tokens=200)
        )
        
        agent = StreamingChatWithTools(
            llm_config=config,
            tools=[search_database, get_time],
            messages=[SystemMessage(content="You are a helpful assistant with access to tools.")]
        )
        
        request = AgentRequest(user_input="What is Python?")
        print(f"\n✓ User request: {request.user_input}")
        print("\n✓ Agent response stream:")
        
        final_response = None
        for response in agent.ask(request):
            # Show tool calls
            for step in response.steps:
                if step.tool_results and step.status == "pending":
                    for tool_result in step.tool_results:
                        print(f"\n  🔧 Tool Call: {tool_result.name}")
                        print(f"     Input: {tool_result.input}")
                        if tool_result.output:
                            print(f"     Output: {tool_result.output}")
            
            # Show final message
            if response.final_message:
                print(f"\n  💬 Final Answer: {response.final_message.content}")
            
            final_response = response
        
        print(f"\n✓ Agent completed:")
        print(f"  Steps taken: {len(final_response.steps)}")
        print(f"  Has final answer: {final_response.final_message is not None}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all demos."""
    print("\n" + "🚀 " + "=" * 68)
    print("  LLM SERVICE DEMO")
    print("  Showcasing the refactored LLM service functionality")
    print("=" * 70)
    
    # Demos that don't require API key
    demo_configuration()
    demo_tools()
    demo_structured_output()
    
    # Demos that require API key
    demo_basic_llm_call()
    demo_structured_streaming()
    demo_streaming()
    demo_tool_calling()
    demo_agent()
    
    print("\n" + "=" * 70)
    print("  ✅ Demo Complete!")
    print("=" * 70)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n💡 Tip: Set OPENAI_API_KEY environment variable to test API features")
    
    print()


if __name__ == "__main__":
    main()
