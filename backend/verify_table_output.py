import requests
import json

url = "http://localhost:8000/chat"

def test_chat_query(message):
    print(f"\nQUERY: '{message}'")
    try:
        response = requests.post(url, json={"message": message}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"ANSWER:\n{data.get('answer')}")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test 1: Past 3 Months (Should trigger Table)
    test_chat_query("Sales for past 3 months Branch 1")
    
    # Test 2: Past 1 Month (Should NOT trigger Table)
    test_chat_query("Sales for past 1 month Branch 1")
    
    # Test 3: Past 1 Month WITH keyword (Should trigger Table)
    test_chat_query("Sales for past 1 month Branch 1 as table")
