from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

ORIGINAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_activity_catalog():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_adds_new_participant():
    # Arrange
    client = TestClient(app)
    email = "newstudent@mergington.edu"
    path = f"/activities/{quote('Chess Club')}/signup?email={email}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_duplicate_signup_returns_400_and_does_not_duplicate_email():
    # Arrange
    client = TestClient(app)
    email = "michael@mergington.edu"
    path = f"/activities/{quote('Chess Club')}/signup?email={email}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert activities["Chess Club"]["participants"].count(email) == 1


def test_unknown_activity_returns_404():
    # Arrange
    client = TestClient(app)
    email = "newstudent@mergington.edu"
    path = f"/activities/{quote('Unknown Activity')}/signup?email={email}"

    # Act
    response = client.post(path)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_email():
    # Arrange
    client = TestClient(app)
    email = "michael@mergington.edu"
    path = f"/activities/{quote('Chess Club')}/signup?email={email}"

    # Act
    response = client.delete(path)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Chess Club"
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_unknown_participant_returns_404():
    # Arrange
    client = TestClient(app)
    email = "notregistered@mergington.edu"
    path = f"/activities/{quote('Chess Club')}/signup?email={email}"

    # Act
    response = client.delete(path)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
