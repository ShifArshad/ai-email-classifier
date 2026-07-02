# AI-Powered Email Classifier & Storage Pipeline

An intelligent, production-ready asynchronous email classification and persistence backend built with **FastAPI**, **SQLite**, and the **Google Gemini 2.5 Flash API**. 

This project simulates a real-world email processing engine that ingests emails, leverages Structured Outputs via Large Language Models (LLMs) to accurately categorize them, implements resilient fault-tolerance algorithms, and enforces database security mechanisms to prevent injection attacks.

---

## 🚀 Key Features & Engineering Highlights

- **Structured LLM Responses:** Utilizes Pydantic schemas paired with Gemini's `response_schema` configuration to enforce deterministic JSON outputs (`category` and `reason`), completely eliminating runtime JSON parsing breaks.
- **Resilient Fault Tolerance:** Implements a custom retry loop with delay padding to gracefully recover from `503 Service Unavailable` or transient API rate limits.
- **Batch & Stream Processing:** Offers endpoints to process a single incoming email payload or sequentially stream and parse an array of emails (simulating an inbox synchronization cron job).
- **Secure Persistence Layer:** Uses **SQLite** with parameterized queries (`?` placeholders) instead of raw string formatting to inherently neutralize SQL Injection vulnerabilities.

---

## 🛠️ Tech Stack

- **Framework:** FastAPI (Python 3.10+)
- **AI Engine:** Google GenAI SDK (`gemini-2.5-flash`)
- **Database:** SQLite3
- **Data Validation:** Pydantic v2
- **Environment Management:** Python-dotenv

---

## ⚡ Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/ai-email-classifier.git](https://github.com/your-username/ai-email-classifier.git)
cd ai-email-classifier