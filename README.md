# Groww Buddy - HDFC Mutual Fund FAQ Assistant

Groww Buddy is a specialized RAG (Retrieval-Augmented Generation) QA assistant designed to answer factual questions about HDFC Mutual Funds. It features guardrails to block personally identifiable information (PII) and intercept financial/investment advisory queries.

---

## 🏗️ Project Structure

* **`frontend/`**: The web UI built with Vite, React, and Vanilla CSS (Groww dark theme).
* **`retrieval/`**: Core RAG query engine, retriever, LLM client, and the Python REST API server.
* **`ingestion/`**: Data scraper, ingestion, and FAISS indexing pipeline.
* **`validation/`**: Automated evaluation suite with 50 test cases for system validation.
* **`tests/`**: Integration and unit tests for the RAG and ingestion code.

---

## 🚀 Deployment

### Backend (Railway)
* Configured using `Procfile` to run the custom Python API server.
* Set to use `python-3.12` via `runtime.txt`.

### Frontend (Vercel)
* Configured to build from the `frontend/` subdirectory.
* Uses `vercel.json` inside `frontend/` for SPA route handling.
