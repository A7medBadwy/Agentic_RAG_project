# Agentic RAG — Multi-Agent Document Intelligence

A modular FastAPI application for chatting with uploaded PDF, DOCX, and TXT documents.
It uses three cooperating components:

- **Retriever Agent**: query rewriting, dense retrieval, BM25 keyword retrieval, hybrid ranking, and evidence selection.
- **Analyst Agent**: evidence sufficiency checks, document comparison, and safe numerical calculations.
- **Answer Agent**: grounded responses with document/page citations.

The workflow includes a bounded feedback loop: if the Analyst identifies missing evidence, the Orchestrator asks the Retriever for another targeted search.

## Requirements

- Python 3.10+
- Windows, macOS, or Linux
- An OpenRouter API key for concise, synthesized answers. Without it, the app explains that answer generation is unavailable.
- Qdrant local mode and Hugging Face embeddings run locally. The first embedding-model use downloads the model.

## Setup (Windows PowerShell)

Run these commands from the project root (the directory containing `requirements.txt`):

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and add your `OPENROUTER_API_KEY` if you want LLM-generated responses.

Start the API from the **project root**:

```powershell
uvicorn app.main:app --reload
```

Open:
- API docs: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8000/

> Important: use `uvicorn app.main:app --reload`, not `uvicorn main:app --reload`, because the FastAPI instance is in `app/main.py`.

## Example workflow

1. Open the dashboard.
2. Upload one or more PDF, DOCX, or TXT files.
3. Ask a question about the uploaded documents.
4. Inspect citations in the answer to see which file and page support the response.

API examples:

```powershell
# Upload a file
curl.exe -X POST "http://127.0.0.1:8000/api/upload" -F "files=@sample.pdf"

# Ask a question
curl.exe -X POST "http://127.0.0.1:8000/api/chat" `
  -H "Content-Type: application/json" `
  -d "{\"question\":\"Summarize the main findings\"}"
```

## Project structure

```text
agentic_rag_project/
├── app/
│   ├── agents/
│   │   ├── analyst_agent.py
│   │   ├── answer_agent.py
│   │   ├── orchestrator.py
│   │   └── retriever_agent.py
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   └── config.py
│   ├── ingestion/
│   │   └── pipeline.py
│   ├── services/
│   │   ├── llm.py
│   │   └── vector_store.py
│   ├── static/
│   │   ├── app.js
│   │   └── styles.css
│   ├── templates/
│   │   └── index.html
│   ├── schemas.py
│   └── main.py
├── data/
├── tests/
├── .env.example
├── .gitignore
└── requirements.txt
```

## Notes and limitations

- Qdrant is configured in local persistent mode under `data/qdrant`; no Docker or hosted Qdrant account is required.
- The default embedding model is `sentence-transformers/all-MiniLM-L6-v2`.
- PDF page citations are page-based. DOCX and TXT citations use a logical page value of `1` because those formats do not provide stable PDF-style page boundaries.
- Table extraction is best-effort. Complex scanned PDFs may require OCR, which is not included in this starter.
- The calculator accepts a restricted arithmetic expression grammar; it does not execute arbitrary Python.
- The first run can take time while the embedding model is downloaded.
- This is a learning/project baseline. Before public deployment, add authentication, per-user authorization, upload quotas, malware scanning, HTTPS, and stronger tenant isolation.
