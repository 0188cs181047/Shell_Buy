import pytest
from fastapi.testclient import TestClient
import uuid
from app.app import app

client = TestClient(app)


# =========================
# 🔹 AUTH FIXTURE (RUN ONCE)
# =========================
@pytest.fixture(scope="session")
def auth_data():
    email = f"user_{uuid.uuid4()}@test.com"

    register_payload = {
        "name": "TestUser",
        "email": email,
        "phone_number": "9999999999",
        "password": "test@123"
    }

    register_response = client.post("/auth/register/", json=register_payload)
    user_data = register_response.json()

    login_payload = {
        "username": email,
        "password": "test@123"
    }

    response = client.post("/auth/login/", data=login_payload)
    token = response.json()["access_token"]

    return {
        "token": token,
        "user_id": user_data["id"],
        "email": email,
        "headers": {"Authorization": f"Bearer {token}"}
    }


# =========================
# 🔹 USER FIXTURE
# =========================
@pytest.fixture
def new_user(auth_data):
    payload = {
        "name": "Shiv",
        "email": f"shiv_{uuid.uuid4()}@test.com",
        "phone_number": "9876543210",
        "password": "test123"
    }

    response = client.post(
        "/users/add",
        json=payload,
        headers=auth_data["headers"]
    )

    return response.json()


# =========================
# 🔹 REGISTER
# =========================
def test_register_user():
    payload = {
        "name": "Test User",
        "email": f"test_{uuid.uuid4()}@example.com",
        "phone_number": "9999999999",
        "password": "test@123"
    }

    response = client.post("/auth/register/", json=payload)
    assert response.status_code == 201


# =========================
# 🔹 LOGIN FAILURE
# =========================
def test_login_invalid_password():
    email = f"user_{uuid.uuid4()}@test.com"

    client.post("/auth/register/", json={
        "name": "WrongPass",
        "email": email,
        "phone_number": "9999999999",
        "password": "test@123"
    })

    response = client.post(
        "/auth/login/",
        data={
            "username": email,
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


# =========================
# 🔹 CREATE CATEGORY
# =========================
def test_create_category(auth_data):
    payload = {
        "name": f"Category_{uuid.uuid4()}",
        "access_level_start": 10,
        "access_level_end": 15
    }

    response = client.post(
        "/user-category/",
        json=payload,
        headers=auth_data["headers"]
    )

    assert response.status_code == 201


# =========================
# 🔹 CREATE USER
# =========================
def test_create_user(auth_data):
    payload = {
        "name": "Shiv",
        "email": f"shiv_{uuid.uuid4()}@test.com",
        "phone_number": "9876543210",
        "password": "test123"
    }

    response = client.post(
        "/users/add",
        json=payload,
        headers=auth_data["headers"]
    )

    assert response.status_code == 201


# =========================
# 🔹 GET USERS
# =========================
def test_read_users(auth_data):
    response = client.get(
        "/users/details/",
        headers=auth_data["headers"]
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_read_users_pagination(auth_data):
    response = client.get(
        "/users/details/?offset=0&limit=2",
        headers=auth_data["headers"]
    )

    assert response.status_code == 200
    assert len(response.json()) <= 2


def test_read_users_limit_exceeded(auth_data):
    response = client.get(
        "/users/details/?limit=101",
        headers=auth_data["headers"]
    )

    assert response.status_code == 422


# =========================
# 🔹 GET USER BY ID
# =========================
def test_read_user(auth_data):
    response = client.get(
        f"/users/detail/{auth_data['user_id']}",
        headers=auth_data["headers"]
    )

    assert response.status_code == 200


# =========================
# 🔹 UPDATE USER
# =========================
def test_update_user(auth_data):
    updated_payload = {
        "name": "Updated Name",
        "email": f"updated_{uuid.uuid4()}@test.com",
        "phone_number": "8888888888"
    }

    response = client.put(
        f"/users/edit/{auth_data['user_id']}",
        json=updated_payload,
        headers=auth_data["headers"]
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == updated_payload["name"]


# =========================
# 🔹 PARTIAL UPDATE
# =========================
def test_update_user_partial(auth_data):
    payload = {"name": "Updated Name"}

    response = client.patch(
        f"/users/edit_partial/{auth_data['user_id']}",
        json=payload,
        headers=auth_data["headers"]
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


# =========================
# 🔹 DELETE USER
# =========================
def test_delete_user(auth_data):
    response = client.delete(
        f"/users/delete/{auth_data['user_id']}",
        headers=auth_data["headers"]
    )

    assert response.status_code == 200
