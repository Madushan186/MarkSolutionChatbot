import requests
import json
import time

API_URL = "http://localhost:8000/chat"

TEST_CASES = [
    {
        "name": "Single Branch Month",
        "msg": "Jan sales branch 1",
        "expect_keywords": ["42,242,986.69", "Branch 1"]
    },
    {
        "name": "Full Year Summary 2025",
        "msg": "full year summary for 2025 across all branches",
        "expect_keywords": ["Total", "2025", "Branch ALL"]
    },
    {
        "name": "Quarterly Analysis Q1",
        "msg": "Give me a summary of Branch 1 Q1 performance",
        "expect_keywords": ["Jan", "Feb", "Mar", "Total", "Q1"]
    },
    {
        "name": "Best Day Analytics",
        "msg": "Which day in June had highest sale for Branch 1?",
        "expect_keywords": ["highest", "sales day", "June", "2025"] 
    },
    {
        "name": "Full Company Aggregation",
        "msg": "Full company sales for Jan",
        "expect_keywords": ["Total", "sales"] 
    },
    {
        "name": "Multi-Branch Comparison",
        "msg": "Compare Branch 1 vs Branch 2 in Jan",
        "expect_keywords": ["compared to", "Branch"] 
    },
    {
        "name": "Branch Extraction List",
        "msg": "Branch 1 and 2",
        "expect_keywords": ["detected", "branches"] 
    },
    {
        "name": "Loop Fix Verification",
        "msg": "How much sale having in 2025 march month?",
        "follow_up": "1",
        "expect_keywords": ["2025", "Branch 1"]
        # Result might be "On 2025-03-01..." so "March" keyword might not appear if generated format differs.
    }
]

def run_test(case):
    print(f"🧪 Testing: {case['name']}")
    
    try:
        res = requests.post(API_URL, json={"message": case["msg"]}, timeout=60)
        data = res.json()
        ans = data.get("answer", "")
        print(f"   Input: '{case['msg']}'")
        print(f"   Output: '{ans}'")
        
        # Follow-up Logic
        if "follow_up" in case:
            if "which branch" in ans.lower():
                print(f"   ↪️ Sending Follow-up: '{case['follow_up']}'")
                res = requests.post(API_URL, json={"message": case["follow_up"]}, timeout=60)
                ans = res.json().get("answer", "")
                print(f"   Follow-up Output: '{ans}'")
            else:
                print("   ⚠️ Bot did not ask for clarification (unexpected).")
                # Continue to verify if it got the right answer anyway?
        
        # Check Expected Keywords (Final Answer)
        if case.get("expect_keywords"):
            for k in case["expect_keywords"]:
                if k.lower() not in ans.lower():
                    print(f"   ❌ Missing keyword: '{k}'")
                    return False
                
        print("   ✅ Passed")
        return True
        
    except Exception as e:
        print(f"   💥 Error: {e}")
        return False

print("--- RUNNING UNIT TEST SUITE ---")
passed = 0
for t in TEST_CASES:
    if run_test(t):
        passed += 1
    print("-" * 30)

print(f"🏁 Result: {passed}/{len(TEST_CASES)} Passed.")
