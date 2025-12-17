# Mahindra Bot Streamlit Application

A rich, interactive web interface for the Mahindra Bot that enables users to interact with the bot through a modern chat interface.

## Features

- 💬 **Chat Interface** - Intuitive chat interface with streaming responses
- 🎯 **Intent Detection** - Real-time intent classification with confidence levels
- 🔧 **Tool Visualization** - See tool executions with expandable details
- 📜 **Conversation History** - Full conversation tracking with chat bubbles
- 🔄 **Reset Functionality** - Clear chat history and start fresh
- ⚙️ **Configuration Display** - View active model and service status

## Supported Features

The app supports all 4 Mahindra Bot intents:

1. **🤔 General Q&A** - Insurance and documentation questions
2. **🚗 Car Recommendation** - Finding the right car based on budget and preferences
3. **⚖️ Car Comparison** - Comparing multiple cars side-by-side
4. **📅 Book Test Drive** - Schedule test drive appointments

## Prerequisites

Before running the application, ensure you have:

1. **Python Environment** - Python 3.12 or higher
2. **Dependencies Installed** - All required packages from `pyproject.toml`
3. **OpenAI API Key** - Set in environment or `.env` file
4. **Data Files**:
   - Car data: `data/new_car_details/` (with JSON files)
   - FAQ data: `data/consolidated_faqs.json`

## Installation

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd scrape
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your-api-key-here
   ```
   
   Or export directly:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

4. **Ensure data files exist**
   ```bash
   # Check for car data
   ls data/new_car_details/
   
   # Check for FAQ data
   ls data/consolidated_faqs.json
   ```

## Usage

### Starting the Application

From the project root directory:

```bash
streamlit run streamlit_apps/mahindra_bot_app.py
```

The application will open in your default browser at `http://localhost:8501`

### Using the Chat Interface

1. **Type your question** in the chat input at the bottom
2. **Press Enter** to submit
3. **Watch the response stream** in real-time
4. **Expand tool calls** to see detailed execution information
5. **Continue the conversation** - context is maintained across messages

### Example Queries

#### General Q&A
```
What documents are needed for RC transfer?
How does car insurance work?
What are the RTO fees in Delhi?
```

#### Car Recommendation
```
I want to buy a car under 15 lakhs
Show me SUVs with good mileage
What are the best family cars?
```

#### Car Comparison
```
Compare Mahindra Thar and Scorpio
What's the difference between XUV700 and XUV300?
Compare prices of Thar and Bolero
```

#### Test Drive Booking
```
I want to book a test drive for XUV700
Schedule a test drive for Scorpio N
Book a test drive at my location
```

## User Interface

### Main Chat Area
- **User messages** - Displayed on the right with user icon
- **Assistant messages** - Displayed on the left with assistant icon
- **Tool executions** - Shown as expandable sections with:
  - Tool name and status (✅ success / ❌ failure)
  - Input parameters (JSON format)
  - Output results (formatted text)
  - Metadata (if available)

### Sidebar

#### Configuration Section
- Current model being used
- Temperature setting
- Service status indicators

#### Available Intents
- Lists all 4 supported intent types
- Helps users understand capabilities

#### Current Intent (when active)
- Detected intent with emoji
- Confidence level (progress bar)
- Reasoning for classification
- Active tools being used

#### Reset Button
- Clears entire conversation history
- Resets session state
- Starts fresh conversation

## Troubleshooting

### Application won't start

**Error: `OPENAI_API_KEY not set`**
```bash
# Solution: Set API key in environment
export OPENAI_API_KEY='your-key-here'
```

**Error: `Car data directory not found`**
```bash
# Solution: Ensure data files exist
ls data/new_car_details/
# Should show JSON files for cars
```

**Error: `FAQ data file not found`**
```bash
# Solution: Run FAQ consolidation script
python scripts/consolidate_faqs.py
```

### Services fail to initialize

Check that all data files are present:
```bash
# Verify car data (should have 200+ JSON files)
ls -l data/new_car_details/ | wc -l

# Verify FAQ data (should exist)
cat data/consolidated_faqs.json | python -m json.tool | head
```

### Tool calls not showing

Tool calls are collapsed by default. Click on the expandable sections to see details.

### Slow responses

- First response may take longer (service initialization)
- Subsequent responses should be faster
- Streaming provides progressive updates

## Architecture

### Component Overview

```
mahindra_bot_app.py
├── Configuration & Setup
│   ├── check_prerequisites()
│   └── initialize_services()
├── Message Rendering
│   ├── render_ai_response()
│   └── render_conversation_history()
├── Sidebar Components
│   └── render_sidebar()
└── Main Application
    └── main()
```

### Data Flow

1. User enters message → Chat input
2. Message added to history → Session state
3. Bot processes request → `run_mahindra_bot()`
4. Intent classified → Displayed in sidebar
5. Tools executed → Shown in expandable sections
6. Response streamed → Progressive updates
7. Final message displayed → Conversation continues

### Session State

The app maintains the following in session state:
- `messages` - Message history for bot logic
- `conversation_display` - UI display history
- `intent_info` - Current intent metadata
- `agent_toolkit` - Tool registry
- `llm_config` - LLM configuration
- `services_initialized` - Initialization flag

## Configuration Options

### Model Settings

Default configuration:
```python
LLMConfig(
    model_id="gpt-4o-mini",
    model_args=ModelArgs(
        temperature=0.7,
        max_tokens=1500
    )
)
```

To modify, edit `mahindra_bot_app.py`:
```python
st.session_state.llm_config = LLMConfig(
    model_id="gpt-4o",  # Change model
    model_args=ModelArgs(
        temperature=0.5,  # Adjust temperature
        max_tokens=2000   # Increase max tokens
    )
)
```

### Custom Styling

The app includes custom CSS for better appearance. To modify, edit the CSS section in `main()`:
```python
st.markdown("""
<style>
/* Your custom styles here */
</style>
""", unsafe_allow_html=True)
```

## Performance Tips

1. **Service Caching** - Services are initialized once and cached in session state
2. **Streaming** - Responses stream progressively for better UX
3. **Tool Output Truncation** - Long outputs are automatically truncated
4. **Lazy Loading** - Tool details loaded on-demand via expanders

## Development

### Project Structure

```
streamlit_apps/
├── mahindra_bot_app.py    # Main application
└── README.md              # This file
```

### Adding New Features

To add new features:

1. **Add to sidebar** - Modify `render_sidebar()`
2. **Add message type** - Extend `render_ai_response()`
3. **Add configuration** - Update session state initialization
4. **Add UI element** - Add to `main()` function

### Testing

Test the app with different query types:
```bash
# Run the app
streamlit run streamlit_apps/mahindra_bot_app.py

# Test scenarios:
# 1. General Q&A queries
# 2. Car recommendations with filters
# 3. Car comparisons
# 4. Test drive booking flow
# 5. Multi-turn conversations
# 6. Reset functionality
# 7. Error handling (remove API key, etc.)
```

## Related Documentation

- [Main Project README](../README.md)
- [Car Service Documentation](../docs/services/car-service.md)
- [FAQ Service Documentation](../docs/services/faq-service.md)
- [Mahindra Bot Core](../docs/services/mahindra-bot-core.md)

## Support

For issues or questions:
1. Check this README
2. Review main project documentation
3. Check GitHub issues
4. Contact development team

## License

[Your License Here]

---

**Last Updated:** 2024-12-14  
**Version:** 1.0.0  
**Maintained by:** Mahindra Bot Team
