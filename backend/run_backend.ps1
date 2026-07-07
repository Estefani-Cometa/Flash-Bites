# Script to run the backend with Python 3.12
py -3.12 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
