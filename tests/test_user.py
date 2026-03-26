from fastapi.testclient import TestClient
from app.model.user_category import UserCategory
import uuid
from app.app import app

client = TestClient(app)
def create_user_and_get_token_mail_id():

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

    return token, email, user_data["id"]

def create_category(session):
    category = UserCategory(
        name=f"Category_{uuid.uuid4()}",
        access_level_start=1,
        access_level_end=5
    )
    session.add(category)
    session.commit()
    session.refresh(category)

    return category

def test_register_user():
    payload = {
        "name": "Test User",
        "email": f"test_{uuid.uuid4()}@example.com",
        "phone_number": "9999999999",
        "password": "test@123"
    }

    response = client.post("/auth/register/", json=payload)
    assert response.status_code == 201

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

def test_create_category():
    token, email, user_id = create_user_and_get_token_mail_id()

    payload = {
        "name": f"Category_{uuid.uuid4()}",
        "access_level_start": 10,
        "access_level_end": 15
    }

    response = client.post(
        "/user-category/",
        json=payload,
        headers={
            "Authorization": f"Bearer {token}" 
        }
    )
    assert response.status_code == 201

def test_create_user_success():
    token, email, user_id = create_user_and_get_token_mail_id()
    payload = {
        "name": "Shiv",
        "email": f"shiv_{uuid.uuid4()}@test.com",
        "phone_number": "9876543210",
        "password": "test123"
    }
    response = client.post(
        "/users/add",
        json=payload,
        headers={
            "Authorization": f"Bearer {token}" 
        }        
    )
    assert response.status_code == 201

def test_read_users_success():
    token, email, user_id = create_user_and_get_token_mail_id()

    response = client.get(
        "/users/details/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

def test_read_users_pagination():
    token, email, user_id = create_user_and_get_token_mail_id()

    response = client.get(
        "/users/details/?offset=0&limit=2",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) <= 2

def test_read_users_limit_exceeded():
    token, email, user_id = create_user_and_get_token_mail_id()

    response = client.get(
        "/users/details/?limit=101",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422

def test_read_user_success():
    token, email, user_id = create_user_and_get_token_mail_id()

    response = client.get(
        f"/users/detail/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

def test_update_user_success():
    token, email, user_id  = create_user_and_get_token_mail_id()

    updated_payload = {
        "name": "Updated Name",
        "email": f"updated_{uuid.uuid4()}@test.com",
        "phone_number": "8888888888"
    }

    response = client.put(
        f"/users/edit/{user_id}",
        json=updated_payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == updated_payload["name"]
    assert data["email"] == updated_payload["email"]
    assert data["phone_number"] == updated_payload["phone_number"]

def test_update_user_partial_name_only():
    token, email, user_id  = create_user_and_get_token_mail_id()

    payload = {
        "name": "Updated Name"
    }

    response = client.patch(
        f"/users/edit_partial/{user_id}",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["email"] == email

def test_delete_user_success():
    token, email, user_id  = create_user_and_get_token_mail_id()

    response = client.delete(
        f"/users/delete/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["deleted_user"]["id"] == user_id
    assert data["deleted_user"]["email"] == email

def test_bulk_delete_success():
    token, email, user1_id  = create_user_and_get_token_mail_id()
    token, email, user2_id  = create_user_and_get_token_mail_id()

    payload = [user1_id, user2_id]

    response = client.request(
        "DELETE",
        "/users/bulk-delete/",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data["deleted_users"]) == 2
    assert data["not_found"] == []
