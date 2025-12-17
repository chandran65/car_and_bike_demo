# Error Handling & Filter Improvements

## Overview

Enhanced CarService with intelligent error handling, filter validation with fuzzy matching suggestions, and improved filter parameters for better usability.

## Changes Implemented

### 1. **Exception Classes** ✅

Added two new custom exception classes:

#### `CarNotFoundError`
Raised when a car ID is not found, with fuzzy-matched suggestions:
```python
try:
    car = service.get_car_details("toyoto_camry")  # Typo
except CarNotFoundError as e:
    print(e)
    # Output:
    # Car 'toyoto_camry' not found.
    # Did you mean one of these?
    #   1. toyota_camry
    #   2. toyota_fortuner
    #   ...
```

#### `InvalidFilterError`
Raised when an invalid filter value is provided, with suggestions:
```python
try:
    cars = service.list_cars(limit=10, brand="Toyoto")  # Typo
except InvalidFilterError as e:
    print(e)
    # Output:
    # Invalid brand: 'Toyoto'
    # Did you mean one of these?
    #   1. Toyota
```

### 2. **Filter Value Tracking** ✅

During initialization, CarService now tracks unique values for validation:
- `available_brands` - Set of all brand names
- `available_body_types` - Set of all body types  
- `available_fuel_types` - Set of all fuel types
- `available_transmissions` - Set of all transmission types

**Console Output:**
```
Loaded 262 cars successfully
Available brands: 39
Available body types: 8
Available fuel types: 5
Available transmissions: 8
```

### 3. **Automatic Filter Validation** ✅

The following filters now validate input and suggest corrections:
- `brand` - Exact match required, case-insensitive
- `body_type` - Exact match required, case-insensitive
- `fuel_type` - Exact match required, case-insensitive
- `transmission` - Exact match required, case-insensitive

**Example Error Messages:**
```python
# Invalid brand
InvalidFilterError: Invalid brand: 'Toyoto'
Did you mean one of these?
  1. Toyota

# Invalid fuel type
InvalidFilterError: Invalid fuel_type: 'Hibrid'
Did you mean one of these?
  1. Hybrid

# Invalid transmission
InvalidFilterError: Invalid transmission: 'Manal'
Did you mean one of these?
  1. Manual
```

### 4. **Improved Range Filters** ✅

Replaced single-value filters with more flexible range filters:

#### **Before:**
```python
# Old API - single threshold
cars = service.list_cars(
    limit=10,
    engine_displacement=1500,  # Exact match only
    mileage="20"  # Minimum only
)
```

#### **After:**
```python
# New API - flexible ranges
cars = service.list_cars(
    limit=10,
    engine_displacement_more_than=1500,  # > 1500cc
    engine_displacement_less_than=2000,  # < 2000cc
    mileage_more_than=20.0,  # > 20 km/l
    mileage_less_than=30.0   # < 30 km/l
)
```

### 5. **Enhanced Methods** ✅

#### `get_car_details(car_id)` & `get_extended_car_details(car_id)`
- **Before**: Returned `None` if not found
- **After**: Raises `CarNotFoundError` with suggestions

#### `list_cars(...)` & `search(...)`
- **Before**: Silently ignored invalid filter values
- **After**: Raises `InvalidFilterError` with suggestions
- **New Parameters**:
  - `engine_displacement_more_than` (replaced `engine_displacement`)
  - `engine_displacement_less_than` (new)
  - `mileage_more_than` (replaced `mileage`)
  - `mileage_less_than` (new)

#### `get_car_comparison(car_ids)`
- **Before**: Skipped invalid car IDs silently
- **After**: Raises `CarNotFoundError` for any invalid ID

## Usage Examples

### Example 1: Handling Car Not Found
```python
from src.mahindrabot.services import CarService, CarNotFoundError

service = CarService("data/new_car_details/")

try:
    car = service.get_car_details("nonexistent_id")
except CarNotFoundError as e:
    print(f"Error: {e}")
    # Shows suggestions for similar car IDs
```

### Example 2: Handling Invalid Filters
```python
from src.mahindrabot.services import CarService, InvalidFilterError

service = CarService("data/new_car_details/")

try:
    cars = service.list_cars(
        limit=10,
        brand="Toyoto",  # Typo
        fuel_type="Hibrid"  # Typo
    )
except InvalidFilterError as e:
    print(f"Invalid filter: {e}")
    # Shows suggestions for correct values
```

### Example 3: Using New Range Filters
```python
# Find cars with displacement between 1500-2000cc
cars = service.list_cars(
    limit=10,
    engine_displacement_more_than=1500,
    engine_displacement_less_than=2000
)

# Find cars with mileage between 15-25 km/l
cars = service.list_cars(
    limit=10,
    mileage_more_than=15.0,
    mileage_less_than=25.0
)

# Combine multiple range filters
cars = service.list_cars(
    limit=10,
    min_price=500000,
    max_price=1000000,
    engine_displacement_more_than=1200,
    mileage_more_than=18.0,
    brand="Maruti Suzuki"  # Validated!
)
```

### Example 4: Safe Comparison
```python
try:
    comparison = service.get_car_comparison([
        "mahindra_xuv_3xo",
        "tata_punch_ev",
        "invalid_car_id"  # Will raise error
    ])
except CarNotFoundError as e:
    print(f"Cannot compare: {e}")
```

## API Changes Summary

### Modified Methods

| Method | Old Return | New Return | New Exceptions |
|--------|-----------|------------|----------------|
| `get_car_details()` | `Optional[CarDetail]` | `CarDetail` | `CarNotFoundError` |
| `get_extended_car_details()` | `Optional[CarDetail]` | `CarDetail` | `CarNotFoundError` |
| `list_cars()` | `list[CarDetail]` | `list[CarDetail]` | `InvalidFilterError` |
| `search()` | `list[CarDetail]` | `list[CarDetail]` | `InvalidFilterError` |
| `get_car_comparison()` | `CarComparison` | `CarComparison` | `CarNotFoundError` |

### Deprecated Parameters

| Old Parameter | New Parameters | Notes |
|--------------|---------------|-------|
| `engine_displacement` | `engine_displacement_more_than`, `engine_displacement_less_than` | More flexible range filtering |
| `mileage` | `mileage_more_than`, `mileage_less_than` | Supports both min and max |

## Benefits

1. **Better UX** - Clear error messages with actionable suggestions
2. **Faster Debugging** - Immediately know what went wrong
3. **Typo-Tolerant** - Fuzzy matching helps users find correct values
4. **Type-Safe** - Proper exception handling instead of None checks
5. **More Flexible** - Range filters for numeric values
6. **Self-Documenting** - Available filter values tracked and displayed

## Backward Compatibility

⚠️ **Breaking Changes:**

1. Methods now raise exceptions instead of returning `None`
2. Filter parameters renamed for engine displacement and mileage

**Migration Guide:**

```python
# Old code
car = service.get_car_details("car_id")
if car is None:
    print("Car not found")

# New code
try:
    car = service.get_car_details("car_id")
except CarNotFoundError as e:
    print(f"Car not found: {e}")

# Old filter parameters
cars = service.list_cars(
    limit=10,
    engine_displacement=1500,
    mileage="20"
)

# New filter parameters
cars = service.list_cars(
    limit=10,
    engine_displacement_more_than=1500,
    mileage_more_than=20.0
)
```

## Testing

✅ **All 141 tests passing**
- Added tests for `CarNotFoundError`
- Added tests for `InvalidFilterError`
- Added tests for new range filters
- Updated existing tests for new API

## Files Modified

1. `src/mahindrabot/services/car_service.py` - Core service with error handling
2. `src/mahindrabot/services/__init__.py` - Export new exception classes
3. `tests/test_car_service.py` - Updated tests
4. `demo_errors.py` - New demo showcasing error handling

## Demo Output

Run `python demo_errors.py` to see the new error handling in action:

```
✅ Caught CarNotFoundError:
Car 'nonexistent_car_id' not found.
Did you mean one of these?
  1. kia_carens
  2. citroen_c3
  ...

✅ Caught InvalidFilterError:
Invalid brand: 'Toyoto'
Did you mean one of these?
  1. Toyota
```

## Future Enhancements

Potential improvements:
1. Add threshold parameter for fuzzy matching sensitivity
2. Support partial matches for filter values
3. Add `get_available_filter_values()` method
4. Cache filter validation for performance
5. Add multi-language support for error messages
