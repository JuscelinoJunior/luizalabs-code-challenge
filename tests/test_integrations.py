import pytest
import requests

BASE_URL = "http://localhost:8000"


def get_header_with_access_token(email, password):
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    user = response.json()
    return {"Authorization": f"Bearer {user['access_token']}"}

@pytest.fixture(scope="session")
def admin_header():
    return get_header_with_access_token("admin@luizalabs.com", "luizaAdmin")

def test_create_and_get_customer(admin_header):
    email = "testcreategetcustomer@example.com"
    response = requests.post(f"{BASE_URL}/users", json={"name": "User", "email": email, "role": "customer", "password": "1234567"}, headers=admin_header)
    assert response.status_code == 201
    customer = response.json()

    response = requests.get(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email

    requests.delete(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)


def test_create_and_try_get_other_customer(admin_header):
    response = requests.post(f"{BASE_URL}/users", json={"name": "User", "email": "testcreategetothercustomer@example.com", "role": "customer", "password": "1234567"}, headers=admin_header)
    assert response.status_code == 201
    customer = response.json()

    response_customer2 = requests.post(f"{BASE_URL}/users", json={"name": "User", "email": "testcreategetothercustomer2@example.com", "role": "customer", "password": "1234567"}, headers=admin_header)
    assert response_customer2.status_code == 201
    customer2 = response_customer2.json()

    customer2_header = get_header_with_access_token("testcreategetothercustomer2@example.com", "1234567")

    try:
        # Must fail with forbidden because the token is from another customer
        response = requests.get(f"{BASE_URL}/users/{customer['id']}", headers=customer2_header)
        assert response.status_code == 403
    finally:
        requests.delete(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)
        requests.delete(f"{BASE_URL}/users/{customer2['id']}", headers=admin_header)


def test_update_customer(admin_header):
    response = requests.post(f"{BASE_URL}/users", json={"name": "User", "email": "testupdatecustomer@example.com", "role": "customer", "password": "1234567"}, headers=admin_header)
    assert response.status_code == 201
    customer = response.json()

    try:
        response = requests.put(
            f"{BASE_URL}/users/{customer['id']}",
            json={"name": "Updated Name", "email": "independent2@example.com"},
            headers=admin_header
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
    finally:
        requests.delete(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)


def test_delete_customer(admin_header):
    response = requests.post(f"{BASE_URL}/users", json={"name": "User", "email": "testdeletecustomer@example.com", "role": "customer", "password": "1234567"}, headers=admin_header)
    assert response.status_code == 201
    customer = response.json()

    response = requests.delete(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)
    assert response.status_code == 204

    response = requests.get(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)
    assert response.status_code == 404


def test_add_and_remove_product_from_wishlist(admin_header):
    response = requests.post(f"{BASE_URL}/users", json={"name": "User", "email": "testaddremoveproduct@example.com", "role": "customer", "password": "1234567"}, headers=admin_header)
    customer = response.json()

    try:
        assert response.status_code == 201

        product_id = 1

        response = requests.post(
            f"{BASE_URL}/users/{customer['id']}/wishlist/{product_id}?test_products=true",
            headers=admin_header
        )
        assert response.status_code == 201

        response = requests.get(
            f"{BASE_URL}/users/{customer['id']}/wishlist?test_products=true",
            headers=admin_header
        )
        assert response.status_code == 200
        products = response.json()
        assert any(product["id"] == product_id for product in products)

        response = requests.delete(f"{BASE_URL}/users/{customer['id']}/wishlist/{product_id}", headers=admin_header)
        assert response.status_code == 204

        response = requests.get(
            f"{BASE_URL}/users/{customer['id']}/wishlist?test_products=true",
            headers=admin_header
        )
        assert response.status_code == 200
        products = response.json()
        assert all(str(prod["id"]) != product_id for prod in products)
    finally:
        requests.delete(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)


@pytest.mark.parametrize("payload, expected_status", [
    ({"name": "User", "email": "invalid-email"}, 422),
    ({"name": "User"}, 422),
    ({}, 422),
])
def test_create_customer_invalid_payload(payload, expected_status, admin_header):
    response = requests.post(f"{BASE_URL}/users", json=payload, headers=admin_header)
    assert response.status_code == expected_status


def test_create_customer_duplicate_email(admin_header):
    email = "duplicated@example.com"
    customer_1 = requests.post(f"{BASE_URL}/users", json={"name": "User", "email": email, "role": "customer", "password": "1234567"}, headers=admin_header)
    assert customer_1.status_code == 201

    customer_2 = requests.post(f"{BASE_URL}/users", json={"name": "Other", "email": email, "role": "customer", "password": "1234567"}, headers=admin_header)
    assert customer_2.status_code == 400

    requests.delete(f"{BASE_URL}/users/{customer_1.json()['id']}", headers=admin_header)


@pytest.mark.parametrize("user_id, payload, expected_status", [
    (999999, {"name": "Updated", "email": "updated@example.com"}, 404),
    (0, {"name": "Updated", "email": "updated@example.com"}, 404),
])
def test_update_nonexistent_customer(user_id, payload, expected_status, admin_header):
    response = requests.put(f"{BASE_URL}/users/{user_id}", json=payload, headers=admin_header)
    assert response.status_code == expected_status


@pytest.mark.parametrize("user_id, expected_status", [
    (999999, 404),
    (0, 404),
])
def test_delete_nonexistent_customer(user_id, expected_status, admin_header):
    response = requests.delete(f"{BASE_URL}/users/{user_id}", headers=admin_header)
    assert response.status_code == expected_status


@pytest.mark.parametrize("product_id, expected_status", [
    (999999, [503, 404]),
    (0, [503, 404]),
])
def test_add_invalid_product_to_wishlist(product_id, expected_status, admin_header):
    customer = requests.post(f"{BASE_URL}/users", json={"name": "User", "email": f"invalidproduct{product_id}@example.com", "role": "customer", "password": "1234567"}, headers=admin_header).json()
    print(customer)
    try:
        response = requests.post(
            f"{BASE_URL}/users/{customer['id']}/wishlist/{product_id}?test_products=false",
            headers=admin_header
        )
        assert response.status_code in expected_status
    finally:
        requests.delete(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)


def test_remove_nonexistent_product_from_wishlist(admin_header):
    customer = requests.post(f"{BASE_URL}/users", json={"name": "User", "email": "testnonexistentproduct@example.com", "role": "customer", "password": "1234567"}, headers=admin_header).json()
    try:
        response = requests.delete(f"{BASE_URL}/users/{customer['id']}/wishlist/12345?test_products=true", headers=admin_header)
        assert response.status_code == 404
    finally:
        requests.delete(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)


@pytest.mark.parametrize("user_id", [999999, 0])
def test_add_product_to_nonexistent_customer(user_id, admin_header):
    response = requests.post(
        f"{BASE_URL}/users/{user_id}/wishlist/1?test_products=true",
        headers=admin_header
    )
    assert response.status_code == 404


def test_get_user_unauthorized():
    # Try to access a protected endpoint without token
    response = requests.get(f"{BASE_URL}/users/1")
    assert response.status_code == 401


@pytest.mark.parametrize("payload, expected_status", [
    ({"name": ""}, 422),
    ({"email": "invalid-email"}, 422),
    ({"name": "New Name", "email": ""}, 422),
])
def test_update_customer_invalid_payload(payload, expected_status, admin_header):
    customer = requests.post(f"{BASE_URL}/users", json={"name": "User", "email": "updateinvalid@example.com", "role": "customer", "password": "1234567"}, headers=admin_header).json()
    try:
        response = requests.put(f"{BASE_URL}/users/{customer['id']}", json=payload, headers=admin_header)
        assert response.status_code == expected_status
    finally:
        requests.delete(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)


def test_get_empty_wishlist(admin_header):
    response = requests.post(f"{BASE_URL}/users", json={"name": "User", "email": "emptywishlist@example.com", "role": "customer", "password": "1234567"}, headers=admin_header)
    assert response.status_code == 201
    customer = response.json()
    try:
        response = requests.get(f"{BASE_URL}/users/{customer['id']}/wishlist?test_products=true", headers=admin_header)
        assert response.status_code == 200
        assert response.json() == []
    finally:
        requests.delete(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)


def test_cannot_access_deleted_customer(admin_header):
    response = requests.post(f"{BASE_URL}/users", json={"name": "User", "email": "deletedcustomer@example.com", "role": "customer", "password": "1234567"}, headers=admin_header)
    customer = response.json()

    del_response = requests.delete(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)
    assert del_response.status_code == 204

    response = requests.get(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)
    assert response.status_code == 404


def test_customer_cannot_update_another_customer(admin_header):
    email1 = "customer1@example.com"
    email2 = "customer2@example.com"

    cust1 = requests.post(f"{BASE_URL}/users", json={"name": "User1", "email": email1, "role": "customer", "password": "1234567"}, headers=admin_header).json()
    cust2 = requests.post(f"{BASE_URL}/users", json={"name": "User2", "email": email2, "role": "customer", "password": "1234567"}, headers=admin_header).json()
    token2_header = get_header_with_access_token(email2, "1234567")

    try:
        response = requests.put(
            f"{BASE_URL}/users/{cust1['id']}",
            json={"name": "ShouldFail", "email": "notallowed@example.com"},
            headers=token2_header
        )
        assert response.status_code == 403
    finally:
        requests.delete(f"{BASE_URL}/users/{cust1['id']}", headers=admin_header)
        requests.delete(f"{BASE_URL}/users/{cust2['id']}", headers=admin_header)

def test_add_product_to_wishlist_exceeding_limit(admin_header):
    response = requests.post(f"{BASE_URL}/users", json={
        "name": "Wishlist Limit",
        "email": "wishlistlimit@example.com",
        "role": "customer",
        "password": "1234567"
    }, headers=admin_header)
    assert response.status_code == 201
    customer = response.json()

    try:
        max_limit = 5
        for i in range(1, max_limit + 1):
            response = requests.post(
                f"{BASE_URL}/users/{customer['id']}/wishlist/{i}?test_products=true",
                headers=admin_header
            )
            assert response.status_code == 201

        response = requests.post(
            f"{BASE_URL}/users/{customer['id']}/wishlist/6?test_products=true",
            headers=admin_header
        )
        assert response.status_code == 400
        assert "limit" in response.text.lower()

    finally:
        requests.delete(f"{BASE_URL}/users/{customer['id']}", headers=admin_header)

