import pytest
from fastapi.testclient import TestClient
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app  # Now this should work
client = TestClient(app)

def test_add_new_user_success():
    """Test creating a new user with valid data."""
    payload = {
        "user_id": "testuser",
        "interests": ["technology", "science"],
        "preferences": {"max_recommendations": 3},
        "demographics": {"age": 25, "location": "Test City", "gender": "other", "occupation": "Tester"}
    }
    response = client.post("/user/user-details", json=payload)
    assert response.status_code in [200, 201]
    json_data = response.json()
    # Check that response contains expected data (e.g., user_id)
    assert "user_id" in json_data
    assert json_data["user_id"] == payload["user_id"]

def test_add_new_user_invalid_json():
    """Test creating a new user with invalid JSON in preferences."""
    payload = {
        "user_id": "testuser_invalid",
        "interests": ["technology"],
        # Providing invalid JSON (as a string that won't parse correctly)
        "preferences": "invalid_json",
        "demographics": {"age": 25, "location": "Test City", "gender": "other"}
    }
    response = client.post("/user/user-details", json=payload)
    # Expecting error because preferences should be a JSON object
    assert response.status_code >= 400

def test_get_recommendation_nonexistent_user():
    """Test fetching recommendations for a user that does not exist."""
    response = client.get("/recommendation/recommendations/?user_id=nonexistent_user")
    # Assuming your API returns a 404 or error message for a non-existent user
    assert response.status_code == 404

def test_get_recommendation_success():
    """
    Test fetching recommendations for an existing user.
    First, create a user then get recommendations.
    """
    # Create a test user
    payload = {
        "user_id": "testuser_recs",
        "interests": ["technology"],
        "preferences": {"max_recommendations": 2},
        "demographics": {"age": 30, "location": "Test City", "gender": "female", "occupation": "Engineer"}
    }
    create_response = client.post("/user/user-details", json=payload)
    assert create_response.status_code in [200, 201]
    
    # Get recommendations for the created user
    rec_response = client.get("/recommendation/recommendations/?user_id=testuser_recs")
    assert rec_response.status_code == 200
    data = rec_response.json()
    # Check that the response includes either Jobs or News recommendations (or both)
    assert "Jobs" in data or "News" in data
    # Optionally, check that the number of recommendations does not exceed the max_recommendations
    if "Jobs" in data:
        assert len(data["Jobs"]) <= payload["preferences"]["max_recommendations"]
    if "News" in data:
        assert len(data["News"]) <= payload["preferences"]["max_recommendations"]

