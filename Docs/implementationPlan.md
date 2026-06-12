# Phase-Wise Implementation Plan: Mutual Fund FAQ Assistant

This document outlines a structured, 6-phase roadmap for developing and deploying the **Mutual Fund FAQ Assistant**. It aligns the goals in [problemStatement.md](file:///c:/Users/shahn/Groww%20Buddy/Docs/problemStatement.md) with the technical designs in [architecture.md](file:///c:/Users/shahn/Groww%20Buddy/Docs/architecture.md).

---

## 📅 Roadmap Overview

| Phase | Focus Area | Estimated Effort | Key Milestone |
| :--- | :--- | :--- | :--- |
| **Phase 0** | Scaffolding & Config | 1 Day | Repository structure setup, environment variables, dependency management, and corpus/source registry configured. |
| **Phase 1** | Ingestion & Cleaning | 2 Days | Automated scraper fetching raw clean text & metrics from all 5 target URLs |
| **Phase 2** | Indexing & Vector DB | 2 Days | ChromaDB initialized and populated with semantically chunked, metadata-tagged documents |
| **Phase 3** | Core RAG Pipeline | 3 Days | LLM integration, post-generation validation, and formatting pipelines finalized |
| **Phase 4** | Guardrails & Refusal | 2 Days | 100% block rate on PII inputs & advisory queries; SEBI/AMFI redirections active |
| **Phase 5** | UI & Daily Scheduler | 2 Days | Streamlit UI running with disclaimer; daily ingestion script automated via Cron |
| **Phase 6** | Testing & Validation | 2 Days | Full evaluation report showing precision, compliance, and hallucination metrics |

---

## 🔍 Detailed Phase Breakdown

### Phase 0: Project Scaffolding & Configuration
*Set up project repository, dependency definitions, local configs, and target source registry.*

- [x] **0.1 Repository Structure Setup**
  - Set up standard folders: `config/`, `ingestion/`, `retrieval/`, `validation/`, `formatter/`, `app/`, `tests/`, `Docs/`.
- [x] **0.2 Dependency Management**
  - Create configuration files (`requirements.txt` or `pyproject.toml`).
  - Install core libraries (LangChain/LlamaIndex, ChromaDB/FAISS, BeautifulSoup4, python-dotenv, streamlit, pytest).
- [x] **0.3 Environment Configuration**
  - Create template `.env.example` and local `.env` containing keys (e.g. `GROQ_API_KEY`) and paths.
  - Set up logging framework configurations.
- [x] **0.4 Corpus & Source Registry**
  - Create a JSON or Python configuration file (`corpus_registry.json`) mapping HDFC schemes to their target seed URLs and expected metadata tags.

---

### Phase 1: Data Ingestion & Cleaning
*Implement the ingestion script to crawl and clean page content.*

- [x] **1.1 Web Scraper Development**
  - Write python module using BeautifulSoup/Playwright to fetch HTML from the target URLs in the corpus registry.
  - Parse unstructured text fields: *Fund Investment Objective, Scheme details, FAQs, and holding distributions*.
  - Parse structured attributes: *Current NAV, Expense Ratio, Exit Loads, Fund Managers, AUM (Assets Under Management)*.
- [x] **1.2 Normalizer & Parser**
  - Implement content cleaning functions to strip headers, footers, script tags, cookies banner text, and HTML noise.
  - Output normalized, plain text files and structured JSON records.

---

### Phase 2: Indexing & Vector DB Setup
*Prepare chunking strategies and populate the database.*

- [x] **2.1 Document Chunking Strategy**
  - **Header-Based Splitting:** Use `MarkdownHeaderTextSplitter` on headers `##` (for sections like Scheme Info, Metrics, Objective) and `###` (for individual fund managers and FAQ Q&A blocks).
  - **Holdings Table Preservation:** Keep the entire `## Top Holdings` table as a single, isolated chunk to maintain row integrity and semantic meaning of tabular asset allocations.
  - **Length-Bounded Recursive Splitting:** For exceptionally large sections (e.g. fund manager experience & list of managed funds), run a secondary `RecursiveCharacterTextSplitter` with a `1000-character chunk size` and a `200-character overlap` to stay within embedding token limits while preserving context.
- [x] **2.2 Metadata Schema Implementation**
  - Tag every text chunk with a metadata schema extracted from the processed registry and JSON data:
    ```json
    {
      "scheme_id": "hdfc_defence",
      "scheme_name": "HDFC Defence Fund Direct Growth",
      "source_url": "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
      "last_updated_date": "2026-06-10",
      "category": "Equity",
      "risk_level": "Very High",
      "section_type": "fund_managers" 
    }
    ```
- [x] **2.3 Vector Database Indexing (FAISS)**
  - Initialize a local `FAISS` index using the `faiss-cpu` library.
  - Use BGE models (e.g. `BAAI/bge-small-en-v1.5` for fast CPU inference, or `BAAI/bge-large-en-v1.5` for higher semantic accuracy) or `google-generativeai` embeddings to generate vectors.
  - Store chunks along with the enriched metadata dictionary in the FAISS-backed document store.

---

### Phase 3: Core RAG Retrieval & LLM Integration
*Build the query retrieval mechanisms, LLM integration, validator checks, and formatters.*

- [x] **3.1 Information Retrieval**
  - Implement query embedding logic.
  - Implement Vector Store query search fetching top-3 closest matches.
  - Add metadata filters to restrict retrieval to a single scheme if mentioned in the query.
  - **Holdings Table Sub-chunking:** Refine indexing to create a "Top 10 Holdings" table chunk and "Individual Company Chunks" (one sentence per holding) to resolve embedding truncation and dilution issues.
- [x] **3.2 LLM Answer Generation**
  - Connect client to LLM API (e.g. Groq).
  - Draft strict prompts instructing the LLM to restrict answers to the context and refrain from predictions or returns.
- [x] **3.3 Response Validator Component**
  - Implement validation checks:
    - **Facts-only check:** Scans the response for recommendations, projections, or comparisons.
    - **Citation presence check:** Ensures the retrieved chunks contain source URLs.
    - **Length validation:** Ensures the answer has a maximum of 3 sentences.
    - **Fallback router:** Raises an error or reroutes to fallback response if checks fail.
- [x] **3.4 Response Formatter Component**
  - Implement formatting rules:
    - **Citation inclusion:** Appends exactly one direct source URL link used to construct the answer.
    - **Footer injection:** Appends `Last updated from sources: YYYY-MM-DD` based on the document crawl date.
    - **Format normalization:** Strips excess whitespace and normalizes text layout.

---

### Phase 4: Guardrails & Refusal Handling
*Create filters to ensure user privacy and regulatory compliance.*

- [x] **4.1 Pre-Retrieval PII Filter**
  - Implement regex patterns to scan query strings for Aadhaar, PAN, emails, bank accounts, and phone numbers.
  - Halt transaction and trigger warning if PII is detected.
- [x] **4.2 Intent Classification (Refusal Module)**
  - Implement a low-latency LLM classification query or heuristic keyword checker to screen for advisory triggers (*"recommend"*, *"should I buy"*, *"which is better"*).
  - Create a Refusal Router that intercepts advisory queries and returns a friendly denial text redirecting to SEBI Investor Education/AMFI.
- [x] **4.3 Post-Generation Output Validation**
  - Add validation code to count sentences in the LLM output.
  - Add compliance check to scan LLM outputs for unauthorized advice keywords. If violated, drop the answer and return the standard fallback response.

---

### Phase 5: User Interface & Ingestion Scheduler
*Assemble the visual application and automate updates.*

- [x] **5.1 API Backend Server & React Front-End Interface**
  - **API Backend Server (`retrieval/api_server.py`):** Build a local Python HTTP server exposing a CORS-enabled `/api/query` POST endpoint that queries `MutualFundQueryEngine`.
  - **React Frontend (`frontend/`):** Scaffold a Vite + React web application.
  - **Modern UI Styling:** Create a dark-themed visual layout with a welcome hero, warning text below the logo header ("Facts-only. No investment advice."), clickable query pills, loading animations, citation links, and footer links mapped to official Groww Privacy Policy and Terms and conditions pages.
- [x] **5.2 Scheduler Setup**
  - Wrap the Phase 1 web scraper into an execution script (`ingest_daily.py`).
  - Configure a local `Cron` (Linux/macOS) or `Task Scheduler` (Windows) to run `ingest_daily.py` daily at 10:00 AM IST.
  - The script will query Groww, check for changes, generate new embeddings, and overwrite the vector database with the new `last_updated_date` timestamp.

---

### Phase 6: Testing, Evaluation & Review
*Evaluate safety, accuracy, and format compliance.*

- [ ] **6.1 Automated Accuracy & Refusal Tests**
  - Run test questions (asking for NAVs, exit loads, expense ratios) and evaluate correctness.
  - Test refusal behavior under adversarial prompts ("Which fund is best?", "Should I buy X?").
- [ ] **6.2 Formatting Validation Tests**
  - Validate that responses contain exactly one citation link, are under 3 sentences, and have the correct footer timestamp.
- [ ] **6.3 Evaluation Matrix**
  Implement test runner metrics to score system performance on a validation dataset of 50+ test cases:
  
  | Metric | Definition | Success Threshold |
  | :--- | :--- | :--- |
  | **Retrieval Precision** | % of retrieved chunks that are directly relevant to the query | $\ge 90\%$ |
  | **Citation Correctness** | % of responses with a citation link pointing directly to the correct source page | $100\%$ |
  | **Refusal Accuracy** | % of advisory, suitability, comparative, or comparison queries correctly declined | $100\%$ |
  | **Hallucination Rate** | % of generated claims that cannot be directly verified against the retrieved context | $0\%$ |
  | **Formatting Compliance** | % of responses with $\le 3$ sentences and the exact required update footer | $100\%$ |
  | **Source Attribution Accuracy** | % of times the system maps the correct scheme URL rather than a generic root URL | $100\%$ |
