from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    original_activities = deepcopy(activities)
    with TestClient(app) as test_client:
        yield test_client
    activities.clear()
    activities.update(original_activities)


def test_signup_adds_participant(client):
    email = "new.student@mergington.edu"

    response = client.post(
        "/activities/Art Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Art Club"}
    assert email in client.get("/activities").json()["Art Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    email = "michael@mergington.edu"

    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_unregister_rejects_unregistered_participant(client):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "new.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"