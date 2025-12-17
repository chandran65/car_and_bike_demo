"""Service for finding nearby EV charging stations."""

import json
import math
from pathlib import Path

import pandas as pd
import pgeocode

from mahindrabot.models.ev_location import Coordinates, EVLocationResult


class EVChargerLocationService:
    """
    Service for finding nearest EV charging stations by pincode.
    
    Uses pgeocode to convert pincodes to coordinates and haversine formula
    to calculate distances.
    """
    
    def __init__(self, json_file: str):
        """
        Initialize the service by loading EV locations data.
        
        Args:
            json_file: Path to JSON file containing EV charging locations
        """
        self.locations: list[dict] = []
        self.nominatim = pgeocode.Nominatim('in')
        
        self._load_locations(json_file)
    
    def _load_locations(self, json_file: str) -> None:
        """
        Load EV charging locations from JSON file.
        
        Args:
            json_file: Path to JSON file
        """
        file_path = Path(json_file)
        
        if not file_path.exists():
            raise ValueError(f"JSON file not found: {json_file}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            self.locations = json.load(f)
        
        print(f"Loaded {len(self.locations)} EV charging locations successfully")
    
    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points using haversine formula.
        
        Args:
            lat1: Latitude of first point
            lon1: Longitude of first point
            lat2: Latitude of second point
            lon2: Longitude of second point
            
        Returns:
            Distance in kilometers
        """
        R = 6371.0  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat/2)**2 + 
            math.cos(math.radians(lat1)) * 
            math.cos(math.radians(lat2)) * 
            math.sin(dlon/2)**2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    def find_nearest_ev_charger(
        self,
        pincode: str,
        radius_in_km: float = 5.0,
        limit: int = 5
    ) -> tuple[dict | None, list[EVLocationResult]]:
        """
        Find EV charging stations within specified radius, sorted by distance.
        
        Args:
            pincode: Indian postal code to search from
            radius_in_km: Maximum search radius in kilometers (default: 5.0)
            limit: Maximum number of results to return (default: 5)
            
        Returns:
            Tuple of (user_location_info, charger_results)
            - user_location_info: Dict with place details from pincode or None if invalid
            - charger_results: List of EVLocationResult objects sorted by distance (empty list if none found)
        """
        # Get coordinates from pincode
        location_info = self.nominatim.query_postal_code(pincode)
        
        # Check if pincode is valid (pgeocode returns pandas Series with NaN for invalid pincodes)
        if location_info is None or pd.isna(location_info.latitude) or pd.isna(location_info.longitude):
            return None, []
        
        # Extract user location information
        user_location = {
            'pincode': pincode,
            'place_name': location_info.place_name if not pd.isna(location_info.place_name) else 'Unknown',
            'city': location_info.place_name if not pd.isna(location_info.place_name) else 'Unknown',
            'state': location_info.state_name if not pd.isna(location_info.state_name) else 'Unknown',
            'latitude': float(location_info.latitude),
            'longitude': float(location_info.longitude)
        }
        
        search_lat = float(location_info.latitude)
        search_lon = float(location_info.longitude)
        
        # Find all locations within radius with their distances
        locations_with_distance = []
        
        for loc in self.locations:
            try:
                loc_lat = float(loc['latitude'])
                loc_lon = float(loc['longitude'])
                
                distance = self._haversine(search_lat, search_lon, loc_lat, loc_lon)
                
                if distance <= radius_in_km:
                    locations_with_distance.append((distance, loc))
                    
            except (ValueError, KeyError):
                # Skip locations with invalid coordinates
                continue
        
        # Sort by distance and apply limit
        locations_with_distance.sort(key=lambda x: x[0])
        locations_with_distance = locations_with_distance[:limit]
        
        # Convert to EVLocationResult objects
        results = []
        for distance, loc in locations_with_distance:
            # Generate Google Maps link
            google_maps_link = (
                f"https://www.google.com/maps/search/?api=1&"
                f"query={loc['latitude']},{loc['longitude']}"
            )
            
            # Create EVLocationResult (convert all fields to proper types to handle mixed data)
            # Handle cost_per_unit which can be empty string or numeric
            cost_per_unit = loc.get('cost_per_unit', 0)
            if isinstance(cost_per_unit, str):
                cost_per_unit = int(cost_per_unit) if cost_per_unit.strip() else 0
            
            # Handle contact_number which can be int or string
            contact_number = loc.get('contact_number', '')
            if contact_number is None:
                contact_number = ''
            
            result = EVLocationResult(
                id=str(loc['id']),
                name=str(loc.get('name', '')),
                address=str(loc['address']),
                city=str(loc['city']),
                postal_code=str(loc['postal_code']),
                country=str(loc['country']),
                latitude=str(loc['latitude']),
                longitude=str(loc['longitude']),
                coordinates=Coordinates(
                    latitude=str(loc['coordinates']['latitude']),
                    longitude=str(loc['coordinates']['longitude'])
                ),
                distance_km=distance,
                capacity=str(loc['capacity']),
                charger_type=str(loc['charger_type']),
                charging_type=str(loc['charging_type']),
                no_of_chargers=int(loc['no_of_chargers']),
                available=int(loc['available']),
                timing=str(loc['timing']),
                open=str(loc['open']),
                close=str(loc['close']),
                staff=str(loc['staff']),
                cost_per_unit=cost_per_unit,
                payment_modes=str(loc['payment_modes']),
                vendor=str(loc['vendor']),
                contact_number=str(contact_number),
                google_maps_link=google_maps_link
            )
            results.append(result)
        
        return user_location, results

