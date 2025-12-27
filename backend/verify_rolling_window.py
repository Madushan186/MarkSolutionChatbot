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
    # Test 1: Explicit Rolling Window Comparison
    # "Compare Branch 1 and Branch 2 for past 3 months"
    test_chat_query("Compare Branch 1 and Branch 2 for past 3 months")
    
    # Test 2: Inferred Rolling Window Context
    # Step A: "Sales Branch 1 past 3 months" (Set Context)
    test_chat_query("Sales Branch 1 past 3 months")
    # Step B: "Compare with Branch 2" (Infer "past 3 months")
    test_chat_query("Compare with Branch 2")
