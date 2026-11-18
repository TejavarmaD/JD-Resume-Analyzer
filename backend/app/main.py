"""Read-only API adapter for the existing deterministic JD-resume engines.

This layer deliberately does not alter or reimplement the scoring/matching logic.
"""
from __future__ import annotations

import json
import sys
import uuid
import re
from pathlib import Path
from typing import Any
import logging
import os
import zipfile
from io import BytesIO

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from . import candidate_pipeline

logger = logging.getLogger(__name__)

MAX_RESUME_SIZE = 10 * 1024 * 1024
MAX_JD_LENGTH = 50_000

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "jd_results"

FILES = {
    "jd": "ai_engineer_jd_analysis.json",
    "tags": "ai_engineer_jd_skill_tags.json",
    "evidence": "ai_engineer_jd_docx_evidence_match.json",
    "score": "ai_engineer_jd_docx_match_score.json",
    "status": "ai_engineer_jd_docx_evidence_status.json",
    "eligibility": "experience_eligibility.json",
}

app = FastAPI(
    title="JD–Resume Analyzer API",
    version="0.1.0",
    description="Dashboard API over the existing deterministic analysis outputs.",
)
def get_cors_origins() -> list[str]:
    """Return exact allowed frontend origins from CORS_ORIGINS.

    Comma-separated origins are supported. Local Vite origins are the
    development default; production deployments must set this variable.
    """
    configured = os.getenv("CORS_ORIGINS", "")
    origins = [origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()]
    if not origins:
        origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
    if "*" in origins:
        raise RuntimeError("CORS_ORIGINS must contain explicit origins, not '*'.")
    return origins


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_json(key: str) -> dict[str, Any]:
    path = RESULTS / FILES[key]
    if not path.is_file():
        raise HTTPException(status_code=503, detail=f"Analysis output is missing: {path.name}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=500, detail=f"Could not read {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise HTTPException(status_code=500, detail=f"Invalid JSON object: {path.name}")
    return data


def index_records(data: dict[str, Any], id_key: str) -> dict[str, dict[str, Any]]:
    records = data.get("requirements", [])
    if not isinstance(records, list):
        return {}
    return {
        str(item.get(id_key)): item
        for item in records
        if isinstance(item, dict) and item.get(id_key)
    }


def build_dashboard() -> dict[str, Any]:
    jd = read_json("jd")
    score = read_json("score")
    status = read_json("status")
    tags = read_json("tags")
    evidence = read_json("evidence")

    score_records = index_records(score, "requirement_id")
    status_records = index_records(status, "requirement_id")
    tag_records = index_records(tags, "requirement_id")
    evidence_records = index_records(evidence, "requirement_id")

    requirements = []
    for jd_record in jd.get("requirements", []):
        if not isinstance(jd_record, dict):
            continue
        rid = jd_record.get("id")
        scored = score_records.get(rid, {})
        interpreted = status_records.get(rid, {})
        tagged = tag_records.get(rid, {})
        matched = evidence_records.get(rid, {})
        requirements.append({
            "id": rid,
            "requirement": jd_record.get("requirement"),
            "category": jd_record.get("category", "uncategorized"),
            "priority": jd_record.get("priority", "must_have"),
            "requirement_type": jd_record.get("requirement_type"),
            "weight": scored.get("weight", jd_record.get("base_weight")),
            "match_status": scored.get("status", matched.get("status", "missing")),
            "evidence_status": interpreted.get("evidence_status", "no_evidence_found"),
            "evidence_strength": scored.get("evidence_strength", matched.get("evidence_strength")),
            "status_reason": scored.get("status_reason", matched.get("status_reason", "")),
            "evidence": scored.get("evidence", matched.get("evidence", [])),
            "manual_evidence": scored.get("manual_evidence", matched.get("manual_evidence", [])),
            "evidence_sources": interpreted.get("evidence_sources", []),
            "supported_groups": interpreted.get("supported_groups", []),
            "unsupported_groups": interpreted.get("unsupported_groups", []),
            "skill_tags": tagged.get("skill_tags", {}),
            "critical_gap": scored.get("critical_gap", False),
        })

    return {
        "job": jd.get("job_metadata", {}),
        "jd_summary": jd.get("summary", {}),
        "alignment": score.get("alignment", {}),
        "summary": score.get("summary", {}),
        "category_scores": score.get("category_scores", {}),
        "critical_gaps": score.get("critical_gaps", []),
        "experience_eligibility": read_json("eligibility").get("assessment", {}),
        "evidence_summary": status.get("summary", {}),
        "requirements": requirements,
        "limitations": score.get("limitations", []),
        "policies": status.get("policy", []),
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "jd-resume-analyzer-api"}


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    return build_dashboard()


@app.get("/api/requirements")
def requirements(
    q: str | None = Query(default=None, description="Search requirement text or ID"),
    category: str | None = None,
    status: str | None = None,
    priority: str | None = None,
) -> dict[str, Any]:
    data = build_dashboard()
    rows = data["requirements"]
    if q:
        needle = q.casefold()
        rows = [r for r in rows if needle in str(r["id"]).casefold() or needle in str(r["requirement"]).casefold()]
    if category:
        rows = [r for r in rows if r["category"] == category]
    if status:
        rows = [r for r in rows if r["match_status"] == status]
    if priority:
        rows = [r for r in rows if r["priority"] == priority]
    return {"total": len(rows), "requirements": rows}


@app.get("/api/requirements/{requirement_id}")
def requirement_detail(requirement_id: str) -> dict[str, Any]:
    rows = build_dashboard()["requirements"]
    for row in rows:
        if row["id"] == requirement_id:
            return row
    raise HTTPException(status_code=404, detail="Requirement not found")

async def read_upload_with_limit(upload: UploadFile) -> bytes:
    """Read an uploaded file without allowing it to exceed the size limit."""

    chunks = []
    total_size = 0

    while True:
        chunk = await upload.read(1024 * 1024)

        if not chunk:
            break

        total_size += len(chunk)

        if total_size > MAX_RESUME_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Resume file must be 10 MB or smaller.",
            )

        chunks.append(chunk)

    return b"".join(chunks)


def validate_resume_file(content: bytes, suffix: str) -> None:
    """Validate the file signature and basic container structure."""

    if suffix == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise HTTPException(
                status_code=400,
                detail=(
                    "The uploaded file does not appear to be a valid PDF. "
                    "Please upload a readable PDF resume."
                ),
            )

    elif suffix == ".docx":
        if not content.startswith(b"PK"):
            raise HTTPException(
                status_code=400,
                detail=(
                    "The uploaded file does not appear to be a valid DOCX. "
                    "Please upload a valid Word document."
                ),
            )

        try:
            with zipfile.ZipFile(BytesIO(content)) as archive:
                if "word/document.xml" not in archive.namelist():
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "The uploaded file is not a valid DOCX document."
                        ),
                    )
        except zipfile.BadZipFile as exc:
            raise HTTPException(
                status_code=400,
                detail="The uploaded DOCX file is corrupted.",
            ) from exc


@app.post("/api/candidates/analyze")
async def analyze_candidate_upload(
    resume: UploadFile = File(...),
    jd_text: str = Form(...),
) -> dict[str, Any]:
    import tempfile

    try:
        filename = Path(resume.filename or "").name
        suffix = Path(filename).suffix.lower()

        if not filename:
            raise HTTPException(
                status_code=400,
                detail="Please select a resume file.",
            )

        if suffix not in {".pdf", ".docx"}:
            raise HTTPException(
                status_code=400,
                detail="Resume must be a PDF or DOCX file.",
            )

        if not isinstance(jd_text, str) or not jd_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Job description cannot be empty.",
            )

        if len(jd_text) > MAX_JD_LENGTH:
            raise HTTPException(
                status_code=413,
                detail="Job description must be 50,000 characters or fewer.",
            )

        content = await read_upload_with_limit(resume)

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded resume is empty.",
            )

        validate_resume_file(content, suffix)

        with tempfile.TemporaryDirectory() as temp_dir:
            resume_path = Path(temp_dir) / f"resume{suffix}"
            resume_path.write_bytes(content)

            normalized_jd_text = re.sub(
                r"\s+(Must Have|Good to Have)\s*:",
                r"\n\n\1:\n",
                jd_text,
                flags=re.IGNORECASE,
            )

            normalized_jd_text = re.sub(
                r"\s+-\s+",
                "\n- ",
                normalized_jd_text,
            )

            analysis = candidate_pipeline.analyze_candidate(
                resume_path,
                normalized_jd_text,
            )

            run_id = str(uuid.uuid4())

        return {
             "run_id": run_id,
            "job": analysis["jd_analysis"].get("job_metadata", {}),
            "alignment": analysis["score"].get("alignment", {}),
            "summary": analysis["score"].get("summary", {}),
            "category_scores": analysis["score"].get("category_scores", {}),
            "critical_gaps": analysis["score"].get("critical_gaps", []),
            "experience_eligibility": analysis["score"].get(
                "experience_eligibility", {}
            ),
            "requirements": analysis["score"].get("requirements", []),
            "resume_warnings": analysis["resume"].get("review_warnings", []),
            "limitations": analysis["score"].get("limitations", []),
        }

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Candidate analysis failed")

        raise HTTPException(
            status_code=500,
            detail=(
                "Candidate analysis failed unexpectedly. "
                "Please verify that the resume is readable and try again."
            ),
        ) from exc

    finally:
        await resume.close()