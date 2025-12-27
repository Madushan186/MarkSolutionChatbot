import difflib

MONTHS = [
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december"
]

typos = ["octomber", "decamber", "janury", "februry", "mach"]

print("Testing Fuzzy Match:")
for typo in typos:
    # Cutoff 0.8 means 80% similarity required
    matches = difflib.get_close_matches(typo, MONTHS, n=1, cutoff=0.7)
    print(f"Input: {typo} -> Match: {matches}")
