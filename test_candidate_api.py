import io
import zipfile
import uuid

import pytest
from fastapi.testclient import TestClient

from backend.app import main


client = TestClient(main.app)


def make_docx_bytes():
    """Create a minimal DOCX container for upload-validation tests."""

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "word/document.xml",
            '<?xml version="1.0"?><document/>',
        )

    return buffer.getvalue()


def make_pdf_bytes():
    return b"%PDF-1.4\nTest PDF content"


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rejects_unsupported_resume_extension():
    response = client.post(
        "/api/candidates/analyze",
        files={
            "resume": ("resume.txt", b"Some text", "text/plain"),
        },
        data={"jd_text": "Must Have:\n- Python"},
    )

    assert response.status_code == 400
    assert "PDF or DOCX" in response.json()["detail"]


def test_rejects_empty_resume():
    response = client.post(
        "/api/candidates/analyze",
        files={
            "resume": ("resume.pdf", b"", "application/pdf"),
        },
        data={"jd_text": "Must Have:\n- Python"},
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_rejects_invalid_pdf_signature():
    response = client.post(
        "/api/candidates/analyze",
        files={
            "resume": (
                "resume.pdf",
                b"This is not a PDF",
                "application/pdf",
            ),
        },
        data={"jd_text": "Must Have:\n- Python"},
    )

    assert response.status_code == 400
    assert "valid PDF" in response.json()["detail"]


def test_rejects_invalid_docx_container():
    response = client.post(
        "/api/candidates/analyze",
        files={
            "resume": (
                "resume.docx",
                b"PK but not a valid zip archive",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        },
        data={"jd_text": "Must Have:\n- Python"},
    )

    assert response.status_code == 400
    assert "corrupted" in response.json()["detail"].lower()


def test_rejects_docx_without_word_document():
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("some-file.txt", "not a Word document")

    response = client.post(
        "/api/candidates/analyze",
        files={
            "resume": (
                "resume.docx",
                buffer.getvalue(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        },
        data={"jd_text": "Must Have:\n- Python"},
    )

    assert response.status_code == 400
    assert "valid DOCX" in response.json()["detail"]


def test_rejects_empty_job_description():
    response = client.post(
        "/api/candidates/analyze",
        files={
            "resume": (
                "resume.pdf",
                make_pdf_bytes(),
                "application/pdf",
            ),
        },
        data={"jd_text": "   "},
    )

    assert response.status_code == 400
    assert "Job description" in response.json()["detail"]


def test_rejects_job_description_over_limit():
    response = client.post(
        "/api/candidates/analyze",
        files={
            "resume": (
                "resume.pdf",
                make_pdf_bytes(),
                "application/pdf",
            ),
        },
        data={"jd_text": "A" * (main.MAX_JD_LENGTH + 1)},
    )

    assert response.status_code == 413
    assert "50,000" in response.json()["detail"]


def test_rejects_resume_over_size_limit():
    oversized_content = (
        b"%PDF-" + b"A" * main.MAX_RESUME_SIZE
    )

    response = client.post(
        "/api/candidates/analyze",
        files={
            "resume": (
                "resume.pdf",
                oversized_content,
                "application/pdf",
            ),
        },
        data={"jd_text": "Must Have:\n- Python"},
    )

    assert response.status_code == 413
    assert "10 MB" in response.json()["detail"]


def test_accepts_valid_docx_signature_and_container(monkeypatch):
    fake_analysis = {
        "jd_analysis": {
            "job_metadata": {"title": "Test role"},
        },
        "score": {
            "alignment": {"alignment_score": 50.0},
            "summary": {
                "total_requirements": 1,
                "matched": 1,
                "partial": 0,
                "missing": 0,
                "must_have_not_fully_matched": 0,
            },
            "category_scores": {},
            "critical_gaps": [],
            "experience_eligibility": {
                "eligibility_status": "unverified",
            },
            "requirements": [],
            "limitations": [],
        },
        "resume": {
            "review_warnings": [],
        },
    }

    monkeypatch.setattr(
        main.candidate_pipeline,
        "analyze_candidate",
        lambda resume_path, jd_text: fake_analysis,
    )

    response = client.post(
        "/api/candidates/analyze",
        files={
            "resume": (
                "resume.docx",
                make_docx_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        },
        data={"jd_text": "Must Have:\n- Python"},
    )

    assert response.status_code == 200

    run_id = response.json()["run_id"]
    assert str(uuid.UUID(run_id)) == run_id

    assert response.json()["alignment"]["alignment_score"] == 50.0

def test_cors_origins_default_to_local_vite(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    assert main.get_cors_origins() == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def test_cors_origins_read_comma_separated_production_origins(monkeypatch):
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://evidencefirst.vercel.app, https://preview.example.com/",
    )

    assert main.get_cors_origins() == [
        "https://evidencefirst.vercel.app",
        "https://preview.example.com",
    ]


def test_cors_origins_reject_wildcard(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "*")

    with pytest.raises(RuntimeError, match="explicit origins"):
        main.get_cors_origins()
