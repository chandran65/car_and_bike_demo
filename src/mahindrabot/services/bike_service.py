"""BikeService for managing and querying bike data."""

import json
from pathlib import Path
from typing import Optional

from thefuzz import fuzz, process

from mahindrabot.models.bike import BikeComparison, BikeDetail
# Reusing data preprocessor as the structure is expected to be similar
from .data_preprocessor import preprocess_car_data as preprocess_bike_data


class BikeNotFoundError(Exception):
    """Raised when a bike is not found."""
    pass


class InvalidBikeFilterError(Exception):
    """Raised when an invalid filter value is provided."""
    
    def __init__(self, filter_name: str, invalid_value: str, suggestions: list[str]):
        self.filter_name = filter_name
        self.invalid_value = invalid_value
        self.suggestions = suggestions
        
        message = f"Invalid {filter_name}: '{invalid_value}'\nDid you mean one of these?\n"
        for i, suggestion in enumerate(suggestions[:5], 1):
            message += f"  {i}. {suggestion}\n"
        
        super().__init__(message)


class BikeService:
    """Service for loading, filtering, searching, and comparing bike data."""
    
    def __init__(self, json_folder: str, fuzzy_threshold: int = 70):
        """
        Initialize BikeService by loading and preprocessing JSON files.
        
        Args:
            json_folder: Path to folder containing bike JSON files
            fuzzy_threshold: Minimum similarity score for fuzzy search (0-100)
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.bikes: dict[str, BikeDetail] = {}
        
        # Track unique values for filter validation
        self.available_brands: set[str] = set()
        self.available_body_types: set[str] = set()
        self.available_fuel_types: set[str] = set()
        
        self._load_bikes(json_folder)
    
    def _load_bikes(self, json_folder: str) -> None:
        """
        Load all bike JSON files from folder.
        
        Args:
            json_folder: Path to folder containing bike JSON files
        """
        folder_path = Path(json_folder)
        
        if not folder_path.exists():
            print(f"Warning: Bike JSON folder not found: {json_folder}. Bike features will work but return no results.")
            return
        
        json_files = list(folder_path.glob("*.json"))
        
        if not json_files:
            print(f"Warning: No JSON files found in: {json_folder}")
            return
        
        for json_file in json_files:
            # Generate bike_id from filename (lowercase with underscores)
            bike_id = json_file.stem.lower()
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                # Preprocess the data
                preprocessed = preprocess_bike_data(raw_data, bike_id)
                
                # Validate and create BikeDetail model
                bike = BikeDetail(**preprocessed)
                self.bikes[bike_id] = bike
                
                # Track unique filter values
                if bike.brand and bike.brand.name:
                    self.available_brands.add(bike.brand.name)
                
                if bike.basic_info.body_type:
                    self.available_body_types.add(bike.basic_info.body_type)
                
                # Collect fuel types
                if bike.fuel and bike.fuel.type:
                    self.available_fuel_types.update(bike.fuel.type)
                if bike.engine and bike.engine.fuel_type:
                    self.available_fuel_types.update(bike.engine.fuel_type)
                
            except Exception as e:
                print(f"Warning: Failed to load {json_file.name}: {e}")
                continue
        
        print(f"Loaded {len(self.bikes)} bikes successfully")
        print(f"Available brands: {len(self.available_brands)}")
        print(f"Available body types: {len(self.available_body_types)}")
        print(f"Available fuel types: {len(self.available_fuel_types)}")
    
    def get_bike_details(self, bike_id: str) -> BikeDetail:
        """Get basic bike details (without extended information)."""
        bike = self.bikes.get(bike_id.lower())
        if bike:
            return bike.get_basic_only()
        
        # Bike not found - suggest similar IDs
        available_ids = list(self.bikes.keys())
        if not available_ids:
             raise BikeNotFoundError(f"Bike '{bike_id}' not found. No bikes available in database.")

        suggestions = process.extract(bike_id.lower(), available_ids, limit=5)
        suggestion_list = [s[0] for s in suggestions]
        
        raise BikeNotFoundError(
            f"Bike '{bike_id}' not found.\n"
            f"Did you mean one of these?\n" + 
            "\n".join(f"  {i}. {s}" for i, s in enumerate(suggestion_list, 1))
        )
    
    def get_extended_bike_details(self, bike_id: str) -> BikeDetail:
        """Get full bike details including all extended information."""
        bike = self.bikes.get(bike_id.lower())
        if bike:
            return bike
        
        available_ids = list(self.bikes.keys())
        if not available_ids:
             raise BikeNotFoundError(f"Bike '{bike_id}' not found. No bikes available in database.")
             
        suggestions = process.extract(bike_id.lower(), available_ids, limit=5)
        suggestion_list = [s[0] for s in suggestions]
        
        raise BikeNotFoundError(
            f"Bike '{bike_id}' not found.\n"
            f"Did you mean one of these?\n" + 
            "\n".join(f"  {i}. {s}" for i, s in enumerate(suggestion_list, 1))
        )
    
    def get_bike_comparison(self, bike_ids: list[str]) -> BikeComparison:
        """Compare multiple bikes."""
        bikes = []
        for bike_id in bike_ids:
            bike = self.get_extended_bike_details(bike_id)
            bikes.append(bike)
        
        if not bikes:
            raise ValueError("No bikes provided for comparison")
        
        # Build comparison matrix
        comparison_matrix = {}
        
        # Price
        comparison_matrix["Price (INR)"] = [bike.price.value for bike in bikes]
        
        # Brand
        comparison_matrix["Brand"] = [bike.brand.name for bike in bikes]
        
        # Body Type
        comparison_matrix["Body Type"] = [
            bike.basic_info.body_type if bike.basic_info.body_type else "N/A" 
            for bike in bikes
        ]
        
        # Engine Displacement
        comparison_matrix["Engine Displacement"] = []
        for bike in bikes:
            if bike.engine and bike.engine.displacement:
                disps = [f"{d.value}{d.unit}" for d in bike.engine.displacement]
                comparison_matrix["Engine Displacement"].append(", ".join(disps))
            else:
                comparison_matrix["Engine Displacement"].append("N/A")
        
        # Fuel Type
        comparison_matrix["Fuel Type"] = []
        for bike in bikes:
            if bike.fuel and bike.fuel.type:
                comparison_matrix["Fuel Type"].append(", ".join(bike.fuel.type))
            elif bike.engine and bike.engine.fuel_type:
                comparison_matrix["Fuel Type"].append(", ".join(bike.engine.fuel_type))
            else:
                comparison_matrix["Fuel Type"].append("N/A")
        
        # Mileage
        comparison_matrix["Mileage"] = []
        for bike in bikes:
            if bike.fuel and bike.fuel.efficiency:
                eff = bike.fuel.efficiency
                if "value" in eff:
                    comparison_matrix["Mileage"].append(f"{eff['value']} {eff.get('unit', '')}")
                elif "min" in eff and "max" in eff:
                    comparison_matrix["Mileage"].append(f"{eff['min']}-{eff['max']} {eff.get('unit', '')}")
                else:
                    comparison_matrix["Mileage"].append("N/A")
            else:
                comparison_matrix["Mileage"].append("N/A")
        
         # Rating
        comparison_matrix["Rating"] = []
        for bike in bikes:
            if bike.rating and bike.rating.value is not None:
                comparison_matrix["Rating"].append(f"{bike.rating.value}/10")
            else:
                comparison_matrix["Rating"].append("N/A")
        
        return BikeComparison(bikes=bikes, comparison_matrix=comparison_matrix)
    
    def _validate_filter_value(self, filter_name: str, value: str, available_values: set[str]) -> None:
        """Validate filter value and raise error with suggestions if invalid."""
        available_values_lower = {v.lower(): v for v in available_values}
        
        if value.lower() not in available_values_lower:
            suggestions = process.extract(value, list(available_values), limit=5)
            suggestion_list = [s[0] for s in suggestions if s[1] > 60]
            
            if not suggestion_list:
                suggestion_list = sorted(list(available_values))[:5]
            
            raise InvalidBikeFilterError(filter_name, value, suggestion_list)
    
    def _matches_filters(
        self,
        bike: BikeDetail,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        brand: Optional[str] = None,
        body_type: Optional[str] = None,
        fuel_type: Optional[str] = None,
        mileage_more_than: Optional[float] = None,
        mileage_less_than: Optional[float] = None,
        engine_displacement_more_than: Optional[int] = None,
        engine_displacement_less_than: Optional[int] = None,
    ) -> bool:
        """Check if bike matches all provided filters (AND logic)."""
        # Price filter
        if min_price is not None and bike.price.value < min_price:
            return False
        if max_price is not None and bike.price.value > max_price:
            return False
        
        # Brand filter
        if brand is not None:
            if not bike.brand.name or bike.brand.name.lower() != brand.lower():
                return False
        
        # Body type filter
        if body_type is not None:
            if not bike.basic_info.body_type or bike.basic_info.body_type.lower() != body_type.lower():
                return False
        
        # Fuel type filter
        if fuel_type is not None:
            fuel_types = []
            if bike.fuel and bike.fuel.type:
                fuel_types.extend([ft.lower() for ft in bike.fuel.type])
            if bike.engine and bike.engine.fuel_type:
                fuel_types.extend([ft.lower() for ft in bike.engine.fuel_type])
            
            if fuel_type.lower() not in fuel_types:
                return False
        
        # Engine displacement filters
        if engine_displacement_more_than is not None or engine_displacement_less_than is not None:
            if not bike.engine or not bike.engine.displacement:
                return False
            
            displacement_values = [d.value for d in bike.engine.displacement]
            max_displacement = max(displacement_values)
            min_displacement = min(displacement_values)
            
            if engine_displacement_more_than is not None:
                if max_displacement <= engine_displacement_more_than:
                    return False
            
            if engine_displacement_less_than is not None:
                if min_displacement >= engine_displacement_less_than:
                    return False
        
        # Mileage filters
        if mileage_more_than is not None or mileage_less_than is not None:
            if not bike.fuel or not bike.fuel.efficiency:
                return False
            
            eff = bike.fuel.efficiency
            bike_mileage = None
            
            if "value" in eff:
                bike_mileage = eff["value"]
            elif "max" in eff:
                bike_mileage = eff["max"]
            elif "min" in eff:
                bike_mileage = eff["min"]
            
            if bike_mileage is None:
                return False
            
            if mileage_more_than is not None and bike_mileage <= mileage_more_than:
                return False
            
            if mileage_less_than is not None and bike_mileage >= mileage_less_than:
                return False
        
        return True
    
    def _get_sort_value(self, bike: BikeDetail, sort_by: str) -> tuple:
        """Extract sort value from bike."""
        if sort_by == "price":
            return (True, bike.price.value)
        
        elif sort_by == "mileage":
            if not bike.fuel or not bike.fuel.efficiency:
                return (False, 0)
            
            eff = bike.fuel.efficiency
            if "value" in eff:
                return (True, eff["value"])
            elif "max" in eff:
                return (True, eff["max"])
            elif "min" in eff:
                return (True, eff["min"])
            return (False, 0)
        
        elif sort_by == "engine_displacement":
            if not bike.engine or not bike.engine.displacement:
                return (False, 0)
            displacement_values = [d.value for d in bike.engine.displacement]
            return (True, max(displacement_values))
        
        return (True, 0)
    
    def list_bikes(
        self,
        limit: int,
        offset: int = 0,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        brand: Optional[str] = None,
        body_type: Optional[str] = None,
        fuel_type: Optional[str] = None,
        mileage_more_than: Optional[float] = None,
        mileage_less_than: Optional[float] = None,
        engine_displacement_more_than: Optional[int] = None,
        engine_displacement_less_than: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> list[BikeDetail]:
        """List bikes with optional filters and pagination."""
        # Validate filter values
        if brand is not None:
            self._validate_filter_value("brand", brand, self.available_brands)
        
        if body_type is not None:
            self._validate_filter_value("body_type", body_type, self.available_body_types)
        
        if fuel_type is not None:
            self._validate_filter_value("fuel_type", fuel_type, self.available_fuel_types)
        
        # Validate sort
        valid_sort_fields = ["price", "mileage", "engine_displacement"]
        if sort_by is not None and sort_by not in valid_sort_fields:
            raise ValueError(f"Invalid sort_by: '{sort_by}'. Must be one of: {', '.join(valid_sort_fields)}")
        
        if sort_order not in ["asc", "desc"]:
            raise ValueError(f"Invalid sort_order: '{sort_order}'. Must be 'asc' or 'desc'")
        
        filtered_bikes = []
        for bike in self.bikes.values():
            if self._matches_filters(
                bike,
                min_price=min_price,
                max_price=max_price,
                brand=brand,
                body_type=body_type,
                fuel_type=fuel_type,
                mileage_more_than=mileage_more_than,
                mileage_less_than=mileage_less_than,
                engine_displacement_more_than=engine_displacement_more_than,
                engine_displacement_less_than=engine_displacement_less_than,
            ):
                filtered_bikes.append(bike)
        
        # Sort
        if sort_by:
            filtered_bikes.sort(
                key=lambda c: self._get_sort_value(c, sort_by),
                reverse=(sort_order == "desc")
            )
        else:
            filtered_bikes.sort(key=lambda c: c.price.value)
        
        paginated = filtered_bikes[offset:offset + limit]
        return [bike.get_basic_only() for bike in paginated]
    
    def search(
        self,
        query: str,
        limit: int,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        brand: Optional[str] = None,
        body_type: Optional[str] = None,
        fuel_type: Optional[str] = None,
        mileage_more_than: Optional[float] = None,
        mileage_less_than: Optional[float] = None,
        engine_displacement_more_than: Optional[int] = None,
        engine_displacement_less_than: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ) -> list[BikeDetail]:
        """Search bikes by query string with optional filters."""
        # Validate filters matches list_bikes
        if brand is not None:
            self._validate_filter_value("brand", brand, self.available_brands)
        if body_type is not None:
            self._validate_filter_value("body_type", body_type, self.available_body_types)
        if fuel_type is not None:
            self._validate_filter_value("fuel_type", fuel_type, self.available_fuel_types)
        
        if sort_by is not None and sort_by not in ["price", "mileage", "engine_displacement"]:
             raise ValueError(f"Invalid sort_by: {sort_by}")

        query_lower = query.lower()
        matching_bikes = []
        
        # Direct string search
        for bike in self.bikes.values():
            manufacturer_match = (bike.basic_info.manufacturer and 
                                query_lower in bike.basic_info.manufacturer.lower())
            
            if (query_lower in bike.basic_info.name.lower() or
                manufacturer_match or
                query_lower in bike.basic_info.model.lower()):
                
                if self._matches_filters(
                    bike,
                    min_price=min_price,
                    max_price=max_price,
                    brand=brand,
                    body_type=body_type,
                    fuel_type=fuel_type,
                    mileage_more_than=mileage_more_than,
                    mileage_less_than=mileage_less_than,
                    engine_displacement_more_than=engine_displacement_more_than,
                    engine_displacement_less_than=engine_displacement_less_than,
                ):
                    matching_bikes.append((bike, 100))
        
        # Fuzzy search
        if not matching_bikes:
            for bike in self.bikes.values():
                score = fuzz.partial_ratio(query_lower, bike.basic_info.name.lower())
                
                if score >= self.fuzzy_threshold:
                    if self._matches_filters(
                        bike,
                        min_price=min_price,
                        max_price=max_price,
                        brand=brand,
                        body_type=body_type,
                        fuel_type=fuel_type,
                        mileage_more_than=mileage_more_than,
                        mileage_less_than=mileage_less_than,
                        engine_displacement_more_than=engine_displacement_more_than,
                        engine_displacement_less_than=engine_displacement_less_than,
                    ):
                        matching_bikes.append((bike, score))
        
        # Sort
        if sort_by:
            matching_bikes.sort(
                key=lambda x: (
                    self._get_sort_value(x[0], sort_by)[0],
                    self._get_sort_value(x[0], sort_by)[1] if sort_order == "asc" else -self._get_sort_value(x[0], sort_by)[1],
                    -x[1]
                )
            )
        else:
            matching_bikes.sort(key=lambda x: (-x[1], x[0].price.value))
        
        results = [bike for bike, score in matching_bikes[:limit]]
        return [bike.get_basic_only() for bike in results]
