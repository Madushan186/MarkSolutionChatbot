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
    # Test 1: Absolute Average (Should work)
    test_chat_query("Average sales in 2025")
    
    # Test 2: Ambiguous Percentage (Should ask for clarification)
    test_chat_query("What is the average percentage growth?")
    
    # Test 3: Ambiguous Percentage (Should ask for clarification)
    test_chat_query("percentage increase")
    
    # Test 4: Valid Percentage (Should work)
    test_chat_query("Percentage growth between 2024 and 2025")
