from datetime import date
import calendar
import sys
import os

# Allow import from current directory
sys.path.append(os.getcwd())

from main import get_past_months

def test_get_past_months():
    # Test 1: Simple case within same year
    ref_date = date(2025, 6, 15) # June 2025
    # Past 3 months: June, May, April. (If inclusive of current)
    # The logic was: start at current_m, loop count times.
    # Iter 1: June
    # Iter 2: May
    # Iter 3: April
    # Return reversed: April, May, June
    
    result = get_past_months(3, ref_date)
    expected = [
        ('April', 4, 2025),
        ('May', 5, 2025),
        ('June', 6, 2025)
    ]
    assert result == expected, f"Test 1 Failed: {result} != {expected}"
    print("Test 1 Passed")

    # Test 2: Year Rollover
    ref_date = date(2025, 2, 10) # Feb 2025
    # Past 3 months: Feb 2025, Jan 2025, Dec 2024
    # Reversed: Dec 2024, Jan 2025, Feb 2025
    
    result = get_past_months(3, ref_date)
    expected = [
        ('December', 12, 2024),
        ('January', 1, 2025),
        ('February', 2, 2025)
    ]
    assert result == expected, f"Test 2 Failed: {result} != {expected}"
    print("Test 2 Passed")

if __name__ == "__main__":
    try:
        test_get_past_months()
        print("All Unit Tests Passed")
    except Exception as e:
        print(f"Test Failed: {e}")
