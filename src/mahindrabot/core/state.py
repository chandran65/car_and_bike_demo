"""State management for OTP and booking flow."""

from datetime import datetime, timedelta
from typing import Optional


class StateManager:
    """In-memory state management for OTP and booking flow."""
    
    def __init__(self):
        """Initialize empty state storage."""
        self._state: dict[str, dict] = {}
    
    def store_otp(self, phone: str, otp: str, name: str) -> None:
        """
        Store OTP with user info and timestamp.
        
        Args:
            phone: User's phone number (used as key)
            otp: Generated OTP code
            name: User's name
        """
        self._state[phone] = {
            "otp": otp,
            "name": name,
            "timestamp": datetime.now(),
        }
    
    def verify_otp(self, phone: str, otp: str) -> tuple[bool, Optional[str]]:
        """
        Verify OTP and return (success, name).
        
        Clears OTP from state on successful verification.
        Checks for expiry (10 minutes).
        
        Args:
            phone: User's phone number
            otp: OTP to verify
            
        Returns:
            Tuple of (success boolean, user name if successful or None)
        """
        if phone not in self._state:
            return False, None
        
        stored = self._state[phone]
        
        # Check expiry (10 minutes)
        if datetime.now() - stored["timestamp"] > timedelta(minutes=10):
            del self._state[phone]
            return False, None
        
        # Verify OTP
        if stored["otp"] == otp:
            name = stored["name"]
            del self._state[phone]
            return True, name
        
        return False, None
    
    def cleanup_expired(self, expiry_minutes: int = 10) -> None:
        """
        Remove expired OTPs from state.
        
        Args:
            expiry_minutes: Number of minutes after which OTPs expire (default: 10)
        """
        now = datetime.now()
        expired = [
            phone for phone, data in self._state.items()
            if now - data["timestamp"] > timedelta(minutes=expiry_minutes)
        ]
        for phone in expired:
            del self._state[phone]
