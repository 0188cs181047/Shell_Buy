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
        "headers": {"Authorization": f"Bearer {token}"}
    }


# =========================
# 🔹 PRODUCT FIXTURE
# =========================
@pytest.fixture
def product(auth_data):
    form_data = {
        "title": f"Product_{uuid.uuid4()}",
        "description": "Test Description",
        "category": "electronics",
        "quantity": "10",
        "quantity_name": "kg",
        "quality": "good",
        "pickup_address": "Test Address",
        "latitude": "28.61",
        "longitude": "77.20"
    }

    response = client.post(
        "/products/add/",
        data=form_data,
        headers=auth_data["headers"]
    )

    return response.json()


# =========================
# 🔹 ADD PRODUCT
# =========================
def test_add_product(auth_data):
    form_data = {
        "title": "Test Product",
        "description": "Test Description",
        "category": "electronics",
        "quantity": "10",
        "quantity_name": "kg",
        "quality": "good",
        "pickup_address": "Test Address",
        "latitude": "28.61",
        "longitude": "77.20"
    }

    response = client.post(
        "/products/add/",
        data=form_data,
        headers=auth_data["headers"]
    )

    assert response.status_code == 201


# =========================
# 🔹 GET PRODUCTS
# =========================
def test_get_products_with_limit(auth_data):
    for _ in range(5):
        client.post(
            "/products/add/",
            data={
                "title": f"Product_{uuid.uuid4()}",
                "description": "Test",
                "category": "electronics",
                "quantity": "10",
                "quantity_name": "kg",
                "quality": "good",
                "pickup_address": "Address",
                "latitude": "28.61",
                "longitude": "77.20"
            },
            headers=auth_data["headers"]
        )

    response = client.get("/products/details/?offset=0&limit=2")

    assert response.status_code == 200
    assert len(response.json()) <= 2


# =========================
# 🔹 GET PRODUCT BY ID
# =========================
def test_get_product_by_id(auth_data, product):
    response = client.get(
        f"/products/detail/{product['id']}",
        headers=auth_data["headers"]
    )

    assert response.status_code == 200
    assert response.json()["id"] == product["id"]


# =========================
# 🔹 UPDATE PRODUCT
# =========================
def test_update_product(auth_data, product):
    headers = auth_data["headers"]

    update_data = {
        "title": "Updated Product",
        "description": "Updated Description",
        "category": "electronics",
        "quantity": "5",
        "quantity_name": "kg",
        "quality": "good",
        "pickup_address": "Updated Address",
        "latitude": "28.70",
        "longitude": "77.10"
    }

    response = client.put(
        f"/products/update/{product['id']}",
        data=update_data,
        headers=headers
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Updated Product"

# =========================
# 🔹 DELETE PRODUCT
# =========================
def test_delete_product(auth_data, product):
    response = client.delete(
        f"/products/delete/{product['id']}",
        headers=auth_data["headers"]
    )

    assert response.status_code == 200


# =========================
# 🔹 IMAGE TESTS
# =========================
def test_update_product_image(auth_data):
    # create product with image
    form_data = {
        "title": "Test Product",
        "description": "Test",
        "category": "electronics",
        "quantity": "10",
        "quantity_name": "kg",
        "quality": "good",
        "pickup_address": "Address",
        "latitude": "28.61",
        "longitude": "77.20"
    }

    files = [("images", ("test.jpg", b"img", "image/jpeg"))]

    res = client.post(
        "/products/add/",
        data=form_data,
        files=files,
        headers=auth_data["headers"]
    )

    image_id = res.json()["images"][0]["id"]

    response = client.patch(
        f"/products/update_image/{image_id}",
        files={"image": ("new.jpg", b"new", "image/jpeg")},
        headers=auth_data["headers"]
    )

    assert response.status_code == 200


def test_delete_product_image(auth_data):
    form_data = {
        "title": "Test Product",
        "description": "Test",
        "category": "electronics",
        "quantity": "10",
        "quantity_name": "kg",
        "quality": "good",
        "pickup_address": "Address",
        "latitude": "28.61",
        "longitude": "77.20"
    }

    files = [("images", ("test.jpg", b"img", "image/jpeg"))]

    res = client.post(
        "/products/add/",
        data=form_data,
        files=files,
        headers=auth_data["headers"]
    )

    image_id = res.json()["images"][0]["id"]

    response = client.delete(
        f"/products/delete_image/{image_id}",
        headers=auth_data["headers"]
    )

    assert response.status_code == 200


# =========================
# 🔹 GET IMAGE
# =========================
def test_get_product_image(auth_data):
    form_data = {
        "title": "Test Product",
        "description": "Test",
        "category": "electronics",
        "quantity": "10",
        "quantity_name": "kg",
        "quality": "good",
        "pickup_address": "Address",
        "latitude": "28.61",
        "longitude": "77.20"
    }

    files = [("images", ("test.jpg", b"img", "image/jpeg"))]

    res = client.post(
        "/products/add/",
        data=form_data,
        files=files,
        headers=auth_data["headers"]
    )

    image_id = res.json()["images"][0]["id"]

    response = client.get(
        f"/products/see_production_image/{image_id}",
        headers=auth_data["headers"]
    )

    assert response.status_code == 200


# =========================
# 🔹 PUBLISH
# =========================
def test_publish_product(auth_data, product):
    response = client.post(
        "/products/publish",
        json={
            "product_id": product["id"],
            "publish_type": "free",
            "amount": None
        },
        headers=auth_data["headers"]
    )

    assert response.status_code == 200


def test_update_publish(auth_data, product):
    # first publish
    client.post(
        "/products/publish",
        json={
            "product_id": product["id"],
            "publish_type": "free",
            "amount": None
        },
        headers=auth_data["headers"]
    )

    # update
    response = client.put(
        f"/products/publish/{product['id']}",
        json={"publish_type": "paid", "amount": 100},
        headers=auth_data["headers"]
    )

    assert response.status_code == 200
    assert response.json()["publish_type"] == "paid"