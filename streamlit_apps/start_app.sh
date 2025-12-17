#!/bin/bash
# Quick start script for Mahindra Bot Streamlit App

echo "🚗 Starting Mahindra Bot Streamlit App..."
echo ""

# Check if running from project root
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   cd /path/to/scrape && ./streamlit_apps/start_app.sh"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Make sure OPENAI_API_KEY is set in your environment"
    echo ""
fi

# Run the app
echo "🚀 Launching application..."
echo "   Access the app at: http://localhost:8501"
echo ""
conda run -n scrape streamlit run streamlit_apps/mahindra_bot_app.py
