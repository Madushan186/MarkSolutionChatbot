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
    # Test 1: Priority Conflict Resolution
    # "Average sales for past 3 months in 2025" -> Should use Past 3 Months (49M) NOT Year Average (44M)
    test_chat_query("Average sales for past 3 months in 2025")
    
    # Test 2: Control Case (Year Only)
    test_chat_query("Average sales in 2025")
    
    # Test 3: Standard Past N Months
    test_chat_query("Average sales for past 3 months")
