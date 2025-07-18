import json
import random
import numpy as np
from faker import Faker

# --- CONFIGURATION ---
NUM_PROPERTIES = 1000
NUM_CONTACTS = 10000
OUTPUT_PROPERTIES_FILE = "properties.json"
OUTPUT_CONTACTS_FILE = "contacts.json"

# Define Geographic Hotspots with center coordinates and a location multiplier for price
# Higher multiplier = more expensive area
GEOGRAPHIC_ZONES = {
    "Hydra (High-End)":       {"lat": 36.75, "lon": 3.04, "price_multiplier": 1.8},
    "Algiers-Center (Urban)": {"lat": 36.77, "lon": 3.06, "price_multiplier": 1.5},
    "Oran (Coastal City)":    {"lat": 35.69, "lon": -0.63, "price_multiplier": 1.1},
    "Constantine (Historic)": {"lat": 36.36, "lon": 6.61, "price_multiplier": 1.0},
    "Bab Ezzouar (Business)": {"lat": 36.72, "lon": 3.18, "price_multiplier": 1.3},
}

# Define Property Archetypes
PROPERTY_TYPES = {
    "apartment": {"base_price": 12_000_000, "base_area": (60, 150)},
    "villa":     {"base_price": 45_000_000, "base_area": (200, 600)},
    "office":    {"base_price": 18_000_000, "base_area": (50, 350)},
    "land":      {"base_price": 25_000_000, "base_area": (300, 1000)},
}

# Initialize Faker for Algerian context if available, otherwise default
try:
    fake = Faker('fr_DZ')
except Exception:
    fake = Faker()

def generate_properties(num_properties):
    """Generates a list of realistic property dictionaries."""
    properties = []
    print(f"Generating {num_properties} properties...")
    for i in range(1, num_properties + 1):
        # 1. Pick a Zone and Type
        zone_name, zone_data = random.choice(list(GEOGRAPHIC_ZONES.items()))
        type_name, type_data = random.choice(list(PROPERTY_TYPES.items()))

        # 2. Calculate Realistic Price
        base_price = type_data["base_price"] * zone_data["price_multiplier"]
        # Use lognormal for a realistic price skew (more mid-range, fewer extremes)
        price = round(base_price * np.random.lognormal(0, 0.25), -4) # Round to nearest 10,000

        # 3. Calculate Realistic Area & Rooms
        min_area, max_area = type_data["base_area"]
        area_sqm = random.randint(min_area, max_area)

        if type_name == "land":
            number_of_rooms = 0
        else:
            # Correlate rooms with area
            number_of_rooms = max(1, int(area_sqm / (random.randint(35, 50))))

        # 4. Generate Geographic Coordinates
        lat = zone_data["lat"] + np.random.normal(0, 0.02)
        lon = zone_data["lon"] + np.random.normal(0, 0.02)

        # 5. Use Faker for Text
        address = f"{fake.street_address()}, {zone_name.split(' ')[0]}"

        properties.append({
            "id": i,
            "address": address,
            "location": {"lat": round(lat, 5), "lon": round(lon, 5)},
            "price": price,
            "area_sqm": area_sqm,
            "property_type": type_name,
            "number_of_rooms": number_of_rooms,
        })
    return properties

def generate_contacts(num_contacts, properties):
    """Generates a list of realistic contact dictionaries based on existing properties."""
    contacts = []
    print(f"Generating {num_contacts} contacts...")
    for i in range(1, num_contacts + 1):
        # 1. Use an "Inspiration Property" to create a realistic profile
        inspiration_property = random.choice(properties)

        # 2. Generate Desired Location(s)
        preferred_locations = []
        loc_lat = inspiration_property["location"]["lat"] + np.random.normal(0, 0.01)
        loc_lon = inspiration_property["location"]["lon"] + np.random.normal(0, 0.01)
        preferred_locations.append({
            "name": f"Around {inspiration_property['address'].split(',')[1].strip()}",
            "lat": round(loc_lat, 5),
            "lon": round(loc_lon, 5)
        })
        # 30% chance of having a second, different preferred location
        if random.random() < 0.3:
            second_inspiration = random.choice(properties)
            loc_lat_2 = second_inspiration["location"]["lat"] + np.random.normal(0, 0.01)
            loc_lon_2 = second_inspiration["location"]["lon"] + np.random.normal(0, 0.01)
            preferred_locations.append({
                "name": f"Around {second_inspiration['address'].split(',')[1].strip()}",
                "lat": round(loc_lat_2, 5),
                "lon": round(loc_lon_2, 5)
            })

        # 3. Generate Realistic Budget
        price = inspiration_property["price"]
        min_budget = round(price * np.random.uniform(0.75, 0.98), -4)
        max_budget = round(price * np.random.uniform(1.02, 1.40), -4)

        # 4. Generate Desired Area & Rooms
        area = inspiration_property["area_sqm"]
        min_area_sqm = int(area * np.random.uniform(0.8, 1.0))
        max_area_sqm = int(area * np.random.uniform(1.0, 1.5))
        min_rooms = max(0, inspiration_property["number_of_rooms"] - random.randint(1,2))

        # 5. Generate Desired Property Types
        property_types = [inspiration_property["property_type"]]
        # 25% chance of being interested in a second property type
        if random.random() < 0.25:
            other_type = random.choice(list(PROPERTY_TYPES.keys()))
            if other_type not in property_types:
                property_types.append(other_type)

        contacts.append({
            "id": i,
            "name": fake.name(),
            "preferred_locations": preferred_locations,
            "min_budget": min_budget,
            "max_budget": max_budget,
            "min_area_sqm": min_area_sqm,
            "max_area_sqm": max_area_sqm,
            "property_types": property_types,
            "min_rooms": min_rooms
        })
    return contacts


if __name__ == "__main__":
    print("Starting synthetic dataset generation...")

    # Generate properties first, as they inform the contacts
    properties_data = generate_properties(NUM_PROPERTIES)
    with open(OUTPUT_PROPERTIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(properties_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Successfully generated and saved {len(properties_data)} properties to {OUTPUT_PROPERTIES_FILE}")

    # Generate contacts based on the created properties
    contacts_data = generate_contacts(NUM_CONTACTS, properties_data)
    with open(OUTPUT_CONTACTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(contacts_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Successfully generated and saved {len(contacts_data)} contacts to {OUTPUT_CONTACTS_FILE}")

    print("\nDataset generation complete!")

