import httpx
import time

BASE = 'http://127.0.0.1:8000'


def call(client, method, path, **kwargs):
    start = time.perf_counter()
    r = client.request(method, BASE + path, timeout=20.0, **kwargs)
    elapsed = (time.perf_counter() - start) * 1000
    print(f"{method} {path} -> {r.status_code} time_ms={elapsed:.1f}")
    try:
        print(r.json())
    except Exception:
        print(r.text[:200])
    return r


def main():
    with httpx.Client() as client:
        # register
        r = call(client, 'POST', '/api/v1/auth/register', json={'email': 'e2e@example.com','password':'e2e12345','full_name':'E2E Tester'})
        token = r.json().get('token') if r.status_code in (200,201) else None
        if not token:
            raise RuntimeError('Registration did not return a valid JWT')

        headers = {'Authorization': f'Bearer {token}'}

        # create customer
        r = call(client, 'POST', '/api/v1/customers', json={'name':'Cliente E2E','email':'cliente@example.com','phone': '555-0101'}, headers=headers)
        if r.status_code not in (200,201):
            raise RuntimeError(f'Customer creation failed: {r.text}')
        customer = r.json()

        # list products
        r = call(client, 'GET', '/api/v1/products')
        if r.status_code != 200:
            raise RuntimeError(f'Product listing failed: {r.text}')
        items = r.json().get('items', [])
        if not items or not items[0].get('id'):
            raise RuntimeError('Product listing returned no valid product ID')
        product_id = items[0]['id']

        # chat
        call(client, 'POST', '/api/v1/chat', json={'message':'Hola, muéstrame productos'}, headers=headers)

        # create order
        payload = {'customer_id': customer['id'], 'items':[{'product_id': product_id, 'quantity':1}]}
        order = call(client, 'POST', '/api/v1/orders', json=payload, headers=headers)
        if order.status_code != 201:
            raise RuntimeError(f'Order creation failed: {order.text}')


if __name__ == '__main__':
    main()
