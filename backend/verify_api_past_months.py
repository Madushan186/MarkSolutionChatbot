import requests
import json

url = "http://localhost:8000/chat"

def test_chat_query(message):
    print(f"Sending: '{message}'")
    try:
        response = requests.post(url, json={"message": message})
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return data
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test 1: Past 3 Months
    test_chat_query("What are the sales for the past 3 months?")
