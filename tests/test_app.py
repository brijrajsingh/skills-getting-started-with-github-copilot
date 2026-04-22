from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert payload["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "pytest-signup-success@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity_name]["participants"]


def test_signup_for_activity_returns_not_found_for_unknown_activity():
    # Arrange
    activity_name = "Robotics Club"
    email = "pytest-signup-missing@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_for_activity_rejects_duplicate_participant():
    # Arrange
    activity_name = "Programming Class"
    email = "pytest-signup-duplicate@mergington.edu"
    first_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert first_response.status_code == 200

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}


def test_unregister_from_activity_removes_existing_participant():
    # Arrange
    activity_name = "Soccer Team"
    email = "pytest-unregister-success@mergington.edu"
    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert signup_response.status_code == 200

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}

    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity_name]["participants"]


def test_unregister_from_activity_returns_not_found_for_unknown_activity():
    # Arrange
    activity_name = "Robotics Club"
    email = "pytest-unregister-missing-activity@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_from_activity_returns_not_found_for_missing_student():
    # Arrange
    activity_name = "Art Club"
    email = "pytest-unregister-missing-student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student not signed up"}