"""Demo script to test CarService with real data."""

from mahindrabot.services.car_service import CarService
from mahindrabot.services.serializers import (
    serialize_car_comparison,
    serialize_car_detail,
)

# Initialize service with real data
print("=" * 80)
print("🚗 CarService Demo with Real Data")
print("=" * 80)
print()

service = CarService("data/new_car_details/", fuzzy_threshold=70)
print()

# Test 1: Get basic car details
print("📋 Test 1: Get Basic Car Details")
print("-" * 80)
car = service.get_car_details("mahindra_xuv_3xo")
if car:
    print(serialize_car_detail(car))
print()

# Test 2: Get extended car details
print("📋 Test 2: Get Extended Car Details")
print("-" * 80)
car_extended = service.get_extended_car_details("mahindra_xuv_3xo")
if car_extended:
    print(serialize_car_detail(car_extended))
print()

# Test 3: List cars with filters
print("📋 Test 3: List Cars (SUVs under 15L)")
print("-" * 80)
cars = service.list_cars(
    limit=5,
    body_type="SUV",
    max_price=1500000
)
for i, car in enumerate(cars, 1):
    print(f"{i}. {car.basic_info.name} - {car.price.value:,} INR")
print()

# Test 4: Search functionality
print("📋 Test 4: Search for 'Mahindra' cars")
print("-" * 80)
results = service.search("Mahindra", limit=3)
for i, car in enumerate(results, 1):
    print(f"{i}. {car.basic_info.name} - {car.brand.name}")
print()

# Test 5: Compare cars
print("📋 Test 5: Compare Cars")
print("-" * 80)
comparison = service.get_car_comparison([
    "mahindra_xuv_3xo",
    "tata_punch_ev",
    "maruti_suzuki_brezza"
])
print(serialize_car_comparison(comparison))
print()

print("=" * 80)
print("✅ Demo Complete!")
print("=" * 80)
