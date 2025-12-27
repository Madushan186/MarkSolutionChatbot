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
    # Test 1: Average Monthly Sales (Year Context)
    test_chat_query("What is the average sales in 2025?")
    
    # Test 2: Average Monthly Sales (Past N Months Context)
    # This failed before because "Total" logic caught it. Should now return Average.
    test_chat_query("Average sales for past 3 months")
    
    # Test 3: Year vs Year with Percentage
    # Added "Branch 1" to pass Strict Branch Guard
    test_chat_query("Compare sales 2024 and 2025 for Branch 1")
    
    # Test 4: Month vs Month with Percentage
    # Added "Branch 1"
    test_chat_query("Compare November and December for Branch 1")
