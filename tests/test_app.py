import pytest
from fastapi.testclient import TestClient

import src.app as app_module


ACTIVITY_NAME = "Chess Club"
EXISTING_EMAIL = "existing@mergington.edu"
NEW_EMAIL = "new@mergington.edu"


@pytest.fixture
def client(monkeypatch):
    activities = {
        ACTIVITY_NAME: {
            "description": "Play chess",
            "schedule": "Fridays",
            "max_participants": 4,
            "participants": [EXISTING_EMAIL],
        }
    }
    monkeypatch.setattr(app_module, "activities", activities)
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_activity = app_module.activities[ACTIVITY_NAME]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {ACTIVITY_NAME: expected_activity}


def test_signup_adds_participant(client):
    # Arrange
    email = NEW_EMAIL

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {ACTIVITY_NAME}"}
    assert email in app_module.activities[ACTIVITY_NAME]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = EXISTING_EMAIL
    original_participants = list(app_module.activities[ACTIVITY_NAME]["participants"])

    # Act
    response = client.post(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}
    assert app_module.activities[ACTIVITY_NAME]["participants"] == original_participants


def test_signup_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": NEW_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant(client):
    # Arrange
    email = EXISTING_EMAIL

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {ACTIVITY_NAME}"}
    assert email not in app_module.activities[ACTIVITY_NAME]["participants"]


def test_unregister_rejects_unregistered_participant(client):
    # Arrange
    email = NEW_EMAIL
    original_participants = list(app_module.activities[ACTIVITY_NAME]["participants"])

    # Act
    response = client.delete(
        f"/activities/{ACTIVITY_NAME}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
    assert app_module.activities[ACTIVITY_NAME]["participants"] == original_participants


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": EXISTING_EMAIL},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}