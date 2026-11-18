# EvidenceFirst — JD–Resume Analyzer

EvidenceFirst analyzes a job description against an uploaded resume and produces an explainable, evidence-based assessment. It identifies matched, partially supported and missing requirements, highlights critical gaps, and shows the resume evidence behind each assessment.

> **Important:** EvidenceFirst is a deterministic decision-support tool, not a hiring decision system. Its alignment score is not a probability of receiving an interview or an assessment of a person's overall ability.

## What it does

- Extracts text from PDF and DOCX resumes.
- Extracts and classifies requirements from job descriptions.
- Matches requirements to resume evidence.
- Labels evidence as matched, partial or missing.
- Calculates a weighted alignment score and identifies critical gaps.
- Reports experience/eligibility signals separately from skills evidence.
- Exposes the existing Python analysis pipeline through a React interface and FastAPI API.

The Python pipeline is the source of truth. The current analysis is deterministic and rule-based; it does not train or fine-tune a machine-learning model.

## Architecture

| Layer | Technology | Location |
|---|---|---|
| User interface | React, TypeScript, Vite | `frontend/` |
| API | FastAPI, Uvicorn | `backend/app/main.py` |
| Candidate workflow | Python | `backend/app/candidate_pipeline.py` |
| Extraction, matching and scoring | Python | Root-level engine modules |

## Run locally

### Prerequisites

- Python 3.12 or a compatible supported version
- Node.js and npm
- Git

### 1. Install backend dependencies

From the repository root:

```powershell
python -m pip install -r requirements-dev.txt
```

### 2. Start the API

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

API health: `http://localhost:8000/api/health`
Interactive API docs: `http://localhost:8000/docs`

### 3. Start the frontend

In a second terminal:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Open `http://localhost:5173`.

The frontend uses `VITE_API_URL` when set; otherwise it calls `http://localhost:8000`.

## Test and build

From the repository root:

```powershell
python -m pytest -q
```

Build the frontend:

```powershell
cd frontend
npm.cmd ci
npm.cmd run build
```

Some optional integration tests use private resume files and generated extraction JSON. They are skipped unless their fixture directories are explicitly configured. See [Testing private resume fixtures](#testing-private-resume-fixtures).

### Testing private resume fixtures

Do not commit personal resumes or generated candidate data. To run the optional local-only integration tests, set these environment variables to directories containing your own fixture files:

```powershell
$env:EVIDENCEFIRST_RESUME_FIXTURE_DIR = "C:\path\to\private\resume-fixtures"
$env:EVIDENCEFIRST_ENTITY_RESULTS_DIR = "C:\path\to\private\entity-results"
python -m pytest -q
```

Expected filenames are documented in `test_structured_parser.py` and `test_structured_entities.py`. These tests validate one private sample resume; they are not a substitute for general, synthetic unit tests.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/dashboard` | Read existing dashboard sample outputs |
| GET | `/api/requirements` | Read/search existing requirement sample outputs |
| GET | `/api/requirements/{requirement_id}` | Read one sample requirement |
| POST | `/api/candidates/analyze` | Analyze an uploaded resume and supplied JD text |

Candidate analysis accepts multipart form fields `resume` (PDF or DOCX) and `jd_text`. Current application limits are 10 MB per resume and 50,000 characters per JD. Dashboard/requirements GET routes read sample files under `jd_results/`; they are distinct from the live candidate-analysis request and may return an unavailable response when those sample files are not present.

## Deployment overview

Deploy the frontend and backend separately:

1. Deploy `backend/` as a Python web service (for example, on Render) using the repository root as its build context.
2. Set the backend start command to:

   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
   ```

3. Set the backend environment variable `CORS_ORIGINS` to the exact deployed frontend origin(s), comma-separated, with no trailing slash. Example: `https://your-app.vercel.app`.
4. Deploy `frontend/` to Vercel with **Root Directory** `frontend`, framework preset **Vite**, build command `npm run build`, and output directory `dist`.
5. Set the Vercel environment variable `VITE_API_URL` to the deployed backend base URL, then redeploy the frontend.

For local development, the backend defaults to `http://localhost:5173` and `http://127.0.0.1:5173` as allowed CORS origins. Production origins must be explicitly configured. Do not use `*` with credentialed CORS.

The backend accepts uploads up to 10 MB. Host-level request-size limits must be checked before production use; do not assume every hosting platform accepts the full application limit.

## Privacy and security

- Never commit resumes, cover letters, candidate data, generated analyses, `.env` files or credentials.
- Use HTTPS in production.
- Configure exact CORS origins.
- Review hosting request limits, logs, retention and privacy disclosures before accepting real candidate documents.
- The current application is not a security or compliance certification.

## Limitations

- Matching is deterministic and may miss semantically equivalent wording.
- Multi-part requirements may need more precise decomposition.
- Extraction quality depends on document structure and text availability; scanned/image-only documents may not work reliably.
- No independently validated accuracy benchmark is currently established.
- The sample dashboard endpoints depend on local `jd_results/` artifacts.

## Project documentation

- [Web application and API details](README_WEB_APP.md)
- [Backend details](backend/README.md)
- [Engineering history, architecture and methodology](docs/ENGINEERING_NOTES.md)

## License

No license has been specified yet. All rights reserved unless a license is added to this repository.
