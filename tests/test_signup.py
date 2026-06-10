"""Tests for the POST /activities/{activity_name}/signup endpoint."""

import pytest


def test_signup_success(client, sample_activity_name, sample_email):
    """Test successful signup for an activity."""
    response = client.post(
        f"/activities/{sample_activity_name}/signup",
        params={"email": sample_email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert sample_email in data["message"]
    assert sample_activity_name in data["message"]


def test_signup_adds_participant_to_activity(client, sample_activity_name, sample_email):
    """Test that signup actually adds the participant to the activity."""
    # Sign up
    client.post(
        f"/activities/{sample_activity_name}/signup",
        params={"email": sample_email}
    )
    
    # Verify participant was added
    response = client.get("/activities")
    activities = response.json()
    participants = activities[sample_activity_name]["participants"]
    
    assert sample_email in participants


def test_signup_nonexistent_activity_returns_404(client, sample_email):
    """Test that signing up for non-existent activity returns 404."""
    response = client.post(
        "/activities/Nonexistent Activity/signup",
        params={"email": sample_email}
    )
    
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_already_registered_returns_400(client, sample_activity_name, sample_email):
    """Test that signing up twice returns 400 error."""
    # First signup
    client.post(
        f"/activities/{sample_activity_name}/signup",
        params={"email": sample_email}
    )
    
    # Second signup with same email
    response = client.post(
        f"/activities/{sample_activity_name}/signup",
        params={"email": sample_email}
    )
    
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_multiple_students_to_same_activity(client, sample_activity_name):
    """Test that multiple different students can sign up for same activity."""
    emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
    
    for email in emails:
        response = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all are signed up
    response = client.get("/activities")
    participants = response.json()[sample_activity_name]["participants"]
    
    for email in emails:
        assert email in participants


def test_signup_same_student_multiple_activities(client, valid_activities):
    """Test that same student can sign up for multiple different activities."""
    email = "versatile@mergington.edu"
    
    for activity in valid_activities[:3]:  # Sign up for first 3 activities
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify student is in all 3 activities
    response = client.get("/activities")
    activities = response.json()
    
    for activity in valid_activities[:3]:
        assert email in activities[activity]["participants"]


def test_signup_with_missing_email_param(client, sample_activity_name):
    """Test that signup without email parameter fails."""
    response = client.post(f"/activities/{sample_activity_name}/signup")
    
    # FastAPI should return 422 (validation error) for missing required param
    assert response.status_code == 422
