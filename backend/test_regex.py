import re
import calendar

MONTH_ALIASES = {
    "january": 1, "jan": 1, 
    "february": 2, "feb": 2, 
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8, 
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10, 
    "november": 11, "nov": 11, 
    "december": 12, "dec": 12
}

def extract_month_only(text):
    text = text.lower()
    print(f"Testing text: '{text}'")
    
    for m_name, m_num in MONTH_ALIASES.items():
        pattern = fr'\b{m_name}\b'
        match = re.search(pattern, text)
        if match:
            print(f"Matched '{m_name}' with pattern '{pattern}'")
            return calendar.month_name[m_num], m_num
            
    print("No match found")
    return None

msg = "how much sale having in 2025 march month? branch 1"
print(f"Result: {extract_month_only(msg)}")
