# FastAPI Backend

## Responsibilities

The FastAPI backend exposes the deterministic JD-resume analysis pipeline through HTTP endpoints.

- `main.py`: API routes, request validation, upload handling and CORS configuration.
- `candidate_pipeline.py`: orchestrates document extraction, resume parsing, entity extraction, JD analysis, skill tagging, evidence matching, eligibility checks and scoring.

The root-level Python engines remain the source of truth for analysis logic.

## Installation

Run from the project root:

```powershell
python -m pip install -r requirements-dev.txt
```

## Start the API

Run from the project root:

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

Interactive API documentation: `http://localhost:8000/docs`

## Endpoints

- `GET /api/health`
- `GET /api/dashboard`
- `GET /api/requirements`
- `GET /api/requirements/{requirement_id}`
- `POST /api/candidates/analyze`

## Candidate analysis request

The live analysis endpoint accepts multipart form data containing:

- `resume`: PDF or DOCX file.
- `jd_text`: job description text.

Limits: 10 MB per resume and 50,000 characters for the job description.

## Security and deployment considerations

- Resume file extensions and file contents are validated.
- Uploaded content is processed using temporary working files.
- Local development defaults to the Vite origins `http://localhost:5173` and `http://127.0.0.1:5173`.
- Set `CORS_ORIGINS` in production to a comma-separated list of exact frontend origins (no trailing slash).
- Wildcard (`*`) origins are rejected because credentialed CORS is enabled.
- Configure HTTPS and verify the hosting provider request-body limit supports the 10 MB application upload limit.

## Testing

Run the project test suite from the root:

```powershell
python -m pytest -q
```


## Production start command

From the repository root:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Set `CORS_ORIGINS` to the exact Vercel frontend origin, for example `https://your-app.vercel.app`.
