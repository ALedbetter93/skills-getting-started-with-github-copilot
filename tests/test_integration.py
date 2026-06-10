"""Integration tests for cross-endpoint scenarios."""

import pytest


def test_signup_appears_in_get_activities(client, sample_activity_name):
    """Test that a signup is immediately visible in GET /activities."""
    email = "integration_test1@mergington.edu"
    
    # Get initial state
    response = client.get("/activities")
    initial_participants = response.json()[sample_activity_name]["participants"]
    
    # Sign up
    client.post(
        f"/activities/{sample_activity_name}/signup",
        params={"email": email}
    )
    
    # Get updated state
    response = client.get("/activities")
    updated_participants = response.json()[sample_activity_name]["participants"]
    
    # Verify the count increased and new email is present
    assert len(updated_participants) == len(initial_participants) + 1
    assert email in updated_participants


def test_unregister_appears_in_get_activities(client, sample_activity_name):
    """Test that an unregister is immediately visible in GET /activities."""
    email = "integration_test2@mergington.edu"
    
    # Sign up first
    client.post(
        f"/activities/{sample_activity_name}/signup",
        params={"email": email}
    )
    
    response = client.get("/activities")
    before_unregister = len(response.json()[sample_activity_name]["participants"])
    
    # Unregister
    client.delete(
        f"/activities/{sample_activity_name}/participants",
        params={"email": email}
    )
    
    # Get updated state
    response = client.get("/activities")
    after_unregister = len(response.json()[sample_activity_name]["participants"])
    
    # Verify count decreased
    assert after_unregister == before_unregister - 1
    assert email not in response.json()[sample_activity_name]["participants"]


def test_signup_unregister_cycle(client, sample_activity_name):
    """Test complete signup and unregister cycle."""
    email = "cycle_test@mergington.edu"
    
    # Verify not initially registered
    response = client.get("/activities")
    assert email not in response.json()[sample_activity_name]["participants"]
    
    # Sign up
    signup_response = client.post(
        f"/activities/{sample_activity_name}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # Verify now registered
    response = client.get("/activities")
    assert email in response.json()[sample_activity_name]["participants"]
    
    # Unregister
    unregister_response = client.delete(
        f"/activities/{sample_activity_name}/participants",
        params={"email": email}
    )
    assert unregister_response.status_code == 200
    
    # Verify back to unregistered state
    response = client.get("/activities")
    assert email not in response.json()[sample_activity_name]["participants"]


def test_multiple_students_signup_and_unregister(client, sample_activity_name):
    """Test multiple students signing up and some unregistering."""
    emails = ["student_a@mergington.edu", "student_b@mergington.edu", "student_c@mergington.edu"]
    
    # All sign up
    for email in emails:
        client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )
    
    response = client.get("/activities")
    assert len(response.json()[sample_activity_name]["participants"]) >= 3
    
    # First student unregisters
    client.delete(
        f"/activities/{sample_activity_name}/participants",
        params={"email": emails[0]}
    )
    
    # Verify first is gone but others remain
    response = client.get("/activities")
    participants = response.json()[sample_activity_name]["participants"]
    assert emails[0] not in participants
    assert emails[1] in participants
    assert emails[2] in participants


def test_max_participants_handling(client):
    """Test behavior when activity has max participants."""
    # Find an activity with lower max_participants
    response = client.get("/activities")
    activities = response.json()
    
    # Chess Club has max 12, let's use that
    test_activity = "Chess Club"
    max_participants = activities[test_activity]["max_participants"]
    current_participants = len(activities[test_activity]["participants"])
    
    # If there's room, try to fill it
    if current_participants < max_participants:
        new_participants_to_add = max_participants - current_participants
        
        for i in range(new_participants_to_add):
            email = f"capacity_test_{i}@mergington.edu"
            response = client.post(
                f"/activities/{test_activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify we've hit capacity
        response = client.get("/activities")
        actual_count = len(response.json()[test_activity]["participants"])
        assert actual_count == max_participants
