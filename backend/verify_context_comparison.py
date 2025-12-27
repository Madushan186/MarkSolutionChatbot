import requests
import json

url = "http://localhost:8000/chat"

def test_chat_query(message):
    print(f"\nQUERY: '{message}'")
    try:
        response = requests.post(url, json={"message": message})
        if response.status_code == 200:
            data = response.json()
            print(f"ANSWER: {data.get('answer')}")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test 1: Establish Context
    # "Sales for Branch 1 in Jan 2025"
    test_chat_query("Sales for Branch 1 in Jan 2025")
    
    # Test 2: Follow-up Comparison (Infer Branch 1 + Jan 2025)
    # "Compare with Branch 2" -> Should compare Branch 1 (context) vs Branch 2 (explicit) in Jan 2025 (context)
    test_chat_query("Compare with Branch 2")
    
    # Test 3: Follow-up Percentage Comparison (Infer Branch 1 + Jan 2025)
    # "Percentage diff with Branch 2" -> Should calculate % diff
    test_chat_query("Percentage difference with Branch 3")
