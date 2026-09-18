import httpx

def main():
    r = httpx.get('http://127.0.0.1:8000/openapi.json', timeout=10.0)
    if r.status_code != 200:
        print('openapi not available', r.status_code)
        return
    data = r.json()
    for p in sorted(data.get('paths', {}).keys()):
        print(p)

if __name__ == '__main__':
    main()
