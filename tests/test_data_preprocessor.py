"""Tests for data preprocessing functions."""

import pytest
from src.mahindrabot.services.data_preprocessor import (
    parse_price,
    parse_engine_displacement,
    parse_mileage,
    parse_seating_capacity,
    parse_rating,
    parse_dimension,
    parse_weight,
    parse_power_torque,
    parse_multi_value_field,
    normalize_fuel_type,
    parse_number_of_doors,
    generate_image_url_id,
    process_image_urls,
    preprocess_car_data,
)


class TestParsePrice:
    def test_parse_price_int(self):
        assert parse_price(43797297) == 43797297
    
    def test_parse_price_string(self):
        assert parse_price("43797297") == 43797297
        assert parse_price("728300") == 728300
    
    def test_parse_price_none(self):
        assert parse_price(None) is None
    
    def test_parse_price_with_symbols(self):
        assert parse_price("₹43,797,297") == 43797297
        assert parse_price("Rs. 728300") == 728300


class TestParseEngineDisplacement:
    def test_single_displacement(self):
        result = parse_engine_displacement("3982 cc")
        assert result == [{"value": 3982, "unit": "cc"}]
    
    def test_multiple_displacements(self):
        result = parse_engine_displacement("1197,1497 cc")
        assert result == [
            {"value": 1197, "unit": "cc"},
            {"value": 1497, "unit": "cc"}
        ]
    
    def test_uppercase_unit(self):
        result = parse_engine_displacement("3982 CC")
        assert result == [{"value": 3982, "unit": "CC"}]
    
    def test_na_value(self):
        assert parse_engine_displacement("N/A") == []
        assert parse_engine_displacement(None) == []
    
    def test_no_unit(self):
        result = parse_engine_displacement("1462")
        assert len(result) == 1
        assert result[0]["value"] == 1462


class TestParseMileage:
    def test_simple_fuel_mileage(self):
        result = parse_mileage("12 KM/L")
        assert result == {"value": 12.0, "unit": "km/l", "type": "fuel"}
    
    def test_range_fuel_mileage(self):
        result = parse_mileage("19 - 25 KM/L")
        assert result == {"min": 19.0, "max": 25.0, "unit": "km/l", "type": "fuel"}
    
    def test_electric_range(self):
        result = parse_mileage("265 Km/Full Charge")
        assert result == {"value": 265.0, "unit": "km", "type": "electric"}
    
    def test_electric_range_multiple(self):
        result = parse_mileage("265,365 Km/Full Charge")
        assert result == {"min": 265.0, "max": 365.0, "unit": "km", "type": "electric"}
    
    def test_decimal_mileage(self):
        result = parse_mileage("12.8 KM/L")
        assert result == {"value": 12.8, "unit": "km/l", "type": "fuel"}
    
    def test_none_value(self):
        assert parse_mileage(None) == {}


class TestParseSeatingCapacity:
    def test_simple_number(self):
        assert parse_seating_capacity("5") == 5
    
    def test_with_text(self):
        assert parse_seating_capacity("5 Seater") == 5
    
    def test_int_value(self):
        assert parse_seating_capacity(5) == 5
    
    def test_none(self):
        assert parse_seating_capacity(None) is None


class TestParseRating:
    def test_string_float(self):
        assert parse_rating("7.5") == 7.5
    
    def test_int(self):
        assert parse_rating(7) == 7.0
    
    def test_dash(self):
        assert parse_rating("-") is None
    
    def test_none(self):
        assert parse_rating(None) is None
    
    def test_float(self):
        assert parse_rating(8.1) == 8.1


class TestParseDimension:
    def test_mm_with_space(self):
        result = parse_dimension("1700 mm ")
        assert result == {"value": 1700.0, "unit": "mm"}
    
    def test_mm_no_space(self):
        result = parse_dimension("1700mm")
        assert result == {"value": 1700.0, "unit": "mm"}
    
    def test_inches(self):
        result = parse_dimension("67.2 inches")
        assert result == {"value": 67.2, "unit": "inches"}
    
    def test_no_unit(self):
        result = parse_dimension("1700")
        assert result == {"value": 1700.0, "unit": "mm"}
    
    def test_none(self):
        assert parse_dimension(None) is None


class TestParseWeight:
    def test_dual_weight(self):
        result = parse_weight("1788/1788")
        assert result == {"kerb_weight": 1788, "gross_weight": 1788}
    
    def test_different_weights(self):
        result = parse_weight("1500/1600")
        assert result == {"kerb_weight": 1500, "gross_weight": 1600}
    
    def test_single_weight(self):
        result = parse_weight("1500")
        assert result == {"kerb_weight": 1500, "gross_weight": 1500}
    
    def test_none(self):
        assert parse_weight(None) == {}


class TestParsePowerTorque:
    def test_simple_power(self):
        result = parse_power_torque("680 bhp")
        assert len(result) == 1
        assert result[0]["value"] == 680
        assert result[0]["unit"] == "bhp"
    
    def test_multiple_values(self):
        result = parse_power_torque("109bhp @5000 rpm,110bhp @5000 rpm")
        assert len(result) == 2
        assert result[0]["value"] == 109
        assert result[0]["unit"] == "bhp"
        assert "rpm" in result[0]["rpm"].lower()
    
    def test_torque(self):
        result = parse_power_torque("700 Nm")
        assert len(result) == 1
        assert result[0]["value"] == 700
        assert result[0]["unit"] == "nm"
    
    def test_none(self):
        assert parse_power_torque(None) == []


class TestParseMultiValueField:
    def test_comma_separated(self):
        result = parse_multi_value_field("Petrol, Diesel")
        assert result == ["Petrol", "Diesel"]
    
    def test_single_value(self):
        result = parse_multi_value_field("Manual")
        assert result == ["Manual"]
    
    def test_multiple_with_spaces(self):
        result = parse_multi_value_field("Manual, Automatic, AMT")
        assert result == ["Manual", "Automatic", "AMT"]
    
    def test_none(self):
        assert parse_multi_value_field(None) == []


class TestNormalizeFuelType:
    def test_plus_separator(self):
        result = normalize_fuel_type(["Petrol+CNG"])
        assert result == ["Petrol", "CNG"]
    
    def test_already_split(self):
        result = normalize_fuel_type(["Petrol", "Diesel"])
        assert result == ["Petrol", "Diesel"]
    
    def test_duplicates(self):
        result = normalize_fuel_type(["Petrol", "Petrol"])
        assert result == ["Petrol"]
    
    def test_slash_separator(self):
        result = normalize_fuel_type(["Petrol/CNG"])
        assert result == ["Petrol", "CNG"]


class TestParseNumberOfDoors:
    def test_string(self):
        assert parse_number_of_doors("5") == 5
    
    def test_int(self):
        assert parse_number_of_doors(5) == 5
    
    def test_none(self):
        assert parse_number_of_doors(None) is None


class TestGenerateImageUrlId:
    def test_main_image(self):
        result = generate_image_url_id("aston_martin_dbx", "main")
        assert result == "aston_martin_dbx_main"
    
    def test_brand_logo(self):
        result = generate_image_url_id("aston_martin_dbx", "brand_logo")
        assert result == "aston_martin_dbx_brand_logo"


class TestProcessImageUrls:
    def test_main_image_and_brand(self):
        raw_data = {
            "basic_info": {
                "name": "Aston Martin DBX",
                "image_url": "https://example.com/dbx.jpg"
            },
            "brand": {
                "name": "Aston Martin",
                "image": "https://example.com/brand.png"
            }
        }
        
        result = process_image_urls("aston_martin_dbx", raw_data)
        
        assert "basic_info.image_url" in result
        assert result["basic_info.image_url"]["url_id"] == "aston_martin_dbx_main"
        assert result["basic_info.image_url"]["alt_text"] == "Aston Martin DBX"
        
        assert "brand.image" in result
        assert result["brand.image"]["url_id"] == "aston_martin_dbx_brand_logo"
        assert result["brand.image"]["alt_text"] == "Aston Martin Logo"
    
    def test_no_images(self):
        raw_data = {"basic_info": {}, "brand": {}}
        result = process_image_urls("test_car", raw_data)
        assert result == {}


class TestPreprocessCarData:
    def test_full_preprocessing(self):
        raw_data = {
            "basic_info": {
                "name": "Test Car",
                "manufacturer": "Test Brand",
                "model": "Model X",
                "image_url": "https://example.com/car.jpg"
            },
            "engine": {
                "displacement": "1497 cc",
                "power": "100 bhp",
                "torque": "200 Nm",
                "fuel_type": "Petrol"
            },
            "transmission": "Manual, Automatic",
            "fuel": {
                "type": "Petrol",
                "efficiency": "18 KM/L"
            },
            "dimensions": {
                "width": "1800 mm",
                "height": "1600 mm",
                "weight": "1200/1300",
                "seating_capacity": "5",
                "number_of_doors": "4"
            },
            "price": {
                "value": "1000000",
                "currency": "INR"
            },
            "brand": {
                "name": "Test Brand",
                "image": "https://example.com/brand.png"
            },
            "rating": {
                "value": "7.5",
                "worst": 1,
                "best": 10
            }
        }
        
        result = preprocess_car_data(raw_data, "test_car")
        
        # Check id
        assert result["id"] == "test_car"
        
        # Check engine processing
        assert len(result["engine"]["displacement"]) == 1
        assert result["engine"]["displacement"][0]["value"] == 1497
        assert result["engine"]["fuel_type"] == ["Petrol"]
        
        # Check transmission
        assert result["transmission"] == ["Manual", "Automatic"]
        
        # Check dimensions
        assert result["dimensions"]["width"]["value"] == 1800.0
        assert result["dimensions"]["seating_capacity"] == 5
        assert result["dimensions"]["weight"]["kerb_weight"] == 1200
        
        # Check price
        assert result["price"]["value"] == 1000000
        
        # Check rating
        assert result["rating"]["value"] == 7.5
        
        # Check images
        assert "url_id" in result["basic_info"]["image_url"]
        assert result["basic_info"]["image_url"]["url_id"] == "test_car_main"
    
    def test_missing_optional_fields(self):
        raw_data = {
            "basic_info": {
                "name": "Minimal Car"
            },
            "price": {
                "value": 500000
            },
            "brand": {
                "name": "Brand"
            }
        }
        
        result = preprocess_car_data(raw_data, "minimal_car")
        
        assert result["id"] == "minimal_car"
        assert "engine" not in result
        assert "dimensions" not in result
