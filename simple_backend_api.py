"""
FastAPI backend for the Mahindra Bot React frontend.
Simplified version without langfuse to avoid compatibility issues.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import sys
from pathlib import Path

app = FastAPI(
    title="Mahindra Bot API",
    description="Backend API for the Mahindra Bot React frontend",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    content: str
    role: str  # "user" or "assistant"
    timestamp: str = None

class PasswordVerification(BaseModel):
    password: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    message: str
    intent: str = None
    tools_used: List[str] = []
    conversation_id: str = None

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Mahindra Bot API is running"}

@app.post("/verify-password")
async def verify_password(request: PasswordVerification):
    """Verify login password. For simple backend, any password 'admin' works."""
    return {"valid": request.password == "admin"}

@app.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """Handle chat messages and return bot response."""
    try:
        # For now, return a mock response while we fix the dependency issues
        user_message = request.message.lower()
        
        # Simple rule-based responses for demo
        if "car" in user_message or "vehicle" in user_message:
            response_text = f"I'd be happy to help you find the perfect car! Based on your query '{request.message}', I can recommend some great options. What's your budget range and preferred features?"
            intent = "car_recommendation"
            tools = ["car_service"]
        elif "bike" in user_message or "motorcycle" in user_message:
            response_text = f"Great choice! I can help you find the ideal bike. For '{request.message}', what type of riding do you plan to do - city commuting, highway touring, or off-road adventures?"
            intent = "bike_recommendation"  
            tools = ["bike_service"]
        elif "charging" in user_message or "ev" in user_message:
            response_text = f"I can help you locate EV charging stations! For '{request.message}', could you share your location or the area where you need charging facilities?"
            intent = "ev_charger_location"
            tools = ["ev_charger_service"]
        elif "insurance" in user_message:
            response_text = f"I'll help you with insurance information! Regarding '{request.message}', are you looking for car insurance, bike insurance, or general vehicle insurance quotes?"
            intent = "insurance_query"
            tools = ["faq_service"]
        elif "hello" in user_message or "hi" in user_message or "hey" in user_message:
            response_text = "Hello! 👋 I'm your Mahindra vehicle assistant. I can help you with car recommendations, bike suggestions, EV charging stations, insurance queries, and more. What can I assist you with today?"
            intent = "greeting"
            tools = []
        else:
            response_text = f"Thank you for your question: '{request.message}'. I can help you with vehicle recommendations, insurance information, EV charging locations, and booking assistance. Could you please be more specific about what you're looking for?"
            intent = "general_qna"
            tools = ["faq_service"]
        
        return ChatResponse(
            message=response_text,
            intent=intent,
            tools_used=tools,
            conversation_id="demo_session"
        )
        
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/intents")
async def get_intents():
    """Get available intent types."""
    return {
        "intents": [
            "greeting",
            "general_qna", 
            "car_recommendation",
            "bike_recommendation",
            "ev_charger_location",
            "insurance_query",
            "booking_assistance",
            "goodbye"
        ]
    }

@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "Mahindra Bot API is running",
        "endpoints": ["/chat", "/intents", "/health"]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Mahindra Bot API...")
    print("📱 React frontend should connect to: http://localhost:8000")
    print("🔧 API documentation available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)