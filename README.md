# Mr. Mark - Financial AI Assistant 🤖💼

**Your dedicated AI partner for MarkSolution Financial Analytics.**

Mr. Mark is an intelligent chatbot designed to bridge the gap between complex ERP data and simple business questions. Instead of running reports, you just ask him.

## 🌟 What Can Mr. Mark Do?

*   **IDENTITY**: Acts as a professional financial assistant (Mr. Mark).
*   **REAL-TIME**: Checks live sales *right now* via ERP API.
*   **HISTORY**: Remembers 2025 sales data for instant analysis.
*   **COMPARISON**: "Compare Jan vs Feb" or "Branch 1 vs Branch 2".
*   **GOALS**: Tracks targets (e.g., "Goal is 50M. How are we doing?").
*   **INSIGHTS**: Finds "Best Day", "Worst Month", "Average Sales".

## 🚀 How to Start

1.  **Start the System**:
    ```bash
    docker-compose up -d
    ```
    (This starts the Database, Backend API, AI Brain, and Web Interface).

2.  **Open the App**:
    👉 **[http://localhost:3000](http://localhost:3000)** (Chat Interface)
    👉 **[http://localhost:8000](http://localhost:8000)** (API Status)

3.  **Sync Data** (If first time):
    ```bash
    docker exec -it marksolution_backend python3 sync_year.py
    ```

## 💡 How to Talk to Mr. Mark

| Goal | Example Question |
| :--- | :--- |
| **Check Live Sales** | "How much are we selling right now?" |
| **Check History** | "What was the total in January?" |
| **Compare** | "Compare Branch 1 and Branch 2 in March." |
| **Best Performance** | "Which was the best sales month in 2025?" |
| **Specific Date** | "How much did we earn on Jan 15th?" |
| **Goal Tracking** | "My goal is 40 Million. Have we reached it?" |

---
*Powered by Mistral AI (Ollama) & FastAPI*
