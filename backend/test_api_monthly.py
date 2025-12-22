import requests
import json

def test_monthly_api():
    url = "https://api.emark.live/api/mobile/sales"
    headers = {"X-Forwarded-For": "144.76.94.137"}
    payload = {
        "db": "84",
        "br_id": "1",
        "year": "2025",
        "type": "monthly",
        "range": "12"
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        if response.status_code == 200:
            print("Status: 200 OK")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Status: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_monthly_api()
