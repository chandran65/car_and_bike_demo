"""Tests for serialization functions."""

import pytest

from src.mahindrabot.models.car import (
    BasicInfo,
    Brand,
    CarComparison,
    CarDetail,
    Dimensions,
    DimensionValue,
    DisplacementValue,
    Engine,
    Fuel,
    ImageReference,
    Price,
    Rating,
)
from src.mahindrabot.services.serializers import (
    _format_displacement,
    _format_fuel_types,
    _format_mileage,
    _format_price,
    _format_rating,
    _format_transmission,
    serialize_car_comparison,
    serialize_car_detail,
)


class TestFormatPrice:
    def test_lakh_format(self):
        assert _format_price(1000000) == "₹10.00L"
        assert _format_price(728300) == "₹7.28L"
    
    def test_crore_format(self):
        assert _format_price(43797297) == "₹4.38Cr"
        assert _format_price(10000000) == "₹1.00Cr"
    
    def test_small_price(self):
        assert _format_price(50000) == "₹50000"


class TestFormatDisplacement:
    def test_single_displacement(self):
        car = CarDetail(
            id="test",
            basic_info=BasicInfo(name="Test", manufacturer="Test", model="Test", url="http://test.com"),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test"),
            engine=Engine(displacement=[DisplacementValue(value=1497, unit="cc")])
        )
        assert _format_displacement(car) == "1497cc"
    
    def test_multiple_displacements(self):
        car = CarDetail(
            id="test",
            basic_info=BasicInfo(name="Test", manufacturer="Test", model="Test", url="http://test.com"),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test"),
            engine=Engine(displacement=[
                DisplacementValue(value=1197, unit="cc"),
                DisplacementValue(value=1497, unit="cc")
            ])
        )
        assert _format_displacement(car) == "1197cc/1497cc"
    
    def test_no_displacement(self):
        car = CarDetail(
            id="test",
            basic_info=BasicInfo(name="Test", manufacturer="Test", model="Test", url="http://test.com"),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test")
        )
        result = _format_displacement(car)
        assert result == "N/A" or result is None  # Accept both for backwards compatibility


class TestFormatFuelTypes:
    def test_single_fuel_type(self):
        car = CarDetail(
            id="test",
            basic_info=BasicInfo(name="Test", manufacturer="Test", model="Test", url="http://test.com"),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test"),
            fuel=Fuel(type=["Petrol"])
        )
        assert _format_fuel_types(car) == "Petrol"
    
    def test_multiple_fuel_types(self):
        car = CarDetail(
            id="test",
            basic_info=BasicInfo(name="Test", manufacturer="Test", model="Test", url="http://test.com"),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test"),
            fuel=Fuel(type=["Petrol", "Diesel"])
        )
        assert _format_fuel_types(car) == "Petrol, Diesel"
    
    def test_electric_fuel_type(self):
        car = CarDetail(
            id="test",
            basic_info=BasicInfo(name="Test", manufacturer="Test", model="Test", url="http://test.com"),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test"),
            fuel=Fuel(type=["Electric"])
        )
        assert _format_fuel_types(car) == "Electric"


class TestFormatTransmission:
    def test_single_transmission(self):
        car = CarDetail(
            id="test",
            basic_info=BasicInfo(name="Test", manufacturer="Test", model="Test", url="http://test.com"),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test"),
            transmission=["Manual"]
        )
        assert _format_transmission(car) == "Manual"
    
    def test_multiple_transmissions(self):
        car = CarDetail(
            id="test",
            basic_info=BasicInfo(name="Test", manufacturer="Test", model="Test", url="http://test.com"),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test"),
            transmission=["Manual", "Automatic"]
        )
        assert _format_transmission(car) == "Manual, Automatic"


class TestFormatMileage:
    def test_single_value(self):
        car = CarDetail(
            id="test",
            basic_info=BasicInfo(name="Test", manufacturer="Test", model="Test", url="http://test.com"),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test"),
            fuel=Fuel(type=["Petrol"], efficiency={"value": 18.0, "unit": "km/l", "type": "fuel"})
        )
        assert _format_mileage(car) == "18.0 km/l"
    
    def test_range_value(self):
        car = CarDetail(
            id="test",
            basic_info=BasicInfo(name="Test", manufacturer="Test", model="Test", url="http://test.com"),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test"),
            fuel=Fuel(type=["Petrol"], efficiency={"min": 18.0, "max": 21.0, "unit": "km/l", "type": "fuel"})
        )
        assert _format_mileage(car) == "18.0-21.0 km/l"


class TestFormatRating:
    def test_with_rating(self):
        car = CarDetail(
            id="test",
            basic_info=BasicInfo(name="Test", manufacturer="Test", model="Test", url="http://test.com"),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test"),
            rating=Rating(value=7.5, worst=1, best=10)
        )
        assert _format_rating(car) == "7.5/10"
    
    def test_without_rating(self):
        car = CarDetail(
            id="test",
            basic_info=BasicInfo(name="Test", manufacturer="Test", model="Test", url="http://test.com"),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test")
        )
        assert _format_rating(car) is None


class TestSerializeCarDetail:
    def test_basic_serialization(self):
        car = CarDetail(
            id="test_car",
            basic_info=BasicInfo(
                name="Test Car",
                manufacturer="Test Brand",
                model="Model X",
                url="http://test.com",
                body_type="SUV"
            ),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test Brand"),
            engine=Engine(
                displacement=[DisplacementValue(value=1497, unit="cc")],
                fuel_type=["Petrol"]
            ),
            transmission=["Manual"],
            fuel=Fuel(
                type=["Petrol"],
                efficiency={"value": 18.0, "unit": "km/l", "type": "fuel"}
            ),
            dimensions=Dimensions(seating_capacity=5),
            rating=Rating(value=7.5, worst=1, best=10)
        )
        
        result = serialize_car_detail(car)
        
        assert "ID: test_car" in result
        assert "Test Car" in result
        assert "Body Type: SUV" in result
        assert "₹10.00L" in result
        assert "1497 cc" in result
        assert "5 seats" in result
        assert "7.5/10" in result
        assert "Fuel Type: Petrol" in result
        assert "Transmission: Manual" in result
    
    def test_serialization_with_images(self):
        img_ref = ImageReference(
            url="http://example.com/car.jpg",
            url_id="test_car_main",
            alt_text="Test Car"
        )
        
        car = CarDetail(
            id="test_car",
            basic_info=BasicInfo(
                name="Test Car",
                manufacturer="Test Brand",
                model="Model X",
                url="http://test.com",
                image_url=img_ref
            ),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test Brand"),
            dimensions=Dimensions(seating_capacity=5)
        )
        
        result = serialize_car_detail(car)
        
        assert "Image: [Test Car](test_car_main)" in result
    
    def test_serialization_with_extended_info(self):
        car = CarDetail(
            id="test_car",
            basic_info=BasicInfo(
                name="Test Car",
                manufacturer="Test Brand",
                model="Model X",
                url="http://test.com"
            ),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test Brand"),
            dimensions=Dimensions(seating_capacity=5),
            colors=["Red", "Blue", "White"],
            pros=["Good mileage", "Spacious", "Affordable"],
            cons=["Basic features", "No sunroof"]
        )
        
        result = serialize_car_detail(car)
        
        assert "AVAILABLE COLORS (3)" in result
        assert "Red" in result
        assert "Blue" in result
        assert "White" in result
        assert "✅ Pros:" in result
        assert "Good mileage" in result
        assert "❌ Cons:" in result
        assert "Basic features" in result
    
    def test_electric_car_serialization(self):
        car = CarDetail(
            id="test_ev",
            basic_info=BasicInfo(
                name="Test EV",
                manufacturer="Test Brand",
                model="EV Model",
                url="http://test.com"
            ),
            price=Price(value=1500000, currency="INR"),
            brand=Brand(name="Test Brand"),
            fuel=Fuel(
                type=["Electric"],
                efficiency={"value": 300.0, "unit": "km", "type": "electric"}
            ),
            transmission=["Automatic"],
            dimensions=Dimensions(seating_capacity=5)
        )
        
        result = serialize_car_detail(car)
        
        assert "Electric" in result
        assert "300.0 km range per charge" in result  # Should show range per charge


class TestSerializeCarComparison:
    def test_comparison_serialization(self):
        car1 = CarDetail(
            id="car1",
            basic_info=BasicInfo(
                name="Car 1",
                manufacturer="Brand A",
                model="Model 1",
                url="http://test.com"
            ),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Brand A"),
            dimensions=Dimensions(seating_capacity=5)
        )
        
        car2 = CarDetail(
            id="car2",
            basic_info=BasicInfo(
                name="Car 2",
                manufacturer="Brand B",
                model="Model 2",
                url="http://test.com"
            ),
            price=Price(value=1200000, currency="INR"),
            brand=Brand(name="Brand B"),
            dimensions=Dimensions(seating_capacity=7)
        )
        
        comparison = CarComparison(
            cars=[car1, car2],
            comparison_matrix={
                "Price (INR)": [1000000, 1200000],
                "Brand": ["Brand A", "Brand B"],
                "Seating Capacity": [5, 7]
            }
        )
        
        result = serialize_car_comparison(comparison)
        
        assert "COMPARISON: Car 1 vs Car 2" in result
        assert "Price (INR)" in result
        assert "₹10.00L" in result
        assert "₹12.00L" in result
        assert "Brand A" in result
        assert "Brand B" in result
    
    def test_comparison_with_images(self):
        img_ref1 = ImageReference(
            url="http://example.com/car1.jpg",
            url_id="car1_main",
            alt_text="Car 1"
        )
        
        img_ref2 = ImageReference(
            url="http://example.com/car2.jpg",
            url_id="car2_main",
            alt_text="Car 2"
        )
        
        car1 = CarDetail(
            id="car1",
            basic_info=BasicInfo(
                name="Car 1",
                manufacturer="Brand A",
                model="Model 1",
                url="http://test.com",
                image_url=img_ref1
            ),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Brand A"),
            dimensions=Dimensions(seating_capacity=5)
        )
        
        car2 = CarDetail(
            id="car2",
            basic_info=BasicInfo(
                name="Car 2",
                manufacturer="Brand B",
                model="Model 2",
                url="http://test.com",
                image_url=img_ref2
            ),
            price=Price(value=1200000, currency="INR"),
            brand=Brand(name="Brand B"),
            dimensions=Dimensions(seating_capacity=7)
        )
        
        comparison = CarComparison(
            cars=[car1, car2],
            comparison_matrix={
                "Price (INR)": [1000000, 1200000]
            }
        )
        
        result = serialize_car_comparison(comparison)
        
        assert "Images:" in result
        assert "[Car 1](car1_main)" in result
        assert "[Car 2](car2_main)" in result


class TestReadability:
    def test_human_readable_format(self):
        """Verify that serialization is human-readable and clear."""
        car = CarDetail(
            id="test_car",
            basic_info=BasicInfo(
                name="Test Car",
                manufacturer="Test Brand",
                model="Model X",
                url="http://test.com",
                body_type="SUV"
            ),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test Brand"),
            engine=Engine(
                displacement=[DisplacementValue(value=1497, unit="cc")],
                fuel_type=["Petrol"]
            ),
            transmission=["Manual", "Automatic"],
            fuel=Fuel(
                type=["Petrol"],
                efficiency={"value": 18.0, "unit": "km/l", "type": "fuel"}
            ),
            dimensions=Dimensions(seating_capacity=5),
            rating=Rating(value=7.5, worst=1, best=10)
        )
        
        result = serialize_car_detail(car)
        
        # Verify clear labels are used
        assert "Price:" in result
        assert "Fuel Type:" in result
        assert "Transmission:" in result
        assert "₹" in result  # Rupee symbol
        
        # Verify section headers
        assert "BASIC INFORMATION" in result
        assert "ENGINE & PERFORMANCE" in result
        assert "DIMENSIONS" in result
        
        # Verify readable format (no abbreviations like P/D)
        assert "Petrol" in result
        assert "Manual, Automatic" in result
