"""
Demo script for Mahindra Bot Core System.

This script demonstrates all 4 intent flows:
1. general_qna - Insurance and documentation questions
2. car_recommendation - Finding the right car
3. car_comparison - Comparing multiple cars
4. book_ride - Booking a test drive

Usage:
    python demos/demo_mahindra_bot.py

Requirements:
    - OpenAI API key set in environment (OPENAI_API_KEY)
    - Car data in data/cars/ directory
    - FAQ data in data/consolidated_faqs.json
    - (Optional) Slack webhook URL for OTP notifications (SLACK_WEBHOOK_URL)
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from mahindrabot.core import AgentToolKit, run_mahindra_bot
from mahindrabot.services.car_service import CarService
from mahindrabot.services.faq_service import FAQService
from mahindrabot.services.llm_service import LLMConfig, ModelArgs

# Load environment variables
load_dotenv()


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_response(response):
    """Print agent response with proper formatting."""
    # Print tool calls if any
    for step in response.steps:
        if step.tool_results and step.status == "done":
            for tool_result in step.tool_results:
                if tool_result.output:
                    print(f"  🔧 Tool: {tool_result.name}")
    
    # Print final message
    if response.final_message:
        print(f"\n  🤖 Bot: {response.final_message.content}\n")


def demo_general_qna(toolkit, llm_config):
    """Demonstrate general Q&A about insurance."""
    print_section("Demo 1: General Q&A (Insurance Questions)")
    
    messages = []
    
    # Question 1: RC Transfer
    print("👤 User: What documents are needed for RC transfer?")
    user_input = "What documents are needed for RC transfer?"
    
    for response in run_mahindra_bot(user_input, messages, toolkit, llm_config):
        pass  # Stream through
    
    print_response(response)
    
    # Question 2: Insurance
    print("👤 User: How does car insurance work?")
    user_input = "How does car insurance work?"
    
    for response in run_mahindra_bot(user_input, messages, toolkit, llm_config):
        pass
    
    print_response(response)


def demo_car_recommendation(toolkit, llm_config):
    """Demonstrate car recommendation based on budget."""
    print_section("Demo 2: Car Recommendation")
    
    messages = []
    
    # Request: Car under budget
    print("👤 User: I want to buy a car under 15 lakhs. What do you recommend?")
    user_input = "I want to buy a car under 15 lakhs. What do you recommend?"
    
    for response in run_mahindra_bot(user_input, messages, toolkit, llm_config):
        pass
    
    print_response(response)
    
    # Follow-up: SUV preference
    print("👤 User: I prefer an SUV with good mileage")
    user_input = "I prefer an SUV with good mileage"
    
    for response in run_mahindra_bot(user_input, messages, toolkit, llm_config):
        pass
    
    print_response(response)


def demo_car_comparison(toolkit, llm_config):
    """Demonstrate car comparison."""
    print_section("Demo 3: Car Comparison")
    
    messages = []
    
    # Request: Compare cars
    print("👤 User: Can you compare Mahindra Thar and Scorpio?")
    user_input = "Can you compare Mahindra Thar and Scorpio?"
    
    for response in run_mahindra_bot(user_input, messages, toolkit, llm_config):
        pass
    
    print_response(response)
    
    # Follow-up: Which is better for families
    print("👤 User: Which one is better for families?")
    user_input = "Which one is better for families?"
    
    for response in run_mahindra_bot(user_input, messages, toolkit, llm_config):
        pass
    
    print_response(response)


def demo_book_ride(toolkit, llm_config):
    """Demonstrate test drive booking flow."""
    print_section("Demo 4: Book Test Drive")
    
    messages = []
    
    # Request: Book test drive
    print("👤 User: I want to book a test drive for XUV700")
    user_input = "I want to book a test drive for XUV700"
    
    for response in run_mahindra_bot(user_input, messages, toolkit, llm_config):
        pass
    
    print_response(response)
    
    # Provide details (simulated - in real flow, bot would ask for these)
    print("👤 User: My name is John Doe and my phone number is 9876543210")
    user_input = "My name is John Doe and my phone number is 9876543210"
    
    for response in run_mahindra_bot(user_input, messages, toolkit, llm_config):
        pass
    
    print_response(response)
    
    # Note: In a real scenario, the user would receive an OTP
    # For demo purposes, we'll show what happens with OTP verification
    print("\n  ℹ️  Note: In production, user would receive OTP via SMS/notification")
    print("  ℹ️  Check Slack for OTP if SLACK_WEBHOOK_URL is configured\n")


def demo_interactive_mode(toolkit, llm_config):
    """Run interactive conversation mode."""
    print_section("Interactive Mode")
    print("  Type your questions below. Type 'exit' or 'quit' to end.\n")
    
    messages = []
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n  👋 Goodbye! Thank you for using Mahindra Bot.\n")
                break
            
            # Run bot
            final_response = None
            for response in run_mahindra_bot(user_input, messages, toolkit, llm_config):
                final_response = response
            
            if final_response:
                print_response(final_response)
        
        except KeyboardInterrupt:
            print("\n\n  👋 Goodbye! Thank you for using Mahindra Bot.\n")
            break
        except Exception as e:
            print(f"\n  ❌ Error: {e}\n")


def main():
    """Run all demos."""
    print("\n" + "🚗 " + "=" * 78)
    print("  MAHINDRA BOT CORE SYSTEM - DEMO")
    print("  Showcasing Intent Classification, Skills, and Tool Execution")
    print("=" * 80)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ Error: OPENAI_API_KEY not set in environment")
        print("   Please set your OpenAI API key to run the demo.\n")
        return
    
    # Check for required data
    car_data_path = Path("data/new_car_details")
    faq_data_path = Path("data/consolidated_faqs.json")
    
    if not car_data_path.exists():
        print(f"\n❌ Error: Car data not found at {car_data_path}")
        print("   Please ensure car JSON files are in the data/new_car_details directory.\n")
        return
    
    if not faq_data_path.exists():
        print(f"\n❌ Error: FAQ data not found at {faq_data_path}")
        print("   Please ensure consolidated_faqs.json is in the data directory.\n")
        return
    
    print("\n✅ Environment checks passed")
    
    # Initialize services
    print("\n📦 Initializing services...")
    try:
        car_service = CarService(str(car_data_path))
        faq_service = FAQService(str(faq_data_path))
        print("   ✓ Car service loaded")
        print("   ✓ FAQ service loaded")
    except Exception as e:
        print(f"\n❌ Error initializing services: {e}\n")
        return
    
    # Create toolkit
    print("\n🔧 Creating AgentToolKit...")
    toolkit = AgentToolKit(car_service=car_service, faq_service=faq_service)
    print(f"   ✓ Registered {len(toolkit.get_tools())} tools")
    
    # Configure LLM
    llm_config = LLMConfig(
        model_id="gpt-4o-mini",
        model_args=ModelArgs(temperature=0.7, max_tokens=1000)
    )
    print(f"   ✓ Using model: {llm_config.model_id}")
    
    # Run demos
    print("\n🎬 Starting demonstrations...\n")
    
    try:
        # Run each demo
        demo_general_qna(toolkit, llm_config)
        demo_car_recommendation(toolkit, llm_config)
        demo_car_comparison(toolkit, llm_config)
        demo_book_ride(toolkit, llm_config)
        
        print_section("All Demos Complete!")
        print("  All 4 intent flows have been demonstrated:")
        print("    ✓ General Q&A (insurance questions)")
        print("    ✓ Car Recommendation (finding the right car)")
        print("    ✓ Car Comparison (comparing multiple cars)")
        print("    ✓ Book Ride (test drive booking)")
        
        # Offer interactive mode
        print("\n  Would you like to try interactive mode? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice in ['y', 'yes']:
            demo_interactive_mode(toolkit, llm_config)
        else:
            print("\n  👋 Thank you for trying Mahindra Bot!\n")
    
    except KeyboardInterrupt:
        print("\n\n  Demo interrupted. Exiting...\n")
    except Exception as e:
        print(f"\n❌ Error during demo: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
