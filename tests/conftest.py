"""Pytest configuration and fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Provide a fresh TestClient for each test."""
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Provide a consistent test email."""
    return "test@mergington.edu"


@pytest.fixture
def sample_activity_name():
    """Provide a consistent test activity name."""
    return "Chess Club"


@pytest.fixture
def valid_activities():
    """Return list of valid activity names in the app."""
    return [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Basketball Team",
        "Yoga Club",
        "Drama Club",
        "Art Workshop",
        "Math Olympiad",
        "Science Bowl"
    ]
