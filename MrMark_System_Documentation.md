# Mr. Mark Financial Assistant - System Documentation

## 1. System Overview
"Mr. Mark" (MarkSolutionChatbot) is an AI-powered enterprise financial assistant designed to answer natural language queries about sales data. It combines a robust SQL-based data retrieval system with a local LLM (Large Language Model) to provide "Accounting Intelligence" without hallucinating numbers.

## 2. Technology Stack

### Backend
*   **Language**: Python 3.10+
*   **Framework**: FastAPI (High-performance web API)
*   **Server**: Uvicorn
*   **Database**: SQLite (`sales.db`) for local sales data and logging.
*   **AI/LLM**: Ollama (running locally) with `tinyllama` model for natural language analysis.
*   **Libraries**: 
    *   `requests` (API calls to ERP and Ollama)
    *   `pydantic` (Data validaton)
    *   `difflib` (Fuzzy string matching for typos)
    *   `calendar` & `datetime` (Date handling)

### Frontend
*   **Framework**: React.js (Create React App)
*   **HTTP Client**: Axios
*   **Styling**: Custom CSS (Glassmorphism design, Dark mode)
*   **Features**:
    *   Role-based UI (Admin, Manager, Staff)
    *   Saved Queries
    *   Copy-to-Clipboard
    *   Smart Suggestions Panel

### External Integrations
*   **ERP API**: `https://api.emark.live` (Fetches real-time daily/monthly sales data)
*   **Ollama**: `http://localhost:11434` (Local inference engine)

## 3. Installation & Setup

### Prerequisites
1.  **Python 3.10+** installed.
2.  **Node.js 16+** installed.
3.  **Ollama** installed and running (`ollama serve`).
4.  **Model**: Run `ollama pull tinyllama` in your terminal.

### Backend Setup
1.  Navigate to `backend/`:
    ```bash
    cd backend
    ```
2.  Create virtual environment (optional but recommended):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Initialize Database (if needed):
    *   Execute `database/seed_sales.sql` into `sales.db`.
5.  Start Server:
    ```bash
    uvicorn main:app --reload --port 8000
    ```

### Frontend Setup
1.  Navigate to `frontend/`:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start React App:
    ```bash
    npm start
    ```
    (Opens at http://localhost:3000)

## 4. Access Control & Roles

The system implements a strict Role-Based Access Control (RBAC) mechanism. Access is divided into four tiers:

| Role | Username (Demo) | Branch Access | AI Analysis | Query Restrictions |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admin` | **ALL** | ✅ Active | **None**. Can compare branches and see company-wide totals. |
| **Owner** | `owner` | **ALL** | ✅ Active | **None**. Optimized for high-level summaries. |
| **Manager** | `manager_br1`<br>`manager_br2` | Scoped (1 or 2) | ✅ Active | Limited to their assigned branch. Cannot see other branches. |
| **Staff** | `staff_br1`<br>`staff_br2` | Scoped (1 or 2) | ❌ **Disabled** | **High Restriction**. Cannot use words like "compare", "growth", "vs". Numeric data only. |

*Note: The "Causal Guard" acts as a global firewall for ALL users, blocking "Why did..." questions to prevent hallucination.*

## 5. System Logic & Workflow

How Mr. Mark processes a user message:

1.  **Input & Correction**:
    *   User types a message (e.g., "Slaes in Januaary").
    *   System corrects typos using `difflib` (e.g., "Januaary" -> "january").

2.  **Safety & Role Checks**:
    *   **Causal Guard**: Blocks questions aimed at "Why" or "Reasons" (e.g., "Why did sales drop?") to effectively prevent AI hallucination of reasons not in the data.
    *   **Role Guard**: content is filtered based on login role:
        *   **STAFF**: Seeing restricted numerical data only. No cross-branch comparisons.
        *   **ADMIN**: Full access to all comparisons and analysis.

3.  **Smart Context Merging**:
    *   The system remembers the previous query's context (Year, Branch, Month).
    *   If a user follows up with "what about branch 2?", it merges this with the previous query (e.g., "Sales in Jan 2025 Branch 1" -> "Sales in Jan 2025 Branch 2").

4.  **Data Retrieval**:
    *   Parses the merged query to extract:
        *   **Date/Time**: Year, Month, "Today", "Yesterday", "Past N Months".
        *   **Branch**: Branch ID(s).
    *   **Source Selection**:
        *   Historical Data -> Queries `sales.db` (SQLite).
        *   Real-time Data ("Today") -> Queries External ERP (`api.emark.live`).

5.  **Accounting Intelligence (LLM Layer)**:
    *   If data is successfully retrieved, it is formatted into a PostgreSQL-style ASCII table.
    *   The text table + User Question is sent to **Ollama (tinyllama)** with a generic "Accounting Assistant" system prompt.
    *   **Prompt Rules**: "NO Causal Inference", "Factual Only", "No Fabricated Metrics".
    *   The AI generates a short, factual observation summary.

6.  **Visualization Layer (Additive)**:
    *   Evaluates if the data supports visualization (Trends/Comparisons + >1 Data Point).
    *   **Role Check**: Skips if User is **STAFF**.
    *   Generates a JSON block (`[CHART_JSON]`) if conditions are met.

7.  **Response Construction**:
    *   Final Output = [ASCII Table] + [AI Analysis (if applicable)] + [Chart JSON (if applicable)].
    *   If the user is **STAFF**, both AI Analysis and Visualization are skipped.

## 6. Visualization Module (Additive Layer)

This strictly additive module generates visualization data without modifying existing outputs.

### 6.1 Trigger Logic (When to Generate)
Visualization is generated **ONLY IF ALL** conditions are met:
1.  **Data Content**: Contains Trends (Time-series) OR Comparisons (Branches/Categories).
2.  **Data Volume**: More than one data point.
3.  **Role Access**: User is **NOT** "STAFF".

### 6.2 Data & Chart Rules
*   **Source**: Extract strictly from the displayed SQL table. No calculations or inferences.
*   **Chart Types**:
    *   **Line**: Dates, Months, Time-series.
    *   **Bar**: Branch comparisons, Category comparisons.

### 6.3 JSON Output Format
The system appends the following block (and only this block) if valid:
```json
[CHART_JSON]
{
  "chart_type": "line", // or "bar"
  "title": "Descriptive Title",
  "labels": ["Label1", "Label2"],
  "datasets": [
      { "label": "Series", "data": [value1, value2] }
  ]
}
[/CHART_JSON]
```

### 6.4 Safety & Restrictions
*   **Immutability**: Must NOT modify SQL, tables, or AI text.
*   **Sanitization**: Valid JSON only, no comments.
*   **Fail-Safe**: If unsafe or unclear, skip visualization silently.

## 7. Key Features

*   **Real-time ERP Sync**: Fetches live sales data for "today" directly from the company API.
*   **Fuzzy Date Parsing**: Understands "Jan", "January", "current month", "last 3 months", "2024".
*   **Secure Implementation**:
    *   SQL Parameterization (prevents SQL Injection).
    *   Output Firewall (scans AI response for forbidden phrases before showing to user).
*   **Interactive UI**:
    *   Glassmorphism design.
    *   One-click "Copy" for tables.
    *   "Save Query" feature to bookmark complex reports.

## 8. Example Outputs

**User**: "Sales in Jan 2025 Branch 1"

**System**:
```text
+----------+-------+
| sale_date| amount|
+----------+-------+
|2025-01-01| 950000|
+----------+-------+

> 📝 AI Analysis: Sales for Branch 1 in January 2025 totaled 950,000. This represents a single data point for the requested period.
```

**User**: "Compare Branch 1 vs 2"

**System**:
```text
(Table showing side-by-side data)
...
> 📝 AI Analysis: Branch 1 shows higher volume than Branch 2 for the observed period, with a difference of X amount.

[CHART_JSON]
{
    "chart_type": "bar",
    "title": "Branch 1 vs Branch 2 Comparison",
    "labels": ["Branch 1", "Branch 2"],
    "datasets": [{ "label": "Sales", "data": [120000, 95000] }]
}
[/CHART_JSON]
```
