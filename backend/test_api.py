import requests

def fetch_probe(label, use_multipart=False, use_json=False):
    url = "https://api.emark.live/api/mobile/sales"
    headers = {
        'X-Forwarded-For': '144.76.94.137',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    data = {
        'db': '84',
        'year': '2025',
        'range': '12', 
        'type': 'week' 
    }

    print(f"\n--- TESTING: {label} ---")
    try:
        if use_multipart:
             # Hack to force multipart without actual files
             # requests sends multipart if 'files' is provided.
             # We pass fields as (None, value) tuples.
             files = {k: (None, v) for k, v in data.items()}
             response = requests.post(url, headers=headers, files=files, timeout=10)
        elif use_json:
             response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
             # Default form-urlencoded
             response = requests.post(url, headers=headers, data=data, timeout=10)
             
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', '')}")
        print("Response Head (500 chars):")
        print(response.text[:500])
        
        try:
            print("JSON Parsed:", response.json())
        except:
            print("JSON Parse Failed.")
            
    except Exception as e:
        print(f"Error: {e}")

fetch_probe("Standard Form-Encoded")
fetch_probe("Multipart Form-Data", use_multipart=True)
fetch_probe("JSON Body", use_json=True)
