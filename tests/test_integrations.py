import pytest
import requests

BASE_URL = "http://localhost:8000"

def test_create_and_get_customer():
    email = "testcreategetcustomer@example.com"
    response = requests.post(f"{BASE_URL}/customers", json={"name": "User", "email": email})
    assert response.status_code == 201
    customer = response.json()

    response = requests.get(f"{BASE_URL}/customers/{customer['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email

    requests.delete(f"{BASE_URL}/customers/{customer['id']}")


def test_update_customer():
    response = requests.post(f"{BASE_URL}/customers", json={"name": "User", "email": "testupdatecustomer@example.com"})
    assert response.status_code == 201
    customer = response.json()

    response = requests.put(
        f"{BASE_URL}/customers/{customer['id']}",
        json={"name": "Updated Name", "email": "independent2@example.com"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

    requests.delete(f"{BASE_URL}/customers/{customer['id']}")


def test_delete_customer():
    response = requests.post(f"{BASE_URL}/customers", json={"name": "User", "email": "testdeletecustomer@example.com"})
    assert response.status_code == 201
    customer = response.json()

    response = requests.delete(f"{BASE_URL}/customers/{customer['id']}")
    assert response.status_code == 204

    response = requests.get(f"{BASE_URL}/customers/{customer['id']}")
    assert response.status_code == 400


def test_add_and_remove_product_from_wishlist():
    response = requests.post(f"{BASE_URL}/customers", json={"name": "User", "email": "testaddremoveproduct@example.com"})
    customer = response.json()

    try:
        assert response.status_code == 201

        product_id = 1

        response = requests.post(
            f"{BASE_URL}/customers/{customer['id']}/wishlist/{product_id}?test_products=true"
        )
        assert response.status_code == 201

        response = requests.get(
            f"{BASE_URL}/customers/{customer['id']}/wishlist?test_products=true"
        )
        assert response.status_code == 200
        products = response.json()
        assert any(product["id"] == product_id for product in products)

        response = requests.delete(f"{BASE_URL}/customers/{customer['id']}/wishlist/{product_id}")
        assert response.status_code == 204

        response = requests.get(
            f"{BASE_URL}/customers/{customer['id']}/wishlist?test_products=true"
        )
        assert response.status_code == 200
        products = response.json()
        assert all(str(prod["id"]) != product_id for prod in products)
    finally:
        requests.delete(f"{BASE_URL}/customers/{customer['id']}")


@pytest.mark.parametrize("payload, expected_status", [
    ({"name": "User", "email": "invalid-email"}, 422),
    ({"name": "User"}, 422),
    ({}, 422),
])
def test_create_customer_invalid_payload(payload, expected_status):
    response = requests.post(f"{BASE_URL}/customers", json=payload)
    assert response.status_code == expected_status


def test_create_customer_duplicate_email():
    email = "duplicated@example.com"
    customer_1 = requests.post(f"{BASE_URL}/customers", json={"name": "User", "email": email})
    assert customer_1.status_code == 201

    customer_2 = requests.post(f"{BASE_URL}/customers", json={"name": "Other", "email": email})
    assert customer_2.status_code == 400

    requests.delete(f"{BASE_URL}/customers/{customer_1.json()['id']}")


@pytest.mark.parametrize("customer_id, payload, expected_status", [
    (999999, {"name": "Updated", "email": "updated@example.com"}, 404),
    (0, {"name": "Updated", "email": "updated@example.com"}, 404),
])
def test_update_nonexistent_customer(customer_id, payload, expected_status):
    response = requests.put(f"{BASE_URL}/customers/{customer_id}", json=payload)
    assert response.status_code == expected_status


@pytest.mark.parametrize("customer_id, expected_status", [
    (999999, 404),
    (0, 404),
])
def test_delete_nonexistent_customer(customer_id, expected_status):
    response = requests.delete(f"{BASE_URL}/customers/{customer_id}")
    assert response.status_code == expected_status


@pytest.mark.parametrize("product_id, expected_status", [
    (999999, [503, 404]),
    (0, [503, 404]),
])
def test_add_invalid_product_to_wishlist(product_id, expected_status):
    customer = requests.post(f"{BASE_URL}/customers", json={"name": "User", "email": f"invalidproduct{product_id}@example.com"}).json()
    try:
        response = requests.post(
            f"{BASE_URL}/customers/{customer['id']}/wishlist/{product_id}?test_products=false"
        )
        assert response.status_code in expected_status
    finally:
        requests.delete(f"{BASE_URL}/customers/{customer['id']}")


def test_remove_nonexistent_product_from_wishlist():
    customer = requests.post(f"{BASE_URL}/customers", json={"name": "User", "email": "testnonexistentproduct@example.com"}).json()
    try:
        response = requests.delete(f"{BASE_URL}/customers/{customer['id']}/wishlist/12345")
        assert response.status_code == 404
    finally:
        requests.delete(f"{BASE_URL}/customers/{customer['id']}")


@pytest.mark.parametrize("customer_id", [999999, 0])
def test_add_product_to_nonexistent_customer(customer_id):
    response = requests.post(
        f"{BASE_URL}/customers/{customer_id}/wishlist/1?test_products=true"
    )
    assert response.status_code == 404
