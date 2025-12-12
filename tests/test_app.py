"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        "Soccer Team": {
            "description": "Practice soccer skills and compete in inter-school matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["alex@mergington.edu", "sarah@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Train and compete in basketball tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["emily@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Class": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Thursdays, 3:00 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 3:00 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "mia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["william@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear existing activities
    activities.clear()
    
    # Add original state back
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Soccer Team" in data
        assert "Basketball Team" in data
        assert len(data) == 9
    
    def test_get_activities_includes_participant_list(self, client, reset_activities):
        """Test that activities include participant information"""
        response = client.get("/activities")
        data = response.json()
        assert "participants" in data["Soccer Team"]
        assert "alex@mergington.edu" in data["Soccer Team"]["participants"]
    
    def test_get_activities_includes_activity_details(self, client, reset_activities):
        """Test that activities include all required details"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Soccer Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Soccer Team"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client, reset_activities):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity"""
        # Try to sign up someone who is already registered
        response = client.post(
            "/activities/Soccer Team/signup",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_for_different_activity(self, client, reset_activities):
        """Test that a student can sign up for multiple different activities"""
        # First, sign up for Basketball
        response1 = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Then, sign up for Drama Club
        response2 = client.post(
            "/activities/Drama Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response2.status_code == 200
        
        # Verify both signups were successful
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Basketball Team"]["participants"]
        assert "newstudent@mergington.edu" in activities_data["Drama Club"]["participants"]


class TestUnregisterFromActivity:
    """Test the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Soccer Team/unregister",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "alex@mergington.edu" in data["message"]
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "alex@mergington.edu" not in activities_data["Soccer Team"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistration from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test unregistration of a student not signed up for the activity"""
        response = client.delete(
            "/activities/Soccer Team/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_multiple_participants(self, client, reset_activities):
        """Test unregistering one participant doesn't affect others"""
        # Verify initial state
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        initial_count = len(activities_data["Soccer Team"]["participants"])
        
        # Unregister one participant
        response = client.delete(
            "/activities/Soccer Team/unregister",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify only one was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert len(activities_data["Soccer Team"]["participants"]) == initial_count - 1
        assert "sarah@mergington.edu" in activities_data["Soccer Team"]["participants"]


class TestRoot:
    """Test the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
