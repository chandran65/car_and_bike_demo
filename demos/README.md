# Demos

This folder contains demonstration scripts showcasing various features of the Mahindra Bot system.

## Available Demos

### 1. `demo.py` - Car Service Demo
Basic demonstration of CarService functionality with real data:
- Get car details
- Search and filter cars
- Compare multiple cars

**Run:**
```bash
conda run -n scrape python demos/demo.py
```

### 2. `demo_errors.py` - Error Handling Demo
Demonstrates error handling with invalid inputs:
- Invalid car IDs
- Invalid filters (brand, body type, fuel type, transmission)
- Fuzzy matching suggestions

**Run:**
```bash
conda run -n scrape python demos/demo_errors.py
```

### 3. `demo_faq.py` - FAQ Service Demo (Interactive)
Interactive demonstration of FAQ Search Service:
- Semantic search using OpenAI embeddings
- Category coverage
- Search quality metrics
- Score distribution
- Interactive search mode

**Run:**
```bash
conda run -n scrape python demos/demo_faq.py
```

### 4. `demo_faq_auto.py` - FAQ Service Demo (Automated)
Automated, non-interactive version of FAQ Search Service demo:
- All features of `demo_faq.py` without user interaction
- Performance metrics
- Cache information

**Run:**
```bash
conda run -n scrape python demos/demo_faq_auto.py
```

### 5. `demo_llm_service.py` - LLM Service Demo
Comprehensive demo of the refactored LLM Service:
- Configuration and message creation
- Tool system with decorators
- Basic LLM interactions
- Structured output
- Streaming responses
- Agent with tool calling

**Requirements:** OPENAI_API_KEY environment variable

**Run:**
```bash
conda run -n scrape python demos/demo_llm_service.py
```

### 6. `demo_mahindra_bot.py` - Mahindra Bot Core Demo
Complete demonstration of all 4 intent flows:
1. **general_qna** - Insurance and documentation questions
2. **car_recommendation** - Finding the right car
3. **car_comparison** - Comparing multiple cars
4. **book_ride** - Booking a test drive

Includes an interactive mode for real-time testing.

**Requirements:**
- OPENAI_API_KEY environment variable
- Car data in `data/new_car_details/`
- FAQ data in `data/consolidated_faqs.json`
- (Optional) SLACK_WEBHOOK_URL for OTP notifications

**Run:**
```bash
conda run -n scrape python demos/demo_mahindra_bot.py
```

## Running from Root

All demos are designed to be run from the project root directory:

```bash
# Ensure you're in the project root
cd /path/to/scrape

# Run any demo using the scrape conda environment
conda run -n scrape python demos/<demo_name>.py
```

## Setup

The project must be installed in editable mode for the demos to work:

```bash
conda activate scrape
pip install -e .
```

This is already done if you're seeing this README, but if you encounter import errors, run the above command.

## Notes

- All demos assume they are run from the project root directory
- Import paths use `mahindrabot` package directly (no `src.` prefix needed)
- Some demos require API keys and data files - check individual requirements above
