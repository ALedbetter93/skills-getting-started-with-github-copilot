"""Tests for the GET /activities and root endpoints."""

import pytest


def test_get_activities_returns_list(client):
    """Test that GET /activities returns all activities."""
    response = client.get("/activities")
    
    assert response.status_code == 200
    activities = response.json()
    
    # Verify it's a dictionary with activities
    assert isinstance(activities, dict)
    assert len(activities) > 0


def test_get_activities_has_required_fields(client):
    """Test that each activity has required fields."""
    response = client.get("/activities")
    activities = response.json()
    
    required_fields = {"description", "schedule", "max_participants", "participants"}
    
    for activity_name, activity_data in activities.items():
        assert isinstance(activity_name, str)
        assert all(field in activity_data for field in required_fields)
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)


def test_get_activities_participants_are_emails(client):
    """Test that participants list contains email addresses."""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant


def test_root_redirects_to_static(client):
    """Test that GET / redirects to /static/index.html."""
    response = client.get("/", follow_redirects=False)
    
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"
