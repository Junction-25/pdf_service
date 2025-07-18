from pydantic import BaseModel
from typing import List, Optional

class Location(BaseModel):
    lat: float
    lon: float

class PreferredLocation(Location):
    name: str

class Contact(BaseModel):
    id: int
    name: str
    preferred_locations: List[PreferredLocation]
    min_budget: float
    max_budget: float
    min_area_sqm: int
    max_area_sqm: int
    property_types: List[str]
    min_rooms: int

class Property(BaseModel):
    id: int
    address: str
    location: Location
    price: float
    area_sqm: int
    property_type: str
    number_of_rooms: int
    description: Optional[str] = None