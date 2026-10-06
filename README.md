# AI Placement Intelligence Platform

An intelligent placement preparation and shortlisting web application designed for students and job seekers.

## Resume Impact
- **Placement Copilot**: Built a RAG pipeline utilizing LangChain, Google Gemini, and PostgreSQL + pgvector to parse company JDs and provide source-grounded answers with page citations.
- **Explainable Matching Engine**: Engineered a deterministic, rule-based matching engine comparing student profiles with company benchmarks across skills, roles, salary, and hiring history.

---

## Tech Stack
- **Backend / Logic**: Python 3.10+
- **RAG Orchestration**: LangChain (Core & Community)
- **Embeddings & LLM**: Google Gemini API (`text-embedding-004`, `gemini-1.5-flash`)
- **Database**: PostgreSQL with `pgvector`
- **Frontend**: Streamlit
- **PDF Extraction**: `pypdf` / `PyPDFLoader`

---

## Project Structure
```
ai-placement-platform/
│
├── app/
│   ├── database/
│   │   ├── connection.py        # Database connection & health check
│   │   └── models.py            # SQLAlchemy models (Document, Chunk, Company)
│   ├── rag/
│   │   ├── loader.py            # PDF document loader
│   │   ├── splitter.py          # Recursive text splitter
│   │   ├── embeddings.py        # Gemini embeddings client
│   │   ├── vector_store.py      # pgvector integration & similarity search
│   │   └── qa.py                # Grounded prompt, LLM call, and source formatter
│   ├── matching/
│   │   ├── scoring.py           # Mathematical scoring formulas
│   │   └── matcher.py           # Company ranking & breakdown generator
│   └── ui/
│       └── app.py               # Streamlit application UI
│
├── data/
│   └── companies.csv            # 35+ realistic company benchmark records
│
├── uploads/                     # Storage for uploaded JD PDFs
├── .env.example                 # Environment variables blueprint
├── requirements.txt             # Project dependencies
├── INTERVIEW_NOTES.md           # Interview concept explanations & Q&A
├── PROJECT_RULES.md             # Development guidelines
└── README.md                    # Setup and execution guide
```

---

## Setup & Installation

### 1. Create and Activate Virtual Environment
Open PowerShell or your terminal inside the project directory:

```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# (If using CMD: venv\Scripts\activate.bat)
# (If using Linux/macOS: source venv/bin/activate)
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Fill in your actual values:
- `DATABASE_URL`: Your PostgreSQL connection string.
- `GOOGLE_API_KEY`: Your Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### 4. Verify Database Connection
Run the connection test script:
```bash
python -c "from app.database.connection import test_connection; print(test_connection())"
```

### 5. Initialize Database & Seed Benchmark Data
```bash
python -m app.database.init_db
```

### 6. Run the Web Application
Launch the Streamlit web dashboard:
```bash
python app/main.py
```
Or directly:
```bash
streamlit run app/ui/app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Running the Automated Test Suites

### 10-Point Comprehensive Test Suite (Resume & Interview Verification)
Validates all 10 core edge cases: valid JD, empty PDF, existing answers, non-existing answers, skill matching, role mismatch, salary penalties, strong fit, weak fit, and profile guards:
```bash
python tests/test_comprehensive_suite.py
```

### Individual Unit Tests
- **PDF Ingestion & Chunking**:
  ```bash
  python tests/test_ingestion.py
  ```
- **Embeddings & Vector Storage**:
  ```bash
  python tests/test_vector_store.py
  ```
- **RAG QA & Citations**:
  ```bash
  python tests/test_qa.py
  ```
- **Student Profile**:
  ```bash
  python tests/test_profile.py
  ```
- **Deterministic Matching Engine**:
  ```bash
  python tests/test_matcher.py
  ```

---

## Interview Preparation & Defense
For complete technical interview questions, mathematical formulas, and architectural trade-offs, read:
👉 **[INTERVIEW_NOTES.md](INTERVIEW_NOTES.md)**

