# Mahindra Bot Streamlit App - Quick Start Guide

## 🚀 Launch the App (3 Steps)

### Step 1: Verify Prerequisites
```bash
# Test components
conda run -n scrape python streamlit_apps/test_app.py
```

### Step 2: Start the App
```bash
# Option A: Using the quick start script
./streamlit_apps/start_app.sh

# Option B: Direct command
conda run -n scrape streamlit run streamlit_apps/mahindra_bot_app.py
```

### Step 3: Open Browser
Navigate to: **http://localhost:8501**

---

## 💬 Example Conversations

### 1. General Q&A
```
You: What documents are needed for RC transfer?
Bot: [Searches FAQs and provides detailed answer]
```

### 2. Car Recommendation
```
You: I want to buy a car under 15 lakhs
Bot: [Lists suitable cars with details]

You: Show me SUVs with good mileage
Bot: [Filters and shows SUV options]
```

### 3. Car Comparison
```
You: Compare Mahindra Thar and Scorpio
Bot: [Shows detailed comparison table]

You: Which one is better for families?
Bot: [Provides recommendation based on features]
```

### 4. Test Drive Booking
```
You: I want to book a test drive for XUV700
Bot: [Initiates booking flow, asks for details]

You: My name is John and phone is 9876543210
Bot: [Processes booking, sends OTP]
```

---

## 🎯 Key Features to Try

1. **Intent Detection** - Watch the sidebar show detected intent
2. **Tool Calls** - Expand tool sections to see execution details
3. **Streaming** - Notice real-time response updates
4. **Reset** - Click "Reset Chat" to start fresh
5. **Multi-turn** - Ask follow-up questions to test context

---

## ⚠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| API key error | `export OPENAI_API_KEY='your-key'` |
| Data not found | Run `python scripts/consolidate_faqs.py` |
| Port in use | Stop other Streamlit apps or use `--server.port 8502` |
| Slow responses | First response loads services; subsequent faster |

---

## 📚 Documentation

- **Full Documentation**: [README.md](README.md)
- **Implementation Details**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Test Script**: `test_app.py`

---

**Need Help?** Check the [main README](README.md) for detailed instructions.
