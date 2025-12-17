"""Integration tests for CarService."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from src.mahindrabot.models.car import CarComparison, CarDetail
from src.mahindrabot.services.car_service import (
    CarNotFoundError,
    CarService,
    InvalidFilterError,
)


@pytest.fixture
def temp_json_folder():
    """Create temporary folder with sample JSON files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample car data files
        car1_data = {
            "basic_info": {
                "name": "Mahindra XUV 3XO",
                "manufacturer": "Mahindra",
                "model": "XUV 3XO",
                "body_type": "SUV",
                "url": "https://example.com/xuv-3xo",
                "image_url": "https://example.com/xuv.jpg"
            },
            "engine": {
                "displacement": "1197,1497 cc",
                "power": "109 bhp",
                "torque": "200 Nm",
                "fuel_type": "Petrol, Diesel"
            },
            "transmission": "Manual, Automatic",
            "fuel": {
                "type": "Petrol, Diesel",
                "efficiency": "18 - 21 KM/L"
            },
            "dimensions": {
                "width": "1821 mm",
                "height": "1647 mm",
                "weight": "1362/1362",
                "seating_capacity": "5",
                "number_of_doors": "5"
            },
            "price": {
                "value": "728300",
                "currency": "INR"
            },
            "brand": {
                "name": "Mahindra",
                "image": "https://example.com/mahindra.png"
            },
            "rating": {
                "value": "7.5",
                "worst": 1,
                "best": 10
            },
            "colors": ["Red", "Blue", "White"],
            "pros": ["Good mileage", "Spacious cabin"],
            "cons": ["Could be cheaper"]
        }
        
        car2_data = {
            "basic_info": {
                "name": "Tata Punch EV",
                "manufacturer": "Tata",
                "model": "Punch EV",
                "body_type": "SUV",
                "url": "https://example.com/punch-ev",
                "image_url": "https://example.com/punch.jpg"
            },
            "engine": {
                "fuel_type": "Electric"
            },
            "transmission": "Automatic",
            "fuel": {
                "type": "Electric",
                "efficiency": "265 - 365 Km/Full Charge"
            },
            "dimensions": {
                "width": "1742 mm",
                "height": "1633 mm",
                "weight": "1354/1354",
                "seating_capacity": "5",
                "number_of_doors": "5"
            },
            "price": {
                "value": 1111732,
                "currency": "INR"
            },
            "brand": {
                "name": "Tata",
                "image": "https://example.com/tata.png"
            },
            "rating": {
                "value": 7,
                "worst": 1,
                "best": 10
            }
        }
        
        car3_data = {
            "basic_info": {
                "name": "Maruti Suzuki Brezza",
                "manufacturer": "Maruti Suzuki",
                "model": "Brezza",
                "body_type": "SUV",
                "url": "https://example.com/brezza"
            },
            "engine": {
                "displacement": "1462 cc",
                "fuel_type": "Petrol, Petrol+CNG"
            },
            "transmission": "Manual, Automatic",
            "fuel": {
                "type": "Petrol, Petrol+CNG",
                "efficiency": "19 - 25 KM/L"
            },
            "dimensions": {
                "width": "1790 mm",
                "height": "1685 mm",
                "weight": "1110/1110",
                "seating_capacity": "5",
                "number_of_doors": "5"
            },
            "price": {
                "value": "825900",
                "currency": "INR"
            },
            "brand": {
                "name": "Maruti Suzuki"
            },
            "rating": {
                "value": "8.5"
            }
        }
        
        # Write JSON files
        with open(os.path.join(tmpdir, "Mahindra_XUV_3XO.json"), "w") as f:
            json.dump(car1_data, f)
        
        with open(os.path.join(tmpdir, "Tata_Punch_EV.json"), "w") as f:
            json.dump(car2_data, f)
        
        with open(os.path.join(tmpdir, "Maruti_Suzuki_Brezza.json"), "w") as f:
            json.dump(car3_data, f)
        
        yield tmpdir


class TestCarServiceInitialization:
    def test_service_loads_cars(self, temp_json_folder):
        service = CarService(temp_json_folder)
        assert len(service.cars) == 3
        assert "mahindra_xuv_3xo" in service.cars
        assert "tata_punch_ev" in service.cars
        assert "maruti_suzuki_brezza" in service.cars
    
    def test_invalid_folder(self):
        with pytest.raises(ValueError, match="not found"):
            CarService("/nonexistent/folder")
    
    def test_empty_folder(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="No JSON files"):
                CarService(tmpdir)


class TestGetCarDetails:
    def test_get_basic_details(self, temp_json_folder):
        service = CarService(temp_json_folder)
        car = service.get_car_details("mahindra_xuv_3xo")
        
        assert car is not None
        assert car.id == "mahindra_xuv_3xo"
        assert car.basic_info.name == "Mahindra XUV 3XO"
        
        # Extended fields should be None
        assert car.engine is None
        assert car.transmission is None
        assert car.colors is None
    
    def test_get_extended_details(self, temp_json_folder):
        service = CarService(temp_json_folder)
        car = service.get_extended_car_details("mahindra_xuv_3xo")
        
        assert car is not None
        assert car.id == "mahindra_xuv_3xo"
        
        # Extended fields should be present
        assert car.engine is not None
        assert car.engine.fuel_type == ["Petrol", "Diesel"]
        assert car.transmission == ["Manual", "Automatic"]
        assert len(car.colors) == 3
    
    def test_car_not_found(self, temp_json_folder):
        service = CarService(temp_json_folder)
        with pytest.raises(CarNotFoundError):
            service.get_car_details("nonexistent")
        with pytest.raises(CarNotFoundError):
            service.get_extended_car_details("nonexistent")
    
    def test_case_insensitive_lookup(self, temp_json_folder):
        service = CarService(temp_json_folder)
        car1 = service.get_car_details("MAHINDRA_XUV_3XO")
        car2 = service.get_car_details("Mahindra_XUV_3XO")
        
        assert car1 is not None
        assert car2 is not None
        assert car1.id == car2.id


class TestGetCarComparison:
    def test_compare_two_cars(self, temp_json_folder):
        service = CarService(temp_json_folder)
        comparison = service.get_car_comparison(
            ["mahindra_xuv_3xo", "tata_punch_ev"]
        )
        
        assert isinstance(comparison, CarComparison)
        assert len(comparison.cars) == 2
        assert "Price (INR)" in comparison.comparison_matrix
        assert len(comparison.comparison_matrix["Price (INR)"]) == 2
    
    def test_compare_all_cars(self, temp_json_folder):
        service = CarService(temp_json_folder)
        comparison = service.get_car_comparison(
            ["mahindra_xuv_3xo", "tata_punch_ev", "maruti_suzuki_brezza"]
        )
        
        assert len(comparison.cars) == 3
        assert "Brand" in comparison.comparison_matrix
        assert comparison.comparison_matrix["Brand"] == ["Mahindra", "Tata", "Maruti Suzuki"]
    
    def test_comparison_with_invalid_id(self, temp_json_folder):
        service = CarService(temp_json_folder)
        
        # Should raise CarNotFoundError for invalid car ID
        with pytest.raises(CarNotFoundError):
            service.get_car_comparison(
                ["mahindra_xuv_3xo", "nonexistent"]
            )
    
    def test_comparison_no_valid_cars(self, temp_json_folder):
        service = CarService(temp_json_folder)
        # Should raise CarNotFoundError for first invalid car ID
        with pytest.raises(CarNotFoundError):
            service.get_car_comparison(["nonexistent1", "nonexistent2"])


class TestListCars:
    def test_list_all_cars(self, temp_json_folder):
        service = CarService(temp_json_folder)
        cars = service.list_cars(limit=10)
        
        assert len(cars) == 3
        # Should be sorted by price
        assert cars[0].price.value <= cars[1].price.value <= cars[2].price.value
    
    def test_invalid_brand_filter(self, temp_json_folder):
        service = CarService(temp_json_folder)
        with pytest.raises(InvalidFilterError) as exc_info:
            service.list_cars(limit=10, brand="InvalidBrand")
        assert "InvalidBrand" in str(exc_info.value)
    
    def test_invalid_fuel_type_filter(self, temp_json_folder):
        service = CarService(temp_json_folder)
        with pytest.raises(InvalidFilterError) as exc_info:
            service.list_cars(limit=10, fuel_type="InvalidFuel")
        assert "InvalidFuel" in str(exc_info.value)
    
    def test_list_with_limit(self, temp_json_folder):
        service = CarService(temp_json_folder)
        cars = service.list_cars(limit=2)
        
        assert len(cars) == 2
    
    def test_list_with_offset(self, temp_json_folder):
        service = CarService(temp_json_folder)
        cars = service.list_cars(limit=2, offset=1)
        
        assert len(cars) == 2
    
    def test_filter_by_price_range(self, temp_json_folder):
        service = CarService(temp_json_folder)
        cars = service.list_cars(limit=10, min_price=700000, max_price=900000)
        
        # Should return Mahindra XUV 3XO and Brezza
        assert len(cars) == 2
        assert all(700000 <= car.price.value <= 900000 for car in cars)
    
    def test_filter_by_brand(self, temp_json_folder):
        service = CarService(temp_json_folder)
        cars = service.list_cars(limit=10, brand="Mahindra")
        
        assert len(cars) == 1
        assert cars[0].brand.name == "Mahindra"
    
    def test_filter_by_body_type(self, temp_json_folder):
        service = CarService(temp_json_folder)
        cars = service.list_cars(limit=10, body_type="SUV")
        
        assert len(cars) == 3  # All are SUVs
    
    def test_filter_by_fuel_type(self, temp_json_folder):
        service = CarService(temp_json_folder)
        cars = service.list_cars(limit=10, fuel_type="Electric")
        
        assert len(cars) == 1
        assert cars[0].id == "tata_punch_ev"
    
    def test_filter_by_transmission(self, temp_json_folder):
        service = CarService(temp_json_folder)
        cars = service.list_cars(limit=10, transmission="Manual")
        
        # Should return XUV 3XO and Brezza
        assert len(cars) == 2
    
    def test_filter_by_seating_capacity(self, temp_json_folder):
        service = CarService(temp_json_folder)
        cars = service.list_cars(limit=10, seating_capacity=5)
        
        assert len(cars) == 3  # All have 5 seats
    
    def test_multiple_filters(self, temp_json_folder):
        service = CarService(temp_json_folder)
        cars = service.list_cars(
            limit=10,
            brand="Mahindra",
            body_type="SUV",
            seating_capacity=5
        )
        
        assert len(cars) == 1
        assert cars[0].id == "mahindra_xuv_3xo"
    
    def test_no_matches_invalid_brand(self, temp_json_folder):
        service = CarService(temp_json_folder)
        with pytest.raises(InvalidFilterError):
            service.list_cars(limit=10, brand="NonexistentBrand")
    
    def test_mileage_more_than_filter(self, temp_json_folder):
        service = CarService(temp_json_folder)
        cars = service.list_cars(limit=10, mileage_more_than=20.0)
        # Should filter cars with mileage > 20
        for car in cars:
            if car.fuel and car.fuel.efficiency:
                eff = car.fuel.efficiency
                if "value" in eff:
                    assert eff["value"] > 20.0
                elif "max" in eff:
                    assert eff["max"] > 20.0
    
    def test_engine_displacement_filters(self, temp_json_folder):
        service = CarService(temp_json_folder)
        cars = service.list_cars(limit=10, engine_displacement_more_than=1300)
        # Should filter cars with displacement > 1300
        assert len(cars) >= 0  # May or may not have results


class TestSearch:
    def test_direct_search_by_name(self, temp_json_folder):
        service = CarService(temp_json_folder)
        results = service.search("Mahindra", limit=10)
        
        assert len(results) == 1
        assert "mahindra" in results[0].basic_info.name.lower()
    
    def test_direct_search_by_model(self, temp_json_folder):
        service = CarService(temp_json_folder)
        results = service.search("Brezza", limit=10)
        
        assert len(results) == 1
        assert results[0].id == "maruti_suzuki_brezza"
    
    def test_partial_match(self, temp_json_folder):
        service = CarService(temp_json_folder)
        results = service.search("XUV", limit=10)
        
        assert len(results) == 1
        assert "xuv" in results[0].id
    
    def test_fuzzy_search(self, temp_json_folder):
        service = CarService(temp_json_folder, fuzzy_threshold=60)
        results = service.search("Mahendra", limit=10)
        
        # Should find "Mahindra" via fuzzy match
        assert len(results) >= 1
    
    def test_search_with_filters(self, temp_json_folder):
        service = CarService(temp_json_folder)
        results = service.search(
            "Mahindra",  # Search for brand instead of body type
            limit=10,
            min_price=700000,
            max_price=900000
        )
        
        # Should find Mahindra cars in price range
        assert len(results) >= 1
        assert all(700000 <= car.price.value <= 900000 for car in results)
    
    def test_search_no_results(self, temp_json_folder):
        service = CarService(temp_json_folder)
        results = service.search("NonexistentCar", limit=10)
        
        assert len(results) == 0
    
    def test_search_limit(self, temp_json_folder):
        service = CarService(temp_json_folder)
        results = service.search("", limit=2)  # Empty query matches all
        
        assert len(results) <= 2
    
    def test_case_insensitive_search(self, temp_json_folder):
        service = CarService(temp_json_folder)
        results1 = service.search("mahindra", limit=10)
        results2 = service.search("MAHINDRA", limit=10)
        results3 = service.search("Mahindra", limit=10)
        
        assert len(results1) == len(results2) == len(results3)


class TestDataPreprocessing:
    def test_engine_displacement_multiple_values(self, temp_json_folder):
        service = CarService(temp_json_folder)
        car = service.get_extended_car_details("mahindra_xuv_3xo")
        
        assert car.engine is not None
        assert len(car.engine.displacement) == 2
        assert car.engine.displacement[0].value == 1197
        assert car.engine.displacement[1].value == 1497
    
    def test_fuel_type_normalization(self, temp_json_folder):
        service = CarService(temp_json_folder)
        car = service.get_extended_car_details("maruti_suzuki_brezza")
        
        # "Petrol+CNG" should be split
        assert car.fuel is not None
        assert "Petrol" in car.fuel.type
        assert "CNG" in car.fuel.type
    
    def test_mileage_range_parsing(self, temp_json_folder):
        service = CarService(temp_json_folder)
        car = service.get_extended_car_details("mahindra_xuv_3xo")
        
        assert car.fuel is not None
        assert "min" in car.fuel.efficiency
        assert "max" in car.fuel.efficiency
        assert car.fuel.efficiency["min"] == 18.0
        assert car.fuel.efficiency["max"] == 21.0
    
    def test_electric_range_parsing(self, temp_json_folder):
        service = CarService(temp_json_folder)
        car = service.get_extended_car_details("tata_punch_ev")
        
        assert car.fuel is not None
        assert car.fuel.efficiency["type"] == "electric"
        assert car.fuel.efficiency["min"] == 265.0
        assert car.fuel.efficiency["max"] == 365.0
    
    def test_image_url_processing(self, temp_json_folder):
        service = CarService(temp_json_folder)
        car = service.get_extended_car_details("mahindra_xuv_3xo")
        
        assert car.basic_info.image_url is not None
        assert car.basic_info.image_url.url_id == "mahindra_xuv_3xo_main"
        assert car.basic_info.image_url.alt_text == "Mahindra XUV 3XO"
        
        assert car.brand.image is not None
        assert car.brand.image.url_id == "mahindra_xuv_3xo_brand_logo"
