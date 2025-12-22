# MarkSolution Financial Chatbot 🤖📊

**A smart, AI-powered financial assistant for analyzing real-time and historical sales data.**

This project is a full-stack chatbot application designed for **MarkSolution** to help business owners and analysts query their ERP sales data using natural language. It seamlessly blends **historical data** from a local PostgreSQL database with **live real-time data** from an external ERP API.

## 🌟 Key Features

*   **Natural Language Querying**: Ask questions like *"How much did we earn in January?"* or *"Compare sales between Oct and Nov"*.
*   **Real-Time Sales**: Instantly fetches live "current" sales data directly from the ERP system.
*   **Historical Analysis**: Deep dives into past performance using a synced PostgreSQL database.
*   **Advanced Analytics**:
    *   📈 **Month-over-Month Comparison**
    *   📊 **Average Daily Sales**
    *   🏆 **Best & Worst Performing Months**
    *   🎯 **Goal Logic** (e.g., *"Goal is 100M"*)
    *   📅 **Year-To-Date (YTD) Summary**
*   **Multi-Branch Support**: Intelligent filtering by Branch ID (e.g., *"Branch 1 sales"*).
*   **Smart Date Parsing**: Handles distinct dates, relative times ("yesterday", "past 3 months"), and future date protection.

## 🛠 Tech Stack

*   **Frontend**: React.js (Chat Interface)
*   **Backend**: Python (FastAPI)
*   **Database**: PostgreSQL 16 (Dockerized)
*   **Infrastructure**: Docker & Docker Compose
*   **Integrations**: eMark External ERP API

## 🚀 Getting Started

### Prerequisites
*   Docker & Docker Compose
*   Git

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Madushan186/MarkSolutionChatbot.git
    cd MarkSolutionChatbot
    ```

2.  **Set up Environment Variables**:
    Create a `.env` file in the root directory with your database credentials (variables matching `docker-compose.yml`).

3.  **Run with Docker**:
    ```bash
    docker-compose up -d --build
    ```
    This will start both the **Backend API** (Port 8000) and **Database** (Port 5432).

4.  **Sync Data**:
    Run the sync script to populate your local database with 2025 data:
    ```bash
    # Sync 2025 Data (Monthly Aggregation)
    docker exec -it marksolution_backend python3 sync_year.py
    ```

## 💡 Usage Examples

*   *"What is the summary for January and February?"*
*   *"How much is the current sale for Branch 1?"*
*   *"Compare October and December sales."*
*   *"What was the highest sales month in 2025?"*

---
*Built for MarkSolution - 2025*
