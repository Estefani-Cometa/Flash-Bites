from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_list_products():
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "owner@example.com", "password": "secret123", "full_name": "Owner"},
    )
    assert register_response.status_code == 200
    data = register_response.json()
    assert "token" in data

    products_response = client.get("/api/v1/products")
    assert products_response.status_code == 200
    assert len(products_response.json()["items"]) >= 1


def test_create_order_requires_auth():
    response = client.post(
        "/api/v1/orders",
        json={"customer_id": "cust-1", "items": [{"product_id": "prod-1", "quantity": 2}]},
    )
    assert response.status_code == 401
