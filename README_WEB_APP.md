# EvidenceFirst Web Application

## Architecture

- `frontend/`: React, TypeScript and Vite user interface.
- `backend/app/main.py`: FastAPI application and HTTP endpoints.
- `backend/app/candidate_pipeline.py`: orchestrates the existing Python analysis engines.
- Root-level Python modules: deterministic extraction, JD analysis, evidence matching, scoring and eligibility.

The deterministic Python pipeline remains the source of truth. The React application is an interface over that pipeline, not a replacement for it.

## Requirements

- Python 3.12 or compatible supported Python version.
- Node.js and npm.

## Run locally on Windows

### 1. Install Python dependencies

From the project root:

```powershell
python -m pip install -r requirements-dev.txt
```

### 2. Start the backend

From the project root, in Terminal 1:

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

Backend health: `http://localhost:8000/api/health`

API documentation: `http://localhost:8000/docs`

### 3. Install and start the frontend

In Terminal 2:

```powershell
cd frontend
npm.cmd ci
npm.cmd run dev
```

Open `http://localhost:5173`.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Backend health check |
| GET | `/api/dashboard` | Existing analysis dashboard data |
| GET | `/api/requirements` | Retrieve and search existing requirements |
| GET | `/api/requirements/{requirement_id}` | Retrieve an existing requirement |
| POST | `/api/candidates/analyze` | Analyze an uploaded resume and job description |

### Live candidate analysis

`POST /api/candidates/analyze` accepts multipart form data:

- `resume`: PDF or DOCX resume.
- `jd_text`: job description text.

The endpoint runs the candidate analysis pipeline using the supplied inputs. The upload limit is 10 MB and the job description limit is 50,000 characters.

### Existing dashboard endpoints

The GET dashboard and requirement endpoints read the existing analysis outputs under `jd_results/`. Those outputs are separate from a new live candidate analysis request.

## Important implementation notes

- The analysis pipeline is deterministic and rule-based; it does not train or fine-tune a machine learning model.
- The API validates uploaded resume formats and file contents.
- Live candidate analysis uses temporary working files rather than treating the sample analysis outputs as the uploaded candidate.
- Local development defaults to `http://localhost:5173` and `http://127.0.0.1:5173` as CORS origins.
- Production must set `CORS_ORIGINS` to exact frontend origins, comma-separated (for example, `https://your-app.vercel.app`). Do not use `*` with credentialed CORS.
- The frontend reads `VITE_API_URL`; set it to the deployed backend base URL in the Vercel project and redeploy.
- Recommended split deployment: FastAPI backend as a Python web service; Vite frontend on Vercel with root directory `frontend`, build command `npm run build`, and output directory `dist`.
- Verify the hosting provider request-body limit supports the application upload limit of 10 MB before accepting production uploads.

## Production build

From the project root:

```powershell
cd frontend
npm.cmd ci
npm.cmd run build
```

The generated frontend build is written to `frontend/dist/` and is excluded from Git.


## Production environment variables

Backend (`CORS_ORIGINS`): comma-separated exact browser origins, without trailing slashes. Example: `https://your-app.vercel.app`.

Frontend (`VITE_API_URL`): backend base URL, without an API path suffix. Example: `https://your-api-service.onrender.com`.
