# AI Interview Preparation & Evaluation System

A full-stack mock interview platform that helps candidates practise role-specific interviews. Configure a session, answer AI-generated questions, receive structured feedback, and review a final performance report. Interview difficulty can adapt to performance, and low-scoring answers can be paused for human review.

The application includes a **React + Vite frontend** and a **FastAPI backend**. Interview workflows are orchestrated with LangGraph, and interview records are stored in SQLite.

## Features

- Configure interviews by role, experience level, interview format, starting difficulty, and question count.
- Generate interview questions and evaluate answers with a configurable language model.
- Adjust question difficulty based on answer scores.
- Pause an interview for human review and optionally override the evaluation before continuing.
- Review interview history, dashboard statistics, scores, recommendations, and final reports.
- Use a local Ollama model, deterministic mock responses, or a supported hosted provider.
- Explore and test the REST API through FastAPI's interactive documentation.

## Technology

- **Backend:** Python, FastAPI, Uvicorn, Pydantic, SQLAlchemy
- **AI workflow:** LangChain and LangGraph
- **Frontend:** React 18, JavaScript, Vite 5
- **Database:** SQLite (`interviews.db`)
- **LLM providers:** Ollama (default), mock, OpenAI, Anthropic, and Google Gemini

## Project structure

```text
app/
  ai/                 LLM provider setup, prompts, and LangChain chains
  api/                FastAPI routes
  graph/              LangGraph state, nodes, routing, and workflow
  schemas/            API request and response models
  services/           Interview lifecycle and scoring
  config.py           Environment-based application settings
  database.py         SQLite models and database setup
  main.py             FastAPI application
frontend/
  src/
    components/       Reusable interview and evaluation UI
    pages/            Dashboard, setup, session, report, and history screens
    api.js            Frontend API client
tests/                Backend API, workflow, and scoring tests
requirements.txt      Python dependencies
```

## Requirements

- Python 3.10 or later
- Node.js and npm
- [Ollama](https://ollama.com/) for local LLM inference (optional if using `mock` or a hosted provider)

## Run locally

Open two terminals from the project root.

### 1. Set up the backend

Create and activate a virtual environment, then install the Python dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

On macOS or Linux:

```bash
cp .env.example .env
```

The example configuration uses Ollama and `gemma2:2b`. Start Ollama and download that model before launching the backend:

```bash
ollama pull gemma2:2b
```

If you prefer the deterministic mock provider, change `LLM_PROVIDER=ollama` to `LLM_PROVIDER=mock` in `.env`. Mock mode does not require an Ollama service or API key.

Start the API:

```bash
python -m uvicorn app.main:app --reload
```

The API is available at <http://127.0.0.1:8000>. Interactive API documentation is at <http://127.0.0.1:8000/docs>, and the health endpoint is <http://127.0.0.1:8000/health>.

### 2. Set up the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. During development, Vite proxies `/interviews` and `/health` requests to the backend at `http://127.0.0.1:8000`.

To create and preview a production build:

```bash
npm run build
npm run preview
```

### 3. Run tests

From the project root, with the Python environment activated:

```bash
python -m pytest -v
```

The test fixtures use the mock LLM provider, so tests do not require access to a model service or hosted LLM API.

## Configuration

Application settings are read from `.env`. The available options are also documented in `.env.example`.

| Variable | Purpose | Example |
|---|---|---|
| `APP_ENV` | Application environment | `development` |
| `HOST` / `PORT` | Backend bind address and port | `0.0.0.0` / `8000` |
| `CORS_ORIGINS` | Allowed browser origins (comma-separated) | `http://localhost:5173,http://127.0.0.1:5173` |
| `LLM_PROVIDER` | Provider: `ollama`, `mock`, `openai`, `anthropic`, or `google` | `ollama` |
| `LLM_MODEL` | Model used by Ollama or mock mode | `gemma2:2b` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OPENAI_API_KEY` / `OPENAI_MODEL` | OpenAI credentials and model | Set the key locally |
| `ANTHROPIC_API_KEY` / `ANTHROPIC_MODEL` | Anthropic credentials and model | Set the key locally |
| `GOOGLE_API_KEY` / `GOOGLE_MODEL` | Google AI credentials and model | Set the key locally |
| `HUMAN_REVIEW_THRESHOLD` | Answer score below which review is requested (0–10) | `5.0` |
| `DIFFICULTY_UPGRADE_THRESHOLD` | Score at or above which difficulty increases | `8.0` |
| `DIFFICULTY_DOWNGRADE_THRESHOLD` | Score below which difficulty decreases | `5.0` |

Keep API keys in `.env`; do not commit secrets. The `.env` file and SQLite database are excluded by `.gitignore`. Provider integrations may require the corresponding LangChain provider package in addition to the dependencies listed in `requirements.txt`.

## Interview workflow

1. Create a session by choosing a role, experience level, interview type, initial difficulty, and 1–20 questions.
2. Start the session to generate the first question.
3. Submit an answer to receive an evaluation with a score, correctness, completeness, clarity, relevance, feedback, and suggested areas to improve.
4. If the score is below `HUMAN_REVIEW_THRESHOLD`, the session pauses. A reviewer can approve the evaluation or provide a modified evaluation, then resume the session.
5. After the final question, review the completed interview report and performance history.

Available experience levels are `entry`, `junior`, and `mid`. Interview types are `technical`, `hr`, and `mixed`. Starting difficulty can be `easy`, `medium`, or `hard`.

## REST API

Base URL: `http://127.0.0.1:8000`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Check API health |
| `POST` | `/interviews/` | Create an interview |
| `GET` | `/interviews/` | List interview history |
| `GET` | `/interviews/stats/summary` | Get dashboard statistics |
| `GET` | `/interviews/{interview_id}` | Get an interview and its history |
| `DELETE` | `/interviews/{interview_id}` | Delete an interview |
| `POST` | `/interviews/{interview_id}/start` | Start the interview and generate its first question |
| `POST` | `/interviews/{interview_id}/answer` | Submit an answer |
| `POST` | `/interviews/{interview_id}/continue` | Resume a session paused for human review |
| `GET` | `/interviews/{interview_id}/result` | Get the final report for a completed interview |

Example request to create a session:

```bash
curl -X POST http://127.0.0.1:8000/interviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "role": "Python Backend Engineer",
    "experience_level": "junior",
    "interview_type": "technical",
    "difficulty": "medium",
    "total_questions": 5
  }'
```

See `/docs` for request and response schemas, validation details, and interactive API requests.

## Data and privacy

Interview records are stored in the local SQLite database at `interviews.db`. The configured LLM provider receives prompts and interview answers for question generation and evaluation; review your provider's privacy terms before using real candidate data.

## License

No license is currently specified. Add a `LICENSE` file before redistributing this project.
