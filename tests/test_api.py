import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Test the basic health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_health_check_detailed():
    """Test the detailed health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "llm_connection" in response.json()

def test_list_properties():
    """Test the properties listing endpoint."""
    response = client.get("/properties")
    assert response.status_code == 200
    assert "properties" in response.json()

def test_list_contacts():
    """Test the contacts listing endpoint."""
    response = client.get("/contacts")
    assert response.status_code == 200
    assert "contacts" in response.json()

def test_get_property_not_found():
    """Test getting a non-existent property."""
    response = client.get("/properties/999999")
    assert response.status_code == 404

def test_get_contact_not_found():
    """Test getting a non-existent contact."""
    response = client.get("/contacts/999999")
    assert response.status_code == 404 