"""Pydantic models for bike data structures."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

# Re-using common models would be ideal, but for now defining them here or importing from car?
# To avoid tight coupling if they diverge, I'll redefine or import common base.
# But `car.py` doesn't have a shared base file.
# I will copy the structure for now.

class ImageReference(BaseModel):
    """Reference to an image with unique identifier."""
    url: str
    url_id: str
    alt_text: str


class DimensionValue(BaseModel):
    """Dimension with value and unit."""
    value: float
    unit: str


class DisplacementValue(BaseModel):
    """Engine displacement with value and unit."""
    value: int
    unit: str


class PowerTorqueValue(BaseModel):
    """Power or torque specification."""
    value: float
    unit: str
    rpm: Optional[str] = None


class BasicInfo(BaseModel):
    """Basic bike information."""
    name: str
    manufacturer: Optional[str] = None
    model: str
    body_type: Optional[str] = None  # e.g., Scooter, Cruiser, Sports
    url: Optional[str] = None
    image_url: Optional[ImageReference] = None
    description: Optional[str] = None
    model_date: Optional[str] = None
    sku: Optional[str] = None
    vin: Optional[str] = None
    condition: Optional[str] = None


class Engine(BaseModel):
    """Engine specifications."""
    displacement: Optional[list[DisplacementValue]] = None
    power: Optional[list[PowerTorqueValue]] = None
    torque: Optional[list[PowerTorqueValue]] = None
    fuel_type: Optional[list[str]] = None


class Fuel(BaseModel):
    """Fuel type and efficiency."""
    type: list[str]
    efficiency: Optional[dict[str, Any]] = None


class Dimensions(BaseModel):
    """Physical dimensions of the bike."""
    width: Optional[DimensionValue] = None
    height: Optional[DimensionValue] = None
    weight: Optional[dict[str, int]] = None
    seat_height: Optional[DimensionValue] = None # Specific to bikes
    ground_clearance: Optional[DimensionValue] = None


class Price(BaseModel):
    """Price information."""
    value: int
    currency: str
    availability: Optional[str] = None
    valid_until: Optional[str] = None
    url: Optional[str] = None


class Brand(BaseModel):
    """Brand information."""
    name: str
    image: Optional[ImageReference] = None


class Rating(BaseModel):
    """Expert rating."""
    value: Optional[float] = None
    worst: Optional[int] = None
    best: Optional[int] = None


class ReviewedBy(BaseModel):
    """Reviewer information."""
    name: str
    job_title: Optional[str] = None
    url: Optional[str] = None


class MileageDetail(BaseModel):
    """Detailed mileage information."""
    fuel_type: str
    transmission: str
    mileage: str
    city_mileage: Optional[str] = None
    highway_mileage: Optional[str] = None


class CompetitorBike(BaseModel):
    """Competitor bike information."""
    name: str
    price: str
    url: str


class ComparisonFeature(BaseModel):
    """Feature comparison across bikes."""
    feature: str
    values: list[str]


class CompetitorComparison(BaseModel):
    """Comparison with competitor bikes."""
    bikes: list[CompetitorBike]
    features: list[ComparisonFeature]


class BikeDetail(BaseModel):
    """Complete bike detail model with all information."""
    
    # Required fields
    id: str = Field(..., description="Unique bike identifier (lowercase with underscores)")
    basic_info: BasicInfo
    price: Price
    brand: Brand
    
    # Optional fields (extended details)
    engine: Optional[Engine] = None
    transmission: Optional[list[str]] = None
    fuel: Optional[Fuel] = None
    dimensions: Optional[Dimensions] = None
    colors: Optional[list[str]] = None
    rating: Optional[Rating] = None
    reviewed_by: Optional[ReviewedBy] = None
    pros: Optional[list[str]] = None
    cons: Optional[list[str]] = None
    verdict: Optional[str] = None
    competitor_comparison: Optional[CompetitorComparison] = None
    mileage_details: Optional[list[MileageDetail]] = None
    whats_new: Optional[dict[str, list[str]]] = None
    features: Optional[list[str]] = None
    
    model_config = ConfigDict(validate_assignment=True, extra="ignore")
    
    def get_basic_only(self) -> "BikeDetail":
        """
        Return a copy with only basic fields populated.
        
        Returns:
            BikeDetail with extended fields set to None
        """
        return BikeDetail(
            id=self.id,
            basic_info=self.basic_info,
            price=self.price,
            brand=self.brand,
            # All optional fields are None by default
        )


class BikeComparison(BaseModel):
    """Comparison matrix between different bikes."""
    
    bikes: list[BikeDetail] = Field(..., description="List of bikes being compared")
    comparison_matrix: dict[str, list[Any]] = Field(
        ..., 
        description="Matrix of comparison features and values"
    )
    
    model_config = ConfigDict(validate_assignment=True)
