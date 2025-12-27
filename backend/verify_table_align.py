import requests
import json
import re

url = "http://localhost:8000/chat"

def query(message):
    print(f"\nQUERY: '{message}'")
    try:
        response = requests.post(url, json={"message": message}, timeout=10)
        return response.json().get('answer', '')
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    # Trigger Table
    res = query("Sales for past 3 months Branch 1")
    print("\n--- OUTPUT START ---")
    print(res)
    print("--- OUTPUT END ---\n")
    
    if "```" in res:
         print(" -> FAIL: Output contains forbidden markdown code blocks")
    else:
         print(" -> SUCCESS: Output is plain text (no markdown wrappers)")
    
    # Analysis
    # Check for Leading Spaces in row values
    # Regex: \|(\S.*)\|.*  (Start of cell, non-space char immediately)
    # Actually, Col 1 should be Left Aligned.
    # `|Value   |`
    # So `|` followed immediately by non-space?
    # User said: "NO leading spaces before cell values."
    # So `|October 2025` is EXPECTED. `| October 2025` is BAD.
    
    lines = res.split('\n')
    table_lines = [l for l in lines if '|' in l]
    
    if len(table_lines) > 0:
        row = table_lines[-3] # A data row (skipping separator? or last row?)
        # Let's check a data row specifically (contains digit and '|')
        data_rows = [l for l in table_lines if '202' in l and '|' in l] 
        if data_rows:
            sample = data_rows[0]
            print(f"Sample Row: '{sample}'")
            if sample.startswith('|') and sample[1] != ' ':
                print(" -> SUCCESS: No leading space in Col 1")
            else:
                print(f" -> CHECK: Col 1 starts with space? '{sample[1]}'")
                
            # Check Col 2 (Right Aligned)
            # Split by ` | `
            parts = sample.split(' | ')
            if len(parts) > 1:
                col2 = parts[1].strip('|') # Get Col 2 content
                # Right aligned means padding on LEFT.
                # So it SHOULD start with space if width > content
                print(f"Col 2 Raw: '{col2}'")
                if col2.startswith(' '):
                    print(" -> SUCCESS: Col 2 is padded (Right Aligned)")
                else:
                    print(" -> NOTE: Col 2 not padded (Content >= Width?)")
        else:
            print(" -> FAIL: No data rows found")
