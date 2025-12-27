import requests
import json

url = "http://localhost:8000/chat"

def test_chat_query(message):
    print(f"\nQUERY: '{message}'")
    try:
        response = requests.post(url, json={"message": message}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"ANSWER: {data.get('answer')}")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    # Test 1: Percentage Guard (Ambiguous Branch vs Branch)
    # "Percentage diff between Branch 1 and Branch 2" -> Should ASK FOR BASELINE
    test_chat_query("Percentage difference between Branch 1 and Branch 2")

    # Test 2: Percentage Guard (With Date Context)
    # "Percentage diff between Branch 1 and Branch 2 in Jan 2025" -> Should ASK FOR BASELINE
    test_chat_query("Percentage difference between Branch 1 and Branch 2 in Jan 2025")
    
    # Test 3: Context Stability (Rolling Window)
    # Step A: "Sales past 3 months" (Set 3 months)
    test_chat_query("Sales past 3 months")
    # Step B: "past 3 months" (Repeat/Reinforce) -> Should NOT reset context or fail
    test_chat_query("past 3 months")
