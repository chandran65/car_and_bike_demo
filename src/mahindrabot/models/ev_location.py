"""Pydantic models for EV charging location data structures."""

from typing import Optional

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    """Geographic coordinates."""
    
    latitude: str = Field(..., description="Latitude coordinate")
    longitude: str = Field(..., description="Longitude coordinate")


class EVLocationResult(BaseModel):
    """
    Result model for EV charging station location.
    
    Contains all information about an EV charging station including
    location, charging specifications, operating hours, and payment details.
    """
    
    # Basic information
    id: str = Field(..., description="Unique identifier for the charging station")
    name: Optional[str] = Field(None, description="Name of the charging station")
    address: str = Field(..., description="Street address of the charging station")
    city: str = Field(..., description="City where the charging station is located")
    postal_code: str = Field(..., description="Postal code of the charging station")
    country: str = Field(..., description="Country where the charging station is located")
    
    # Location coordinates
    latitude: str = Field(..., description="Latitude coordinate")
    longitude: str = Field(..., description="Longitude coordinate")
    coordinates: Coordinates = Field(..., description="Geographic coordinates object")
    
    # Distance (calculated field)
    distance_km: Optional[float] = Field(None, description="Distance from search location in kilometers")
    
    # Charging specifications
    capacity: str = Field(..., description="Charging capacity (e.g., '3.3kw')")
    charger_type: str = Field(..., description="Type of charger (e.g., 'LEV AC')")
    charging_type: str = Field(..., description="Charging or battery swap type")
    no_of_chargers: int = Field(..., description="Total number of chargers available")
    available: int = Field(..., description="Number of chargers currently available")
    
    # Operating hours
    timing: str = Field(..., description="Operating hours in format 'HH:MM:SS - HH:MM:SS'")
    open: str = Field(..., description="Opening time in HH:MM:SS format")
    close: str = Field(..., description="Closing time in HH:MM:SS format")
    staff: str = Field(..., description="Staffing status (e.g., 'Staffed', 'Unstaffed')")
    
    # Payment information
    cost_per_unit: int = Field(..., description="Cost per unit of electricity in INR")
    payment_modes: str = Field(..., description="Accepted payment modes")
    
    # Additional information
    vendor: str = Field(..., description="Vendor/operator of the charging station")
    contact_number: Optional[str] = Field(None, description="Contact phone number")
    
    # Google Maps link (generated field)
    google_maps_link: Optional[str] = Field(None, description="Google Maps link for the location")

