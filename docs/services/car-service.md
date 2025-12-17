# CarService Implementation

## Overview

A comprehensive car data management service with preprocessing, filtering, searching, and comparison capabilities. Successfully loads and processes 260 cars from JSON files with automatic data cleaning and normalization.

## Features

### ✅ Data Preprocessing
- **Engine displacement**: Handles multiple values with units preserved (e.g., "1197,1497 cc" → `[{value: 1197, unit: "cc"}, {value: 1497, unit: "cc"}]`)
- **Price normalization**: Converts string/int to standardized integer format
- **Mileage parsing**: Supports fuel efficiency ranges and EV ranges
- **Dimension parsing**: Preserves units (mm, inches, etc.)
- **Fuel type normalization**: Splits combined types like "Petrol+CNG" → ["Petrol", "CNG"]
- **Image URL handling**: Assigns unique `url_id` to each image for markdown references

### ✅ Pydantic Models
- **CarDetail**: Main model with basic (required) and extended (optional) fields
- **CarComparison**: Structured comparison matrix between cars
- **Helper models**: ImageReference, DimensionValue, DisplacementValue, etc.
- **Type-safe**: Full validation with Pydantic v2

### ✅ CarService Methods

#### `__init__(json_folder, fuzzy_threshold=70)`
Loads and preprocesses all JSON files from specified folder.
- Successfully loaded: 260/262 cars
- Automatic preprocessing and validation
- Configurable fuzzy search threshold

#### `get_car_details(car_id) -> CarDetail | None`
Returns basic car information only (minimal fields).

#### `get_extended_car_details(car_id) -> CarDetail | None`
Returns complete car information with all extended fields.

#### `list_cars(limit, offset, **filters) -> list[CarDetail]`
List cars with pagination and multiple filters (AND logic):
- `min_price`, `max_price`: Price range filtering
- `brand`: Brand name (case-insensitive)
- `body_type`: Body type (case-insensitive)
- `fuel_type`: Fuel type (checks if exists in list)
- `transmission`: Transmission type (checks if exists in list)
- `seating_capacity`: Exact match
- `engine_displacement`: Matches any displacement value
- `mileage`: Minimum mileage threshold

#### `search(query, limit, **filters) -> list[CarDetail]`
Search cars by text query with fuzzy fallback:
1. **Direct search**: Case-insensitive substring match in name/manufacturer/model
2. **Fuzzy search**: Uses thefuzz library if no direct matches (configurable threshold)
3. Applies all filters with AND logic
4. Results sorted by relevance score then price

#### `get_car_comparison(car_ids) -> CarComparison`
Compare multiple cars with structured comparison matrix:
- Price, Brand, Body Type, Engine Displacement
- Fuel Type, Transmission, Mileage
- Seating Capacity, Rating

### ✅ Serialization Functions

#### `serialize_car_detail(car_detail) -> str`
Compact, token-optimized format for LLMs:
```
[mahindra_xuv_3xo] | Mahindra XUV 3XO | SUV | ₹7.28L | 1197cc/1497cc P/D | M/A/AMT | 18.0-21.0km/l | 5-seat | ★7.5/10
Img: [Mahindra XUV 3XO](mahindra_xuv_3xo_main)
Extended: 16 colors | Logo: [Mahindra Logo](mahindra_xuv_3xo_brand_logo)
```

Features:
- Abbreviations: P (Petrol), D (Diesel), EV (Electric), M (Manual), A (Automatic)
- Compact price format: ₹7.28L (Lakh), ₹4.38Cr (Crore)
- Markdown image references: `[alt_text](url_id)`
- Minimal tokens without losing information

#### `serialize_car_comparison(car_comparison) -> str`
Tabular comparison format with aligned columns and image references.

## Usage Example

```python
from src.mahindrabot.services.car_service import CarService
from src.mahindrabot.services.serializers import serialize_car_detail, serialize_car_comparison

# Initialize service
service = CarService("data/new_car_details/", fuzzy_threshold=70)

# Get basic details
car = service.get_car_details("mahindra_xuv_3xo")
print(serialize_car_detail(car))

# Get extended details
car_full = service.get_extended_car_details("mahindra_xuv_3xo")

# List cars with filters
cars = service.list_cars(
    limit=5,
    body_type="SUV",
    max_price=1500000,
    fuel_type="Petrol"
)

# Search functionality
results = service.search("Mahindra", limit=10)

# Compare cars
comparison = service.get_car_comparison([
    "mahindra_xuv_3xo",
    "tata_punch_ev",
    "maruti_suzuki_brezza"
])
print(serialize_car_comparison(comparison))
```

## Testing

### Test Coverage
- **137 tests** - All passing ✅
- **Unit tests**: Data preprocessor, Pydantic models, serializers
- **Integration tests**: CarService with mock and real data
- **Edge cases**: Missing fields, null values, multiple formats

### Run Tests
```bash
conda run -n scrape pytest tests/ -v
```

## Project Structure

```
src/mahindrabot/
├── models/
│   └── car.py                    # Pydantic models
├── services/
│   ├── data_preprocessor.py      # Data cleaning & normalization
│   ├── car_service.py            # Main service implementation
│   └── serializers.py            # Compact serialization

tests/
├── test_car_models.py            # Model validation tests
├── test_data_preprocessor.py     # Preprocessing tests
├── test_car_service.py           # Service integration tests
└── test_serializers.py           # Serialization tests
```

## Key Design Decisions

1. **Preprocessing at load time**: Clean once, use many times
2. **Type safety**: Pydantic ensures data integrity
3. **List handling**: Multiple engine displacements, fuel types, transmissions
4. **Unit preservation**: All measurements keep their units (mm, cc, etc.)
5. **Image URL structuring**: Unique `url_id` for markdown LLM references
6. **Case-insensitive**: All text filters and searches
7. **AND logic**: Multiple filters must all match
8. **Fuzzy search fallback**: Handles typos and variations
9. **Token optimization**: Compact serialization for LLM efficiency

## Performance

- **Load time**: ~1-2 seconds for 260 cars
- **Search time**: < 0.1 seconds (in-memory operations)
- **Memory usage**: Reasonable for 260 cars with full details
- **Test execution**: 137 tests in < 1 second

## Data Quality Handling

Successfully handles:
- Mixed data types (string "7.5" vs int 7)
- Multiple values in single field ("1197,1497 cc")
- Ranges ("18 - 21 KM/L")
- Missing optional fields
- Combined fuel types ("Petrol+CNG")
- Trailing spaces and formatting issues
- Electric vs fuel efficiency formats

## Future Enhancements

Potential improvements:
- Caching for frequently accessed cars
- Database backend for larger datasets
- API endpoints (FastAPI/Flask)
- More advanced search (synonyms, semantic search)
- Export to different formats (CSV, Excel)
- Variant-level details (currently car-level)

## Success Metrics

✅ **260/262 cars loaded** (99.2% success rate)  
✅ **137/137 tests passing** (100% pass rate)  
✅ **0 deprecation warnings**  
✅ **Full type safety** with Pydantic v2  
✅ **Comprehensive preprocessing** for real-world messy data  
✅ **Token-optimized serialization** for LLM efficiency
