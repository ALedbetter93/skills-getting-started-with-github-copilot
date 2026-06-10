"""Tests for the DELETE /activities/{activity_name}/participants endpoint."""

import pytest


def test_unregister_success(client, sample_activity_name):
    """Test successful unregistration from an activity."""
    email = "unregister_test@mergington.edu"
    
    # Sign up first
    client.post(
        f"/activities/{sample_activity_name}/signup",
        params={"email": email}
    )
    
    # Unregister
    response = client.delete(
        f"/activities/{sample_activity_name}/participants",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert sample_activity_name in data["message"]


def test_unregister_removes_participant(client, sample_activity_name):
    """Test that unregister actually removes the participant."""
    email = "remove_test@mergington.edu"
    
    # Sign up
    client.post(
        f"/activities/{sample_activity_name}/signup",
        params={"email": email}
    )
    
    # Verify participant was added
    response = client.get("/activities")
    assert email in response.json()[sample_activity_name]["participants"]
    
    # Unregister
    client.delete(
        f"/activities/{sample_activity_name}/participants",
        params={"email": email}
    )
    
    # Verify participant was removed
    response = client.get("/activities")
    assert email not in response.json()[sample_activity_name]["participants"]


def test_unregister_nonexistent_activity_returns_404(client):
    """Test that unregistering from non-existent activity returns 404."""
    response = client.delete(
        "/activities/Fake Activity/participants",
        params={"email": "test@mergington.edu"}
    )
    
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_nonexistent_participant_returns_404(client, sample_activity_name):
    """Test that unregistering non-existent participant returns 404."""
    response = client.delete(
        f"/activities/{sample_activity_name}/participants",
        params={"email": "notregistered@mergington.edu"}
    )
    
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_unregister_idempotency_fails_on_second_attempt(client, sample_activity_name):
    """Test that unregistering twice fails on second attempt."""
    email = "idempotent_test@mergington.edu"
    
    # Sign up
    client.post(
        f"/activities/{sample_activity_name}/signup",
        params={"email": email}
    )
    
    # First unregister - should succeed
    response1 = client.delete(
        f"/activities/{sample_activity_name}/participants",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second unregister - should fail (participant no longer exists)
    response2 = client.delete(
        f"/activities/{sample_activity_name}/participants",
        params={"email": email}
    )
    assert response2.status_code == 404


def test_unregister_only_affects_specified_activity(client, valid_activities):
    """Test that unregistering from one activity doesn't affect others."""
    email = "multi_activity@mergington.edu"
    activity1, activity2 = valid_activities[0], valid_activities[1]
    
    # Sign up for two activities
    client.post(f"/activities/{activity1}/signup", params={"email": email})
    client.post(f"/activities/{activity2}/signup", params={"email": email})
    
    # Unregister from first activity
    client.delete(
        f"/activities/{activity1}/participants",
        params={"email": email}
    )
    
    # Verify removed from activity1 but still in activity2
    response = client.get("/activities")
    activities = response.json()
    
    assert email not in activities[activity1]["participants"]
    assert email in activities[activity2]["participants"]


def test_unregister_with_missing_email_param(client, sample_activity_name):
    """Test that unregister without email parameter fails."""
    response = client.delete(f"/activities/{sample_activity_name}/participants")
    
    # FastAPI should return 422 (validation error) for missing required param
    assert response.status_code == 422
