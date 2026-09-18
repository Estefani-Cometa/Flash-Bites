import os
import httpx


BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000")


def main():
    with httpx.Client() as client:
        def expect(response, expected, path):
            if response.status_code != expected:
                raise RuntimeError(f"{path}: esperaba {expected}, recibió {response.status_code}: {response.text}")
            return response

        expect(client.get(BASE_URL + "/health", timeout=10), 200, "/health")
        register = expect(client.post(BASE_URL + "/api/v1/auth/register", json={"email": "smoke@example.com", "password": "smoke1234", "full_name": "Smoke Tester"}, timeout=10), 200, "/auth/register")
        token = register.json().get("token")
        if not token:
            raise RuntimeError("/auth/register no devolvió un JWT válido")
        headers = {"Authorization": f"Bearer {token}"}
        products = expect(client.get(BASE_URL + "/api/v1/products", timeout=10), 200, "/products").json().get("items", [])
        if not products or not products[0].get("id"):
            raise RuntimeError("/products no devolvió productos con ID")
        customer = expect(client.post(BASE_URL + "/api/v1/customers", headers=headers, json={"name": "Smoke Customer", "email": "smoke-customer@example.com"}, timeout=10), 201, "/customers").json()
        order = expect(client.post(BASE_URL + "/api/v1/orders", headers=headers, json={"customer_id": customer["id"], "items": [{"product_id": products[0]["id"], "quantity": 1}]}, timeout=10), 201, "/orders")
        expect(client.post(BASE_URL + "/api/v1/chat", headers=headers, json={"message": "Hola"}, timeout=20), 200, "/chat")
        print(f"SMOKE TEST OK: {order.json()['id']} con producto {products[0]['id']}")


if __name__ == "__main__":
    main()
