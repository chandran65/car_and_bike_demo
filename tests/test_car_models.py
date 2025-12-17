"""Tests for Pydantic car models."""

import pytest
from pydantic import ValidationError
from src.mahindrabot.models.car import (
    ImageReference,
    DimensionValue,
    DisplacementValue,
    PowerTorqueValue,
    BasicInfo,
    Engine,
    Fuel,
    Dimensions,
    Price,
    Brand,
    Rating,
    CarDetail,
    CarComparison,
)


class TestImageReference:
    def test_valid_image_reference(self):
        img = ImageReference(
            url="https://example.com/car.jpg",
            url_id="test_car_main",
            alt_text="Test Car"
        )
        assert img.url_id == "test_car_main"
        assert img.alt_text == "Test Car"
    
    def test_missing_fields(self):
        with pytest.raises(ValidationError):
            ImageReference(url="https://example.com/car.jpg")


class TestDimensionValue:
    def test_valid_dimension(self):
        dim = DimensionValue(value=1700.0, unit="mm")
        assert dim.value == 1700.0
        assert dim.unit == "mm"
    
    def test_different_units(self):
        dim = DimensionValue(value=67.2, unit="inches")
        assert dim.value == 67.2
        assert dim.unit == "inches"


class TestDisplacementValue:
    def test_valid_displacement(self):
        disp = DisplacementValue(value=1497, unit="cc")
        assert disp.value == 1497
        assert disp.unit == "cc"
    
    def test_uppercase_unit(self):
        disp = DisplacementValue(value=3982, unit="CC")
        assert disp.unit == "CC"


class TestPowerTorqueValue:
    def test_without_rpm(self):
        power = PowerTorqueValue(value=680, unit="bhp")
        assert power.value == 680
        assert power.unit == "bhp"
        assert power.rpm is None
    
    def test_with_rpm(self):
        power = PowerTorqueValue(value=109, unit="bhp", rpm="5000 rpm")
        assert power.rpm == "5000 rpm"


class TestBasicInfo:
    def test_minimal_basic_info(self):
        basic = BasicInfo(
            name="Test Car",
            manufacturer="Test Brand",
            model="Model X",
            url="https://example.com/car"
        )
        assert basic.name == "Test Car"
        assert basic.body_type is None
    
    def test_with_image(self):
        img_ref = ImageReference(
            url="https://example.com/car.jpg",
            url_id="test_car_main",
            alt_text="Test Car"
        )
        basic = BasicInfo(
            name="Test Car",
            manufacturer="Test Brand",
            model="Model X",
            url="https://example.com/car",
            image_url=img_ref
        )
        assert basic.image_url.url_id == "test_car_main"


class TestEngine:
    def test_engine_with_displacement(self):
        engine = Engine(
            displacement=[
                DisplacementValue(value=1497, unit="cc"),
                DisplacementValue(value=1197, unit="cc")
            ],
            fuel_type=["Petrol", "Diesel"]
        )
        assert len(engine.displacement) == 2
        assert engine.fuel_type == ["Petrol", "Diesel"]
    
    def test_empty_engine(self):
        engine = Engine()
        assert engine.displacement is None
        assert engine.fuel_type is None


class TestFuel:
    def test_fuel_with_efficiency(self):
        fuel = Fuel(
            type=["Petrol"],
            efficiency={"value": 18.0, "unit": "km/l", "type": "fuel"}
        )
        assert fuel.type == ["Petrol"]
        assert fuel.efficiency["value"] == 18.0


class TestDimensions:
    def test_full_dimensions(self):
        dims = Dimensions(
            width=DimensionValue(value=1800.0, unit="mm"),
            height=DimensionValue(value=1600.0, unit="mm"),
            weight={"kerb_weight": 1200, "gross_weight": 1300},
            seating_capacity=5,
            number_of_doors=4
        )
        assert dims.seating_capacity == 5
        assert dims.weight["kerb_weight"] == 1200
    
    def test_minimal_dimensions(self):
        dims = Dimensions(seating_capacity=5)
        assert dims.seating_capacity == 5
        assert dims.width is None


class TestPrice:
    def test_valid_price(self):
        price = Price(value=1000000, currency="INR")
        assert price.value == 1000000
        assert price.currency == "INR"
    
    def test_with_optional_fields(self):
        price = Price(
            value=1000000,
            currency="INR",
            availability="InStock",
            valid_until="2026-03-31"
        )
        assert price.availability == "InStock"


class TestBrand:
    def test_brand_without_image(self):
        brand = Brand(name="Test Brand")
        assert brand.name == "Test Brand"
        assert brand.image is None
    
    def test_brand_with_image(self):
        img_ref = ImageReference(
            url="https://example.com/brand.png",
            url_id="test_brand_logo",
            alt_text="Test Brand Logo"
        )
        brand = Brand(name="Test Brand", image=img_ref)
        assert brand.image.url_id == "test_brand_logo"


class TestRating:
    def test_valid_rating(self):
        rating = Rating(value=7.5, worst=1, best=10)
        assert rating.value == 7.5
    
    def test_null_rating(self):
        rating = Rating(value=None)
        assert rating.value is None


class TestCarDetail:
    def test_minimal_car_detail(self):
        car = CarDetail(
            id="test_car",
            basic_info=BasicInfo(
                name="Test Car",
                manufacturer="Test Brand",
                model="Model X",
                url="https://example.com/car"
            ),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test Brand")
        )
        assert car.id == "test_car"
        assert car.engine is None
        assert car.transmission is None
    
    def test_full_car_detail(self):
        car = CarDetail(
            id="test_car",
            basic_info=BasicInfo(
                name="Test Car",
                manufacturer="Test Brand",
                model="Model X",
                url="https://example.com/car",
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
            dimensions=Dimensions(
                seating_capacity=5,
                number_of_doors=4
            ),
            colors=["Red", "Blue", "White"],
            rating=Rating(value=7.5, worst=1, best=10),
            pros=["Good mileage", "Spacious"],
            cons=["Expensive"]
        )
        assert car.id == "test_car"
        assert car.engine.fuel_type == ["Petrol"]
        assert car.transmission == ["Manual", "Automatic"]
        assert len(car.colors) == 3
    
    def test_get_basic_only(self):
        car = CarDetail(
            id="test_car",
            basic_info=BasicInfo(
                name="Test Car",
                manufacturer="Test Brand",
                model="Model X",
                url="https://example.com/car"
            ),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Test Brand"),
            engine=Engine(fuel_type=["Petrol"]),
            transmission=["Manual"],
            pros=["Good car"]
        )
        
        basic_car = car.get_basic_only()
        assert basic_car.id == "test_car"
        assert basic_car.basic_info.name == "Test Car"
        assert basic_car.engine is None
        assert basic_car.transmission is None
        assert basic_car.pros is None


class TestCarComparison:
    def test_car_comparison(self):
        car1 = CarDetail(
            id="car1",
            basic_info=BasicInfo(
                name="Car 1",
                manufacturer="Brand A",
                model="Model 1",
                url="https://example.com/car1"
            ),
            price=Price(value=1000000, currency="INR"),
            brand=Brand(name="Brand A")
        )
        
        car2 = CarDetail(
            id="car2",
            basic_info=BasicInfo(
                name="Car 2",
                manufacturer="Brand B",
                model="Model 2",
                url="https://example.com/car2"
            ),
            price=Price(value=1200000, currency="INR"),
            brand=Brand(name="Brand B")
        )
        
        comparison = CarComparison(
            cars=[car1, car2],
            comparison_matrix={
                "Price": [1000000, 1200000],
                "Manufacturer": ["Brand A", "Brand B"]
            }
        )
        
        assert len(comparison.cars) == 2
        assert "Price" in comparison.comparison_matrix
        assert comparison.comparison_matrix["Price"] == [1000000, 1200000]


class TestModelIntegration:
    def test_preprocessed_data_to_model(self):
        """Test that preprocessed data can be converted to model."""
        preprocessed = {
            "id": "test_car",
            "basic_info": {
                "name": "Test Car",
                "manufacturer": "Test Brand",
                "model": "Model X",
                "url": "https://example.com/car",
                "body_type": "SUV",
                "image_url": {
                    "url": "https://example.com/car.jpg",
                    "url_id": "test_car_main",
                    "alt_text": "Test Car"
                }
            },
            "engine": {
                "displacement": [{"value": 1497, "unit": "cc"}],
                "power": [{"value": 100.0, "unit": "bhp"}],
                "torque": [{"value": 200.0, "unit": "nm"}],
                "fuel_type": ["Petrol"]
            },
            "transmission": ["Manual", "Automatic"],
            "fuel": {
                "type": ["Petrol"],
                "efficiency": {"value": 18.0, "unit": "km/l", "type": "fuel"}
            },
            "dimensions": {
                "width": {"value": 1800.0, "unit": "mm"},
                "height": {"value": 1600.0, "unit": "mm"},
                "weight": {"kerb_weight": 1200, "gross_weight": 1300},
                "seating_capacity": 5,
                "number_of_doors": 4
            },
            "price": {
                "value": 1000000,
                "currency": "INR"
            },
            "brand": {
                "name": "Test Brand",
                "image": {
                    "url": "https://example.com/brand.png",
                    "url_id": "test_brand_logo",
                    "alt_text": "Test Brand Logo"
                }
            },
            "rating": {
                "value": 7.5,
                "worst": 1,
                "best": 10
            }
        }
        
        car = CarDetail(**preprocessed)
        assert car.id == "test_car"
        assert car.basic_info.image_url.url_id == "test_car_main"
        assert car.engine.displacement[0].value == 1497
        assert car.dimensions.width.value == 1800.0
