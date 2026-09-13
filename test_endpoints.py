import requests

print("Testing /api/v1/classify-text")
try:
    resp = requests.post(
        "http://127.0.0.1:8000/api/v1/classify-text", 
        json={"text": "play some music"},
        timeout=10
    )
    print("Status:", resp.status_code)
    print("Response:", resp.json())
except Exception as e:
    print("Error:", e)

print("\nTesting /api/v1/classify-audio with missing file")
try:
    resp2 = requests.post(
        "http://127.0.0.1:8000/api/v1/classify-audio",
        timeout=10
    )
    print("Status:", resp2.status_code)
    print("Response:", resp2.json())
except Exception as e:
    print("Error:", e)
