import requests
import json

url = "http://localhost:8000/chat"

def test_chat_query(message):
    print(f"\nQUERY: '{message}'")
    try:
        response = requests.post(url, json={"message": message}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"ANSWER: {data.get('answer')}")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test 1: Setup Context (Branch 1, Jan 2025)
    test_chat_query("Sales for Branch 1 in Jan 2025")
    
    # Test 2: Compare with Branch 2 (Triggers Comparison)
    # Then ask for PERCENTAGE difference (Should trigger new rule)
    test_chat_query("Percentage difference with Branch 2")
    
    # Test 3: Past N Months Context (Setup)
    test_chat_query("Sales for past 3 months Branch 1")
    
    # Test 4: Compare with Branch 2 + Percentage
    test_chat_query("Percentage difference with Branch 2")
    
    # Test 5: Negative Test (No Context)
    # Should be blocked by Guard
    test_chat_query("Percentage difference between Branch 1 and Branch 2")
