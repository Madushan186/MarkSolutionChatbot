from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import re
import sqlite3
import json
import calendar
import difflib # ADDED for fuzzy matching
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()
# Force Reload Fix

# ===============================
# APP SETUP
# ===============================
app = FastAPI(
    title="Mr. Mark Financial Assistant",
    description="Internal Financial Assistant for Mr. Mark",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# CONFIG
# ===============================
# ===============================
DB_NAME = "sales.db"

def log_query(query, intent, response):
    try:
        conn = sqlite3.connect(DB_NAME)
        # Lazy Table Creation (Safe & Simple)
        conn.execute('''CREATE TABLE IF NOT EXISTS query_logs
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                         user_query TEXT,
                         intent TEXT,
                         response_text TEXT)''')
        conn.execute("INSERT INTO query_logs (user_query, intent, response_text) VALUES (?, ?, ?)",
                     (query, intent, str(response)))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Log Error: {e}")

class ChatRequest(BaseModel):
    message: str

# Context Store
PENDING_CONTEXT = {
    "query": None
}

# ===============================
# HELPERS: DATABASE
# ===============================
def get_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        return conn
    except Exception as e:
        print(f"❌ Database Connection Error: {e}")
        return None

def fetch_from_db(date_str, br_id=1):
    conn = get_db()
    if not conn: return None
    try:
        cur = conn.cursor()
        if br_id == 'ALL':
             query = "SELECT SUM(amount) FROM sales WHERE sale_date = ?"
             cur.execute(query, (date_str,))
        else:
             query = "SELECT amount FROM sales WHERE sale_date = ? AND br_id = ?"
             cur.execute(query, (date_str, br_id))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return float(row[0]) if row and row[0] is not None else None
    except Exception as e:
        print(f"❌ DB Fetch Error: {e}")
        return None

def fetch_monthly_sum_from_db(year, month_num, br_id=1):
    conn = get_db()
    if not conn: return 0.0
    try:
        _, last_day = calendar.monthrange(year, month_num)
        start_date = f"{year}-{month_num:02d}-01"
        end_date = f"{year}-{month_num:02d}-{last_day}"
        cur = conn.cursor()
        
        if br_id == 'ALL':
            query = "SELECT SUM(amount) FROM sales WHERE sale_date >= ? AND sale_date <= ?"
            cur.execute(query, (start_date, end_date))
        else:
            query = "SELECT SUM(amount) FROM sales WHERE sale_date >= ? AND sale_date <= ? AND br_id = ?"
            cur.execute(query, (start_date, end_date, br_id))
        
        row = cur.fetchone()
        cur.close()
        conn.close()
        return float(row[0]) if row and row[0] is not None else 0.0
    except Exception:
        return 0.0

def fetch_monthly_average(year, month_num, br_id=1):
    conn = get_db()
    if not conn: return None
    try:
        cur = conn.cursor()
        if br_id == 'ALL':
             query = """
                 SELECT AVG(daily_total) 
                 FROM (
                     SELECT sale_date, SUM(amount) as daily_total 
                     FROM sales 
                     WHERE strftime('%Y', sale_date) = ? 
                     AND strftime('%m', sale_date) = ?
                     GROUP BY sale_date
                 ) sub
             """
             cur.execute(query, (str(year), f"{month_num:02d}"))
        else:
             query = "SELECT AVG(amount) FROM sales WHERE strftime('%Y', sale_date)=? AND strftime('%m', sale_date)=? AND br_id=?"
             cur.execute(query, (str(year), f"{month_num:02d}", br_id))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return float(row[0]) if row and row[0] is not None else None
    except Exception:
        return None

def fetch_year_total(year, br_id=1):
    conn = get_db()
    if not conn: return None
    try:
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        cur = conn.cursor()
        if br_id == 'ALL':
            query = "SELECT SUM(amount) FROM sales WHERE sale_date >= ? AND sale_date <= ?"
            cur.execute(query, (start_date, end_date))
        else:
            query = "SELECT SUM(amount) FROM sales WHERE sale_date >= ? AND sale_date <= ? AND br_id = ?"
            cur.execute(query, (start_date, end_date, br_id))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return float(row[0]) if row and row[0] is not None else 0.0
    except Exception:
        return None

def find_extreme_month(year=2025, mode='max', br_id=1):
    conn = get_db()
    if not conn: return None, 0.0
    try:
        cur = conn.cursor()
        order = "DESC" if mode == 'max' else "ASC"
        if br_id == 'ALL':
             query = f"SELECT strftime('%m', sale_date) as m, SUM(amount) as total FROM sales WHERE strftime('%Y', sale_date) = ? GROUP BY m ORDER BY total {order} LIMIT 1"
             cur.execute(query, (str(year),))
        else:
             query = f"SELECT strftime('%m', sale_date) as m, SUM(amount) as total FROM sales WHERE strftime('%Y', sale_date) = ? AND br_id = ? GROUP BY m ORDER BY total {order} LIMIT 1"
             cur.execute(query, (str(year), br_id))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            m_num = int(row[0])
            total = float(row[1])
            return calendar.month_name[m_num], total
        return None, 0.0
    except Exception:
        return None, 0.0

def find_extreme_day_in_month(year, month_num, br_id=1, mode="MAX"):
    conn = get_db()
    if not conn: return None, 0.0
    try:
        cur = conn.cursor()
        order = "DESC" if mode == "MAX" else "ASC"
        if br_id == 'ALL':
             query = f"SELECT sale_date, SUM(amount) as total FROM sales WHERE strftime('%Y', sale_date) = ? AND strftime('%m', sale_date) = ? GROUP BY sale_date ORDER BY total {order} LIMIT 1"
             cur.execute(query, (str(year), f"{month_num:02d}"))
        else:
             query = f"SELECT sale_date, amount FROM sales WHERE strftime('%Y', sale_date) = ? AND strftime('%m', sale_date) = ? AND br_id = ? ORDER BY amount {order} LIMIT 1"
             cur.execute(query, (str(year), f"{month_num:02d}", br_id))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return row[0], float(row[1])
        return None, 0.0
    except Exception:
        return None, 0.0

# ===============================
# HELPERS: ERP API
# ===============================
def fetch_live_sales(period="day", year="2025", br_id=1):
    url = "https://api.emark.live/api/mobile/sales"
    headers = {"X-Forwarded-For": "144.76.94.137"}
    payload = {"db": "84", "br_id": str(br_id), "year": year, "type": "daily", "range": "1"}
    
    if period == "month":
        payload["type"] = "monthly"
        payload["range"] = "1"
        
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "data" in data and isinstance(data["data"], list):
                today_str = datetime.now().strftime("%Y-%m-%d")
                total = 0.0
                for row in data["data"]:
                    if row.get("period") == today_str:
                         total += float(row.get("total_sales", row.get("total_sale", 0)))
                return {"total": total}
        return {"total": 0, "error": "Invalid ERP Response"}
    except Exception as e:
        return {"total": 0, "error": str(e)}

# ===============================
# HELPERS: EXTRACTORS
# ===============================
MONTH_ALIASES = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "september": 9, "sept": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
    "decamber": 12, # Common Typo Support
    "this month": datetime.now().month,
    "current month": datetime.now().month
}

def fuzzy_correct_months(text):
    # Handle "this month" / "current month" replacement first
    lower_text = text.lower()
    if "this month" in lower_text or "current month" in lower_text:
         # We rely on extract_month_only to catch these specific keys in MONTH_ALIASES
         pass
    
    words = text.split()
    corrected_words = []
    known_months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
    
    for word in words:
        clean_word = word.lower().strip(",.?!")
        # specific check to avoid short word confusion
        if len(clean_word) < 4: 
            corrected_words.append(word)
            continue
            
        matches = difflib.get_close_matches(clean_word, known_months, n=1, cutoff=0.7)
        if matches:
            # maintain case/punctuation? No, simplify to lowercase month
            corrected_words.append(matches[0])
        else:
            corrected_words.append(word)
            
    return " ".join(corrected_words)

def extract_branch(text):
    match = re.search(r'branch\s*(\d+)', text.lower())
    return int(match.group(1)) if match else None

def extract_all_branches(text):
    text = text.lower()
    matches = re.findall(r'branch\s*(\d+)', text)
    ids = [int(m) for m in matches]
    multi_match = re.search(r'branch\s+(\d+)\s*(?:vs|and|&|,)\s*(\d+)', text)
    if multi_match:
         ids.append(int(multi_match.group(1)))
         ids.append(int(multi_match.group(2)))
    return sorted(list(set(ids)))

def extract_date(text):
    text = text.lower()
    # Fixed Offset for IST (UTC+5:30)
    ist_offset = timedelta(hours=5, minutes=30)
    now_ist = datetime.utcnow() + ist_offset
    
    if "yesterday" in text:
        return (now_ist - timedelta(days=1)).strftime("%Y-%m-%d")
    if "today" in text:
        return now_ist.strftime("%Y-%m-%d")
    match_iso = re.search(r'\d{4}-\d{2}-\d{2}', text)
    if match_iso:
        print(f"DEBUG: Extracted Date (ISO): {match_iso.group(0)}")
        return match_iso.group(0)
    # Dynamic Year Extraction
    target_year = extract_year(text)
    
    for m_name, m_num in MONTH_ALIASES.items():
        if len(m_name) < 3: continue 
        # Regex: Month followed strictly by a number (Day), allowing for "st/nd/rd/th" 
        # and optional "the" or whitespace.
        # e.g. "January 5th", "Jan 05", "Jan the 5th"
        # We start with strict check to avoid 'July 2024' being parsed as Day 2024.
        
        matches = re.finditer(fr'\b{m_name}\b\s*(?:the\s*)?(\d+)(st|nd|rd|th)?\b', text)
        for match in matches:
            if text[:match.start(1)].strip().lower().endswith("branch"): continue
            day = int(match.group(1))
            
            # Sanity Check: Day must be valid
            if 1 <= day <= 31:
                try:
                    # Validate valid date (e.g. Feb 30 check)
                    test_date = date(target_year, m_num, day)
                    return test_date.strftime("%Y-%m-%d")
                except ValueError:
                    continue # Invalid date (e.g. Feb 30)

    # Reverse format: "5th of January"
    matches = re.finditer(r'\b(\d+)(st|nd|rd|th)?\s+(?:of\s+)?([a-zA-Z]+)\b', text)
    for match in matches:
        day = int(match.group(1))
        m_name_can = match.group(3).lower()
        if 1 <= day <= 31 and m_name_can in MONTH_ALIASES:
             m_num = MONTH_ALIASES[m_name_can]
             try:
                 test_date = date(target_year, m_num, day)
                 return test_date.strftime("%Y-%m-%d")
             except ValueError:
                 continue

    return None

def extract_month_only(text):
    text = text.lower()
    # Explicit check for phrases first
    if "this month" in text or "current month" in text:
        return calendar.month_name[datetime.now().month], datetime.now().month
        
    for m_name, m_num in MONTH_ALIASES.items():
        if re.search(fr'\b{m_name}\b', text):
             return calendar.month_name[m_num], m_num
    return None

def extract_all_months(text):
    text = text.lower()
    found = []
    seen = set()
    for m_name, m_num in MONTH_ALIASES.items():
        if m_num in seen: continue
        if re.search(fr'\b{m_name}\b', text):
            found.append((calendar.month_name[m_num], m_num))
            seen.add(m_num)
    found.sort(key=lambda x: x[1])
    return found

def extract_two_months(text):
    data = extract_all_months(text)
    return [data[0], data[1]] if len(data) >= 2 else None

def get_past_months(count, ref_date=None):
    if ref_date is None: ref_date = date(2025, 12, 22)
    result = []
    current_m = ref_date.month
    for _ in range(count):
        result.append((calendar.month_name[current_m], current_m))
        current_m -= 1
        if current_m < 1: current_m = 12
    return result[::-1]

def extract_quarter(text):
    match = re.search(r'\bq([1-4])\b', text.lower())
    if not match: match = re.search(r'quarter\s*([1-4])', text.lower())
    return int(match.group(1)) if match else None

def extract_goal_amount(text):
    match = re.search(r'(?:goal|target|aim).*?(\d+(?:,\d{3})*(?:\.\d+)?)\s*(m|k|million|thousand)?', text.lower())
    if match:
        val = float(match.group(1).replace(',', ''))
        mult = match.group(2)
        if mult in ['m', 'million']: val *= 1_000_000
        elif mult in ['k', 'thousand']: val *= 1_000
        return val
    return None

def extract_year(text):
    match = re.search(r'\b(202[0-9])\b', text)
    if match:
        return int(match.group(1))
    return 2025 # Default

# ===============================
# HELPERS: OLLAMA
# ===============================
def call_ollama(prompt, model="tinyllama"):
    # Change to localhost for local run
    url = "http://localhost:11434/api/generate"
    try:
        resp = requests.post(url, json={"model": model, "prompt": prompt, "stream": False}, timeout=60)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"⚠️ Ollama Error: {e}")
        return "I'm having trouble thinking right now. Please try again."

def generate_smart_response(data_text, user_question):
    # Deterministic Response - Fast & Accurate
    log_query(user_question, "Financial Query", data_text)
    return {"answer": data_text}
    
    # Strict prompt for TinyLlama completion
    prompt = f"""Data: {data_text}
Question: {user_question}
Task: Write a single sentence answering the question using the data.
Answer: The total"""
    
    llm = call_ollama(prompt, model="tinyllama")
    if "I'm having trouble" in llm: return {"answer": f"{data_text} (AI Explanation Unavailable)"}
    
    # Prepend the start of the sentence
    full_answer = f"The total {llm}"
    return {"answer": full_answer}

# ===============================
# MAIN API
# ===============================
@app.get("/")
def read_root():
    conn = get_db()
    status = "Connected to DB ✅" if conn else "DB Connection Failed ❌"
    if conn: conn.close()
    return {"status":"Mr. Mark (Legacy Monolith restored) 🚀", "db_status": status}

def merge_context(last_query, new_input):
    if not last_query: return new_input
    
    merged_query = last_query
    
    # 1. Detect Year Change
    year_match = re.search(r'\b(202[0-9])\b', new_input)
    if year_match:
        new_year = year_match.group(1)
        if re.search(r'\b202[0-9]\b', merged_query):
            merged_query = re.sub(r'\b202[0-9]\b', new_year, merged_query)
        else:
            merged_query += f" {new_year}"

    # 2. Detect Branch Change
    branch_match = re.search(r'branch\s*(\d+)', new_input.lower())
    if branch_match:
        new_br = branch_match.group(1)
        if re.search(r'branch\s*\d+', merged_query.lower()):
            merged_query = re.sub(r'branch\s*\d+', f"Branch {new_br}", merged_query, flags=re.IGNORECASE)
        else:
            merged_query += f" Branch {new_br}"

    # 3. Detect Month Change (if simple single month)
    m_info = extract_month_only(new_input)
    if m_info:
        new_month_name = m_info[0] # e.g. "June"
        # Try to find and replace existing month in query
        all_months_in_last = extract_all_months(merged_query)
        if all_months_in_last:
             # Heuristic: Replace the first found month ?? 
             # Or regex replace the word.
             old_m_name = all_months_in_last[0][0] # "November"
             # Regex replace
             merged_query = re.sub(fr'\b{old_m_name}\b', new_month_name, merged_query, flags=re.IGNORECASE)
        else:
             merged_query += f" {new_month_name}"

    return merged_query

# Global Context stores
PENDING_CONTEXT = {"query": None}
LAST_SUCCESSFUL_QUERY = {"text": None}
LAST_ATTEMPTED_QUERY = {"text": None} # For clarification loops

def generate_clarification_response(user_msg):
    # Prompt the AI to ask a helpful follow-up question
    prompt = f"""You are Mr. Mark. The user asked: "{user_msg}".
    You cannot answer because the query is missing specific details (like Year, Month, or Branch) or is not about Sales.
    If the user's input is just a number (e.g. "1"), treat it as a Branch selection.
    Task: politely ask the user to provide the missing details (e.g. "Which branch?").
    Answer:"""
    
    llm = call_ollama(prompt, model="tinyllama")
    if "request failed" in llm.lower() or not llm:
        return {"answer": "I'm not exactly sure what you mean. Could you specify a Year, Month, and Branch?"}
    return {"answer": llm}

@app.get("/suggestions")
def get_suggestions():
    conn = get_db()
    if not conn:
        return {"suggestions": []}
    
    try:
        cur = conn.cursor()
        
        # 1. Get Years
        cur.execute("SELECT DISTINCT strftime('%Y', sale_date) FROM sales ORDER BY 1 DESC")
        years = [row[0] for row in cur.fetchall()]
        current_year = years[0] if years else "2025"
        prev_year = years[1] if len(years) > 1 else str(int(current_year)-1)
        
        # 2. Get Branches
        cur.execute("SELECT DISTINCT br_id FROM sales ORDER BY br_id")
        branches = [row[0] for row in cur.fetchall()]
        
        # 3. Find Most Active Branch (Heuristic)
        cur.execute("SELECT br_id, COUNT(*) as c FROM sales GROUP BY br_id ORDER BY c DESC LIMIT 1")
        top_row = cur.fetchone()
        top_branch = top_row[0] if top_row else (branches[0] if branches else 1)
        
        cur.close()
        conn.close()
        
        # 4. Generate Suggestions
        suggestions = {
            "Branch Insights": [
                f"Sales of Branch {top_branch} today",
                "Which branch has the highest sales this month?",
                "Lowest performing branch this year"
            ]
        }
        
        return suggestions
        
    except Exception as e:
        print(f"Suggestion Error: {e}")
        return {"suggestions": []}

@app.post("/chat")
def chat_implementation(req: ChatRequest):
    user_msg_raw = req.message.strip()
    user_msg = fuzzy_correct_months(user_msg_raw) # Autocorrect typos
    
    # Reset attempted query for this new request (will act as 'buffer' if we fail later)
    # Actually no, we need to READ it first, then overwrite it at end?
    # No, we read it to MERGE.
    
    target_year = extract_year(user_msg)
    
    # 1. Context Merge
    branch_match = re.match(r'^(branch\s*)?(\d+)$', user_msg.lower())
    
    # Scenario A: Pending "Which branch?" Question (Highest Priority)
    if branch_match and PENDING_CONTEXT.get("query"):
        user_msg = f"{PENDING_CONTEXT['query']} Branch {branch_match.group(2)}"
        PENDING_CONTEXT["query"] = None
        target_year = extract_year(user_msg)
        print(f"DEBUG: Merged Pending: {user_msg}")
        # Clear Attempted since we resolved it
        LAST_ATTEMPTED_QUERY["text"] = None
        
    # Scenario B: Smart Context Memory (Follow-ups)
    # Check LAST_ATTEMPTED first (it's the most recent unfinished business)
    # Then check LAST_SUCCESSFUL
    base_context = LAST_ATTEMPTED_QUERY.get("text") or LAST_SUCCESSFUL_QUERY.get("text")
    
    if base_context:
        # Check for keywords that imply a TOTALLY NEW query
        force_new_keywords = ["compare", "vs", "goal", "average", "summary", "analysis", "sales", "sale", "total"]
        # If user repeats a main keyword, likely a new query.
        matches_keyword = any(k in user_msg.lower() for k in force_new_keywords)
        
        # But wait, "Sales in June?" has "sales". It might be a correction of "Sales in July".
        # If I say "Sales in July" (Failed) -> "Sales in June" (Correction).
        # Merging "Sales in July" + "Sales in June" -> Messy.
        # merge_context handles replacement.
        
        if matches_keyword:
            print("DEBUG: Force New Query Detected. Skipping Merge.")
            merged = user_msg
        else:
             merged = merge_context(base_context, user_msg)
        
        if merged != base_context:
             # If `merged` absorbed the user input, we use it.
             # E.g. Base="Sales Branch 1", User="June". Merged="Sales Branch 1 June".
             user_msg = merged
             target_year = extract_year(user_msg)
             print(f"DEBUG: Smart Merged (Base='{base_context}'): {user_msg}")
        
    # 2. Branch ID Extraction
    br_id = None
    if any(k in user_msg.lower() for k in ["full company", "all branches"]):
        br_id = "ALL"
    else:
        br_id = extract_branch(user_msg)
        
    # 3. Branch Guard & Defaults
    if br_id is None:
         # A. Comparison -> strict block (User must specify branches)
        if any(k in user_msg.lower() for k in ["compare", "vs"]):
             PENDING_CONTEXT["query"] = user_msg # SAVE CONTEXT
             return {"answer": "Which branches would you like to compare?"}
        
        # B. Defaulting Logic (Override: Sales/Date queries -> Default to Branch 1)
        fin_keys = ["goal", "sales", "sale", "highest", "lowest", "average", "total", "year", "quarter"]
        # Check for Month (e.g. "June") or Date "2024-05-01" or Year "2024"
        is_relevant = any(k in user_msg.lower() for k in fin_keys) or extract_date(user_msg) or extract_month_only(user_msg) or extract_year(user_msg) != 2025
        
        if is_relevant:
            print("DEBUG: Auto-defaulting to Branch 1")
            br_id = 1
        else:
            # If no financial context found, we might ask clarification logic later
            # OR we can return a generic "Which branch?" if we are sure it was a query attempt.
            # Existing logic was stricter. Let's keep strictness for "ambiguous" queries.
            if any(k in user_msg.lower() for k in fin_keys): 
                # Should have been caught by is_relevant, so this is redundant but safe.
                pass 
            # If completely irrelevant (e.g. "hi"), we fall through to Greeting.

    # Clear pending if we resolved (or defaulted) a branch
    if br_id is not None:
         PENDING_CONTEXT["query"] = None

    if br_id is None:
        br_label = "Branch 1" # Fallback for display if we missed it?
    elif br_id == "ALL":
        br_label = "All Branches"
    else:
        br_label = f"Branch {br_id}"

    # Best Branch (High Priority)
    if "branch" in user_msg.lower() and any(k in user_msg.lower() for k in ["highest", "best", "top", "lowest", "worst"]):
        mode = "ASC" if any(k in user_msg.lower() for k in ["lowest", "worst"]) else "DESC"
        m_info = extract_month_only(user_msg)
        target_month = m_info[1] if m_info else 0 # 0 = Year Total
        
        # We need a new helper or ad-hoc query
        conn = get_db()
        if conn:
            cur = conn.cursor()
            if target_month > 0:
                # Best Branch in Month
                query = f"SELECT br_id, SUM(amount) as total FROM sales WHERE strftime('%Y', sale_date)=? AND strftime('%m', sale_date)=? GROUP BY br_id ORDER BY total {mode} LIMIT 1"
                cur.execute(query, (str(target_year), f"{target_month:02d}"))
                lbl = f"{m_info[0]} {target_year}"
            else:
                # Best Branch in Year
                query = f"SELECT br_id, SUM(amount) as total FROM sales WHERE strftime('%Y', sale_date)=? GROUP BY br_id ORDER BY total {mode} LIMIT 1"
                cur.execute(query, (str(target_year),))
                lbl = f"{target_year}"
                
            row = cur.fetchone()
            cur.close()
            conn.close()
            
            if row:
                return generate_smart_response(f"The {'best' if mode=='DESC' else 'lowest'} performing branch in {lbl} is Branch {row[0]} with sales of {row[1]:,.2f} LKR.", user_msg)
            return {"answer": f"No data found to determine the best branch in {lbl}."}

    # Greeting
    if user_msg.lower() in ["hi", "hello"]:
        return {"answer": "Hello! I am Mr. Mark."}

    # 4. Priority Ladder
    
    # Goal
    if "goal" in user_msg.lower():
        target = extract_goal_amount(user_msg)
        if target:
            LAST_SUCCESSFUL_QUERY["text"] = user_msg # Save Context
            ytd = fetch_year_total(target_year, br_id) or 0.0
            diff = ytd - target
            ctx = f"Goal: {target:,.2f} LKR for {br_label}. YTD ({target_year}): {ytd:,.2f} LKR. Surplus: {diff:,.2f} LKR" if diff >= 0 else f"Goal: {target:,.2f} LKR for {br_label}. Need {abs(diff):,.2f} LKR more. YTD ({target_year}): {ytd:,.2f} LKR"
            return generate_smart_response(ctx, user_msg)

    # Quarterly
    q_num = extract_quarter(user_msg)
    if q_num:
        LAST_SUCCESSFUL_QUERY["text"] = user_msg # Save Context
        q_map = {1:["Jan","Feb","Mar"], 2:["Apr","May","Jun"], 3:["Jul","Aug","Sep"], 4:["Oct","Nov","Dec"]}
        months = q_map.get(q_num, [])
        total = 0.0
        parts = []
        for m in months:
            val = fetch_monthly_sum_from_db(target_year, MONTH_ALIASES[m.lower()], br_id)
            total += val
            parts.append(f"{m}: {val:,.2f} LKR")
        return generate_smart_response(f"Q{q_num} {target_year} Total for {br_label}: {total:,.2f} LKR. Breakdown: {', '.join(parts)}", user_msg)

    # Comparison
    if "compare" in user_msg.lower() or "vs" in user_msg.lower():
        LAST_SUCCESSFUL_QUERY["text"] = user_msg # Save Context
        # Branch vs Branch
        branches = extract_all_branches(user_msg)
        if len(branches) >= 2:
            m_info = extract_month_only(user_msg)
            if m_info:
                val1 = fetch_monthly_sum_from_db(target_year, m_info[1], branches[0])
                val2 = fetch_monthly_sum_from_db(target_year, m_info[1], branches[1])
                diff = val1 - val2
                return generate_smart_response(f"Branch {branches[0]}: {val1:,.2f} LKR, Branch {branches[1]}: {val2:,.2f} LKR. Diff: {diff:,.2f} LKR", user_msg)
            return {"answer": "Please specify a month for comparison."}
            
        # Year vs Year
        years = re.findall(r'\b(202[0-9])\b', user_msg)
        if len(years) >= 2:
            years = sorted(list(set(years))) # Clean duplicates? 2024 vs 2025
            if len(years) >= 2:
                val1 = fetch_year_total(int(years[0]), br_id)
                val2 = fetch_year_total(int(years[1]), br_id)
                diff = val2 - val1 # growth
                return generate_smart_response(f"Sales {years[0]}: {val1:,.2f} LKR, Sales {years[1]}: {val2:,.2f} LKR. Growth: {diff:,.2f} LKR for {br_label}", user_msg)

        # Month vs Month
        months = extract_two_months(user_msg)
        if months:
            val1 = fetch_monthly_sum_from_db(target_year, months[0][1], br_id)
            val2 = fetch_monthly_sum_from_db(target_year, months[1][1], br_id)
            diff = val1 - val2
            return generate_smart_response(f"{months[0][0]}: {val1:,.2f} LKR, {months[1][0]}: {val2:,.2f} LKR. Diff: {diff:,.2f} LKR", user_msg)

    # Multi Month
    months = extract_all_months(user_msg)
    if len(months) >= 2:
        LAST_SUCCESSFUL_QUERY["text"] = user_msg # Save Context
        total = 0
        parts = []
        for m in months:
            val = fetch_monthly_sum_from_db(target_year, m[1], br_id)
            total += val
            parts.append(f"{m[0]}: {val:,.2f} LKR")
        return generate_smart_response(f"Total for {len(months)} months in {target_year} for {br_label}: {total:,.2f} LKR. Breakdown: {', '.join(parts)}", user_msg)

    # Average
    if "average" in user_msg.lower():
        LAST_SUCCESSFUL_QUERY["text"] = user_msg # Save Context
        m_info = extract_month_only(user_msg)
        if m_info:
            val = fetch_monthly_average(target_year, m_info[1], br_id)
            if val: return generate_smart_response(f"Average daily sales in {m_info[0]} {target_year} for {br_label}: {val:,.2f} LKR", user_msg)

    # YTD
    if "year" in user_msg.lower() and "total" in user_msg.lower():
        LAST_SUCCESSFUL_QUERY["text"] = user_msg # Save Context
        val = fetch_year_total(target_year, br_id)
        if val: return generate_smart_response(f"Total YTD Sales {target_year} for {br_label}: {val:,.2f} LKR", user_msg)

    # Best Day (Priority 3.5)
    if any(k in user_msg.lower() for k in ["highest", "best", "lowest", "worst"]) and "day" in user_msg.lower():
        LAST_SUCCESSFUL_QUERY["text"] = user_msg # Save Context
    # Real Time
    if "now" in user_msg.lower() or "current" in user_msg.lower():
        res = fetch_live_sales(br_id=br_id)
        if "error" in res: return {"answer": res["error"]}
        return generate_smart_response(f"Live Sales: {res['total']:,.2f} LKR", user_msg)

    # Specific Date
    d = extract_date(user_msg)
    if d:
        LAST_SUCCESSFUL_QUERY["text"] = user_msg # Save Context
        val = fetch_from_db(d, br_id)
        if val is not None:
            # Zero-Data Handling Rule
            if val == 0.0:
                 return {"answer": f"No sales were recorded for {d} for {br_label}."}
            return generate_smart_response(f"Sales on {d} for {br_label}: {val:,.2f} LKR", user_msg)
        return {"answer": f"No sales were recorded for {d} for {br_label}."}

    # Month Summary
    m_info = extract_month_only(user_msg)
    if m_info:
        LAST_SUCCESSFUL_QUERY["text"] = user_msg # Save Context
        val = fetch_monthly_sum_from_db(target_year, m_info[1], br_id)
        if val is not None: 
            # Zero-Data Handling Rule
            if val == 0.0:
                 return {"answer": f"No sales were recorded in {m_info[0]} {target_year} for {br_label}."}
            return generate_smart_response(f"Total sales in {m_info[0]} {target_year} for {br_label}: {val:,.2f} LKR", user_msg)
        return {"answer": f"No sales were recorded in {m_info[0]} {target_year} for {br_label}."}

    # Fallback: Clarification Loop (AI Brain)
    LAST_ATTEMPTED_QUERY["text"] = user_msg
    return generate_clarification_response(user_msg)
