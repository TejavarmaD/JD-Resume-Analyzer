import json

import pytest

from backend.app import candidate_pipeline


def test_rejects_job_description_with_no_extracted_requirements(monkeypatch):
    monkeypatch.setattr(
        candidate_pipeline.jd_analyzer,
        "analyze_jd",
        lambda jd_text: {"requirements": [], "job_metadata": {}},
    )

    with pytest.raises(
        ValueError,
        match="No job requirements could be extracted",
    ):
        candidate_pipeline.analyze_candidate_jd(
            "This is a paragraph with no recognizable requirements."
        )


def test_candidate_runs_are_saved_in_separate_directories(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        candidate_pipeline,
        "PROJECT_ROOT",
        tmp_path,
    )

    resume_one = tmp_path / "candidate_one.pdf"
    resume_two = tmp_path / "candidate_two.pdf"

    resume_one.write_bytes(b"%PDF-1.4 candidate one")
    resume_two.write_bytes(b"%PDF-1.4 candidate two")

    analysis_one = {"candidate": "one", "score": 75}
    analysis_two = {"candidate": "two", "score": 25}

    saved_one = candidate_pipeline.save_candidate_run(
        resume_one,
        analysis_one,
    )

    saved_two = candidate_pipeline.save_candidate_run(
        resume_two,
        analysis_two,
    )

    assert saved_one["run_id"] != saved_two["run_id"]
    assert saved_one["run_directory"] != saved_two["run_directory"]

    with open(saved_one["analysis_file"], encoding="utf-8") as file:
        result_one = json.load(file)

    with open(saved_two["analysis_file"], encoding="utf-8") as file:
        result_two = json.load(file)

    assert result_one["candidate"] == "one"
    assert result_one["score"] == 75

    assert result_two["candidate"] == "two"
    assert result_two["score"] == 25

    assert (
        open(saved_one["resume_file"], "rb").read()
        == b"%PDF-1.4 candidate one"
    )

    assert (
        open(saved_two["resume_file"], "rb").read()
        == b"%PDF-1.4 candidate two"
    )