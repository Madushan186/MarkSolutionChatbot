import requests
import json
import re

url = "http://localhost:8000/chat"

def query(message):
    print(f"\nQUERY: '{message}'")
    try:
        response = requests.post(url, json={"message": message}, timeout=10)
        if response.status_code != 200:
             return f"Error {response.status_code}: {response.text}"
        return response.json().get('answer', '')
    except Exception as e:
        return f"Exception: {e}"

if __name__ == "__main__":
    # Test 1: Setup Comparison (Year vs Year)
    ans1 = query("Compare 2024 and 2025 Branch 1")
    print(f"ANSWER 1: {ans1}")
    
    # Check if correct comparison
    if "2024" in ans1 and "2025" in ans1 and "Branch 1" in ans1:
        print(" -> SUCCESS: Initial Context Set")
    else:
        print(" -> FAIL: Initial Context Missing")

    # Test 2: Switch Branch with isolated integer
    ans2 = query("2")
    print(f"ANSWER 2: {ans2}")
    
    # Check if it maintained Year comparison
    if "2024" in ans2 and "2025" in ans2 and "Branch 2" in ans2:
        print(" -> SUCCESS: Context Maintained & Branch Switched")
    else:
        print(" -> FAIL: Context Lost or Branch Logic Failed")
        
    # Test 3: Switch Branch with "Branch 3"
    ans3 = query("Branch 3")
    print(f"ANSWER 3: {ans3}")
    if "2024" in ans3 and "2025" in ans3 and "Branch 3" in ans3:
        print(" -> SUCCESS: Context Maintained & Branch Switched (Explicit)")
