import re

def smart_merge(last_query, new_input):
    print(f"Old: '{last_query}'")
    print(f"New: '{new_input}'")
    
    merged_query = last_query
    
    # 1. Detect Year Change
    year_match = re.search(r'\b(202[0-9])\b', new_input)
    if year_match:
        new_year = year_match.group(1)
        # Replace existing year in old query, or append if missing
        if re.search(r'\b202[0-9]\b', merged_query):
            merged_query = re.sub(r'\b202[0-9]\b', new_year, merged_query)
        else:
            merged_query += f" {new_year}"
        print(f" -> Detected Year Update: {new_year}")

    # 2. Detect Branch Change
    branch_match = re.search(r'branch\s*(\d+)', new_input.lower())
    # Fallback: Detect isolated integer "2" or "what about 2" if it looks like a branch switch
    if not branch_match:
         # Check for simple integer or "about N" (Limit to 1-2 digits to avoid years like 2024)
         iso_match = re.search(r'(?:^|about\s+)(\d{1,2})(?:\s+|$|\?)', new_input.lower())
         if iso_match:
             potential_br = iso_match.group(1)
             # Heuristic: If we are in a comparison context (merged query has "Compare" or "Branch"), treat as branch
             if "branch" in merged_query.lower():
                 branch_match = iso_match # Reuse logic below

    if branch_match:
        new_br = branch_match.group(1)
        # Replace existing branch
        if re.search(r'branch\s*\d+', merged_query.lower()):
            merged_query = re.sub(r'branch\s*\d+', f"Branch {new_br}", merged_query, flags=re.IGNORECASE)
        else:
            merged_query += f" Branch {new_br}"
        print(f" -> Detected Branch Update: {new_br}")

    # 3. Detect Month Change (Simple Check against a list)
    # (Simplified for prototype)
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    new_month = None
    for m in months:
        if m in new_input.lower():
            new_month = m
            break
            
    if new_month:
        # Replace old month
        for old_m in months:
            if old_m in merged_query.lower():
                # Replace logic is tricky with regex, simpler to just append? 
                # Or replace the word.
                merged_query = re.sub(fr'\b{old_m}[a-z]*\b', new_month, merged_query, flags=re.IGNORECASE)
                break
        print(f" -> Detected Month Update: {new_month}")
                
    # 4. Detect Rolling Window (Past N Months)
    past_match = re.search(r'\b(?:past|last|previous)\s+(\d+)\s+months?\b', new_input.lower())
    if past_match:
         count = past_match.group(1)
         new_phrase = f"past {count} months"
         # Replace existing past N months
         if re.search(r'\b(?:past|last|previous)\s+\d+\s+months?\b', merged_query.lower()):
              merged_query = re.sub(r'\b(?:past|last|previous)\s+\d+\s+months?\b', new_phrase, merged_query, flags=re.IGNORECASE)
         else:
              merged_query += f" {new_phrase}"
         print(f" -> Detected Rolling Window Update: {new_phrase}")

    print(f"Result: '{merged_query}'\n")
    return merged_query

# Test Cases
print("--- TEST 1 ---")
smart_merge("Total sales in November Branch 1", "how about 2024?")

print("--- TEST 2 ---")
smart_merge("Total sales in November 2025 Branch 1", "what about branch 2?")

print("--- TEST 3 ---")
smart_merge("Sales in Jan 2025", "how about feb?")

print("--- TEST 4 (Complex) ---")
smart_merge("Total sales in November", "how about 2024? in branch 1?")
