"""Demo script to test error handling with invalid inputs."""

from mahindrabot.services.car_service import (
    CarNotFoundError,
    CarService,
    InvalidFilterError,
)

print("=" * 80)
print("🚗 CarService Error Handling Demo")
print("=" * 80)
print()

service = CarService("data/new_car_details/", fuzzy_threshold=70)
print()

# Test 1: Invalid car ID
print("📋 Test 1: Get car details with invalid ID")
print("-" * 80)
try:
    car = service.get_car_details("nonexistent_car_id")
except CarNotFoundError as e:
    print(f"✅ Caught CarNotFoundError:")
    print(str(e))
print()

# Test 2: Invalid brand filter
print("📋 Test 2: List cars with invalid brand")
print("-" * 80)
try:
    cars = service.list_cars(
        limit=10,
        brand="Toyoto"  # Typo in Toyota
    )
except InvalidFilterError as e:
    print(f"✅ Caught InvalidFilterError:")
    print(str(e))
print()

# Test 3: Invalid body type filter
print("📋 Test 3: List cars with invalid body type")
print("-" * 80)
try:
    cars = service.list_cars(
        limit=10,
        body_type="Sedan"  # Maybe not available
    )
except InvalidFilterError as e:
    print(f"✅ Caught InvalidFilterError:")
    print(str(e))
print()

# Test 4: Invalid fuel type filter
print("📋 Test 4: Search with invalid fuel type")
print("-" * 80)
try:
    results = service.search(
        "car",
        limit=10,
        fuel_type="Hibrid"  # Typo in Hybrid
    )
except InvalidFilterError as e:
    print(f"✅ Caught InvalidFilterError:")
    print(str(e))
print()

# Test 5: Invalid transmission filter
print("📋 Test 5: List cars with invalid transmission")
print("-" * 80)
try:
    cars = service.list_cars(
        limit=10,
        transmission="Manal"  # Typo in Manual
    )
except InvalidFilterError as e:
    print(f"✅ Caught InvalidFilterError:")
    print(str(e))
print()

# Test 6: New filter parameters - engine displacement range
print("📋 Test 6: List cars with engine displacement > 1500cc")
print("-" * 80)
cars = service.list_cars(
    limit=5,
    engine_displacement_more_than=1500
)
for i, car in enumerate(cars, 1):
    print(f"{i}. {car.basic_info.name} - {car.price.value:,} INR")
print()

# Test 7: New filter parameters - mileage range
print("📋 Test 7: List cars with mileage > 20 km/l")
print("-" * 80)
cars = service.list_cars(
    limit=5,
    mileage_more_than=20.0
)
for i, car in enumerate(cars, 1):
    print(f"{i}. {car.basic_info.name} - {car.price.value:,} INR")
print()

print("=" * 80)
print("✅ Error Handling Demo Complete!")
print("=" * 80)
